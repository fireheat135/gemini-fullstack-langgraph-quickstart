"""
Test Generation Engine
自己回帰ループシステムの基盤実装
"""
import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import random


@dataclass
class TestCase:
    """テストケースを表すデータクラス"""
    name: str
    function: str
    inputs: Dict[str, Any]
    expected_behavior: str
    assertion_type: str
    category: str = "normal"  # normal, edge, error


@dataclass
class Function:
    """関数情報を表すデータクラス"""
    name: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int = 0


class CodeAnalyzer:
    """コードを解析してAST情報を抽出"""
    
    def parse(self, source_code: str) -> ast.Module:
        """ソースコードをパースしてASTを返す"""
        return ast.parse(source_code)
    
    def extract_functions(self, ast_tree: ast.Module) -> List[Function]:
        """ASTから関数情報を抽出"""
        functions = []
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                func = self._extract_function_info(node)
                functions.append(func)
        
        return functions
    
    def _extract_function_info(self, node: ast.FunctionDef) -> Function:
        """関数ノードから情報を抽出"""
        parameters = []
        
        for arg in node.args.args:
            param = {"name": arg.arg, "type": None}
            
            # 型アノテーションがある場合
            if arg.annotation:
                param["type"] = ast.unparse(arg.annotation)
            
            parameters.append(param)
        
        # 戻り値の型
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # docstring
        docstring = ast.get_docstring(node)
        
        return Function(
            name=node.name,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring
        )
    
    def calculate_complexity(self, source_code: str) -> int:
        """循環複雑度を計算（簡易版）"""
        tree = self.parse(source_code)
        complexity = 1  # 基本値
        
        for node in ast.walk(tree):
            # 分岐を数える
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):  # and, or
                complexity += len(node.values) - 1
        
        return complexity


class PatternDetector:
    """コードパターンを検出"""
    
    def detect(self, source_code: str) -> List[str]:
        """既知のパターンを検出"""
        patterns = []
        
        # シンプルなパターン検出
        if "_instance" in source_code and "__new__" in source_code:
            patterns.append("Singleton")
        
        if "@property" in source_code:
            patterns.append("Property")
        
        if "def __enter__" in source_code and "def __exit__" in source_code:
            patterns.append("ContextManager")
        
        return patterns


class EdgeCaseGenerator:
    """エッジケースを生成"""
    
    def generate(self, function: Function) -> List[TestCase]:
        """関数に対するエッジケースを生成"""
        edge_cases = []
        
        for param in function.parameters:
            param_cases = self._generate_parameter_edge_cases(param, function)
            edge_cases.extend(param_cases)
        
        return edge_cases
    
    def generate_for_parameter(self, param_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """パラメータに対するエッジケース値を生成"""
        edge_values = []
        param_type = param_info.get("type", "Any")
        
        if param_type == "int":
            edge_values.extend([
                {"value": 0, "description": "ゼロ"},
                {"value": -1, "description": "負の数"},
                {"value": 1, "description": "最小の正数"},
                {"value": 2**31 - 1, "description": "32bit最大値"},
                {"value": -2**31, "description": "32bit最小値"},
            ])
            
            # 制約がある場合
            if "constraints" in param_info:
                min_val = param_info["constraints"].get("min")
                max_val = param_info["constraints"].get("max")
                
                if min_val is not None:
                    edge_values.extend([
                        {"value": min_val, "description": "最小値"},
                        {"value": min_val - 1, "description": "最小値未満"},
                    ])
                
                if max_val is not None:
                    edge_values.extend([
                        {"value": max_val, "description": "最大値"},
                        {"value": max_val + 1, "description": "最大値超"},
                    ])
        
        elif param_type == "str":
            edge_values.extend([
                {"value": "", "description": "空文字列"},
                {"value": " ", "description": "空白文字"},
                {"value": "a", "description": "単一文字"},
                {"value": "a" * 1000, "description": "長い文字列"},
                {"value": "あ", "description": "日本語文字"},
                {"value": "🌸", "description": "絵文字"},
                {"value": "test\ntest", "description": "改行を含む"},
                {"value": "test'test", "description": "シングルクォート"},
                {"value": 'test"test', "description": "ダブルクォート"},
            ])
            
            # 長さ制約
            if "constraints" in param_info:
                min_len = param_info["constraints"].get("min_length")
                max_len = param_info["constraints"].get("max_length")
                
                if min_len is not None:
                    edge_values.append({
                        "value": "a" * min_len,
                        "description": f"最小長（{min_len}文字）"
                    })
                
                if max_len is not None:
                    edge_values.append({
                        "value": "a" * max_len,
                        "description": f"最大長（{max_len}文字）"
                    })
        
        elif "List" in param_type:
            edge_values.extend([
                {"value": [], "description": "空リスト"},
                {"value": [1], "description": "単一要素"},
                {"value": [1] * 1000, "description": "大量の要素"},
                {"value": [1, 1, 1], "description": "重複要素"},
                {"value": [1, None, 3], "description": "Noneを含む"},
            ])
        
        elif param_type == "float":
            edge_values.extend([
                {"value": 0.0, "description": "ゼロ"},
                {"value": -0.0, "description": "負のゼロ"},
                {"value": float('inf'), "description": "無限大"},
                {"value": float('-inf'), "description": "負の無限大"},
                {"value": float('nan'), "description": "NaN"},
                {"value": 1e-308, "description": "最小の正の値"},
                {"value": 1.7976931348623157e+308, "description": "最大の値"},
            ])
        
        return edge_values
    
    def _generate_parameter_edge_cases(self, param: Dict[str, Any], function: Function) -> List[TestCase]:
        """パラメータのエッジケースからテストケースを生成"""
        test_cases = []
        edge_values = self.generate_for_parameter(param)
        
        for edge_value in edge_values:
            # 他のパラメータはデフォルト値を使用
            inputs = {}
            for p in function.parameters:
                if p["name"] == param["name"]:
                    inputs[p["name"]] = edge_value["value"]
                else:
                    inputs[p["name"]] = self._get_default_value(p["type"])
            
            test_case = TestCase(
                name=f"test_{function.name}_edge_{param['name']}_{edge_value['description']}",
                function=function.name,
                inputs=inputs,
                expected_behavior=f"エッジケース: {edge_value['description']}",
                assertion_type="return_value",
                category="edge"
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def _get_default_value(self, param_type: Optional[str]) -> Any:
        """型のデフォルト値を返す"""
        if not param_type:
            return None
        
        type_defaults = {
            "int": 1,
            "float": 1.0,
            "str": "test",
            "bool": True,
            "List": [],
            "Dict": {},
        }
        
        for type_name, default in type_defaults.items():
            if type_name in param_type:
                return default
        
        return None


class TestGenerationEngine:
    """テスト生成エンジンのメインクラス"""
    
    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.pattern_detector = PatternDetector()
        self.edge_case_generator = EdgeCaseGenerator()
    
    def generate_tests(self, source_code: str) -> List[TestCase]:
        """ソースコードから自動的にテストケースを生成"""
        # コード解析
        ast_tree = self.code_analyzer.parse(source_code)
        functions = self.code_analyzer.extract_functions(ast_tree)
        
        test_cases = []
        for func in functions:
            # 通常ケース
            normal_cases = self.generate_normal_cases(func)
            test_cases.extend(normal_cases)
            
            # エッジケース
            edge_cases = self.edge_case_generator.generate(func)
            test_cases.extend(edge_cases)
            
            # エラーケース
            error_cases = self.generate_error_cases(func)
            test_cases.extend(error_cases)
        
        return test_cases
    
    def generate_normal_cases(self, function: Function) -> List[TestCase]:
        """関数の通常動作をテストするケースを生成"""
        cases = []
        
        # パラメータの組み合わせを生成
        param_combos = self.generate_parameter_combinations(function)
        
        for i, combo in enumerate(param_combos[:5]):  # 最大5つの通常ケース
            test_case = TestCase(
                name=f"test_{function.name}_normal_{i+1}",
                function=function.name,
                inputs=combo,
                expected_behavior="正常動作",
                assertion_type="return_value",
                category="normal"
            )
            cases.append(test_case)
        
        return cases
    
    def generate_parameter_combinations(self, function: Function) -> List[Dict[str, Any]]:
        """パラメータの組み合わせを生成"""
        combinations = []
        
        # 基本的な組み合わせを生成
        base_combo = {}
        for param in function.parameters:
            base_combo[param["name"]] = self._generate_normal_value(param["type"])
        
        combinations.append(base_combo)
        
        # バリエーションを追加
        for param in function.parameters:
            variant = base_combo.copy()
            variant[param["name"]] = self._generate_variant_value(param["type"])
            combinations.append(variant)
        
        return combinations
    
    def generate_error_cases(self, function: Function) -> List[TestCase]:
        """エラーケースを生成"""
        cases = []
        
        # 各パラメータにNoneを渡すテスト
        for param in function.parameters:
            inputs = {}
            for p in function.parameters:
                if p["name"] == param["name"]:
                    inputs[p["name"]] = None
                else:
                    inputs[p["name"]] = self._generate_normal_value(p["type"])
            
            test_case = TestCase(
                name=f"test_{function.name}_none_{param['name']}",
                function=function.name,
                inputs=inputs,
                expected_behavior="Handle None input gracefully",
                assertion_type="exception",
                category="error"
            )
            cases.append(test_case)
        
        # 型エラーテスト
        for param in function.parameters:
            if param["type"] in ["int", "float", "str", "List[str]"]:
                inputs = {}
                for p in function.parameters:
                    if p["name"] == param["name"]:
                        # 間違った型を渡す
                        inputs[p["name"]] = 123 if param["type"] == "str" else "wrong_type"
                    else:
                        inputs[p["name"]] = self._generate_normal_value(p["type"])
                
                test_case = TestCase(
                    name=f"test_{function.name}_type_error_{param['name']}",
                    function=function.name,
                    inputs=inputs,
                    expected_behavior="Handle type error gracefully",
                    assertion_type="exception",
                    category="error"
                )
                cases.append(test_case)
        
        # 除算関数の場合、ゼロ除算をチェック
        if "divide" in function.name.lower():
            for param in function.parameters:
                if param["type"] in ["float", "int"]:
                    inputs = {}
                    for p in function.parameters:
                        if p["name"] == param["name"] and "divisor" in p["name"].lower() or p["name"] == "b" or p["name"] == "y":
                            inputs[p["name"]] = 0
                        else:
                            inputs[p["name"]] = 1
                    
                    test_case = TestCase(
                        name=f"test_{function.name}_zero_division",
                        function=function.name,
                        inputs=inputs,
                        expected_behavior="ValueError: Division by zero",
                        assertion_type="exception",
                        category="error"
                    )
                    cases.append(test_case)
                    break
        
        return cases
    
    def _generate_normal_value(self, param_type: Optional[str]) -> Any:
        """正常な値を生成"""
        if not param_type:
            return "test"
        
        # 具体的な型から順番にチェック（より具体的な型を優先）
        if param_type == "List[str]":
            return [f"keyword_{i}" for i in range(3)]
        elif param_type == "List[int]":
            return [random.randint(1, 10) for _ in range(3)]
        elif "List[str]" in param_type:
            return [f"keyword_{i}" for i in range(3)]
        elif "List[int]" in param_type:
            return [random.randint(1, 10) for _ in range(3)]
        elif "List" in param_type:
            return [f"item_{i}" for i in range(3)]
        elif param_type == "int":
            return random.randint(1, 100)
        elif param_type == "float":
            return round(random.uniform(1.0, 100.0), 2)
        elif param_type == "str":
            return f"test_{random.randint(1, 100)}"
        elif param_type == "bool":
            return random.choice([True, False])
        elif "Dict" in param_type:
            return {"key": "value", "number": 42}
        else:
            return "default"
    
    def _generate_variant_value(self, param_type: Optional[str]) -> Any:
        """バリエーション値を生成"""
        if not param_type:
            return "variant"
        
        # 具体的な型から順番にチェック（より具体的な型を優先）
        if param_type == "List[str]":
            return [f"variant_{i}" for i in range(5)]
        elif param_type == "List[int]":
            return [random.randint(11, 20) for _ in range(5)]
        elif "List[str]" in param_type:
            return [f"variant_{i}" for i in range(5)]
        elif "List[int]" in param_type:
            return [random.randint(11, 20) for _ in range(5)]
        elif "List" in param_type:
            return [f"variant_{i}" for i in range(5)]
        elif param_type == "int":
            return random.randint(101, 200)
        elif param_type == "float":
            return round(random.uniform(101.0, 200.0), 2)
        elif param_type == "str":
            return f"variant_{random.randint(1, 100)}"
        elif param_type == "bool":
            return True
        elif "Dict" in param_type:
            return {"variant": "data", "count": 100}
        else:
            return "variant"
    
    def analyze_code_complexity(self, source_code: str) -> Dict[str, Any]:
        """コードの複雑度分析を実行"""
        ast_tree = self.code_analyzer.parse(source_code)
        functions = self.code_analyzer.extract_functions(ast_tree)
        
        analysis = {
            "functions": {},
            "total_complexity": 0,
            "average_complexity": 0
        }
        
        total = 0
        for func in functions:
            complexity = self.code_analyzer.calculate_complexity(f"""
def {func.name}({', '.join(p['name'] for p in func.parameters)}):
    pass
""")
            analysis["functions"][func.name] = complexity
            total += complexity
        
        analysis["total_complexity"] = total
        analysis["average_complexity"] = total / len(functions) if functions else 0
        
        return analysis
    
    def generate_edge_cases(self, function: Function) -> List[TestCase]:
        """エッジケース生成（EdgeCaseGeneratorへの委譲）"""
        return self.edge_case_generator.generate(function)
    
    def run_self_recursive_loop(self, source_code: str, coverage_threshold: float, 
                               quality_threshold: int, max_iterations: int) -> Dict[str, Any]:
        """自己改善ループの実行（まだ実装されていない）"""
        raise NotImplementedError("自己改善ループはまだ実装されていません")
    
    def analyze_with_coverage(self, monitor, source_code: str) -> Dict[str, Any]:
        """CoverageMonitorとの統合分析（まだ実装されていない）"""
        raise NotImplementedError("カバレッジ統合分析はまだ実装されていません")
    
    def generate_ai_assisted_tests(self, function_name: str) -> List[TestCase]:
        """AI支援テスト生成（モック実装）"""
        # AIサービスを取得して呼び出し
        ai_service = self._get_ai_service()
        
        # AI サービスからテスト提案を取得
        ai_suggestions = ai_service.generate_test_suggestions(function_name)
        
        # AI提案をTestCaseオブジェクトに変換
        test_cases = []
        for suggestion in ai_suggestions:
            test_case = TestCase(
                name=suggestion.get("test_name", f"test_{function_name}_ai_generated"),
                function=function_name,
                inputs=suggestion.get("inputs", {"content": "テスト記事", "keywords": ["SEO", "テスト"]}),
                expected_behavior=f"Expected: {suggestion.get('expected', 'AI generated result')}",
                assertion_type="return_value",
                category="ai_generated"
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def generate_property_based_tests(self, function_spec: Dict[str, Any]) -> List[TestCase]:
        """プロパティベーステスト生成（まだ実装されていない）"""
        raise NotImplementedError("プロパティベーステスト生成はまだ実装されていません")
    
    def _get_ai_service(self):
        """AI サービスの取得（モック用）"""
        # 実際の実装では AIServiceManager を使用
        from unittest.mock import MagicMock
        return MagicMock()