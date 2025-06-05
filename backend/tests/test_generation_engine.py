"""
TDD: Test Generation Engine Tests
自己回帰ループシステムの基盤テスト
"""
import pytest
import ast
from typing import List
from unittest.mock import Mock, MagicMock


# Red Phase: まず失敗するテストを書く
class TestGenerationEngine:
    """テスト生成エンジンのテストクラス"""

    def test_parse_source_code(self):
        """ソースコードのパースが正しく動作することを確認"""
        # Arrange
        source_code = """
def add(a: int, b: int) -> int:
    '''2つの数値を加算する'''
    return a + b
        """
        
        # Act - TestGenerationEngineがまだ存在しないので失敗する
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        ast_tree = engine.code_analyzer.parse(source_code)
        
        # Assert
        assert ast_tree is not None
        assert isinstance(ast_tree, ast.Module)

    def test_extract_functions_from_ast(self):
        """ASTから関数を抽出できることを確認"""
        # Arrange
        source_code = """
def greet(name: str) -> str:
    return f"Hello, {name}!"

def calculate_price(amount: float, tax_rate: float = 0.1) -> float:
    return amount * (1 + tax_rate)
        """
        
        # Act
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        ast_tree = engine.code_analyzer.parse(source_code)
        functions = engine.code_analyzer.extract_functions(ast_tree)
        
        # Assert
        assert len(functions) == 2
        assert functions[0].name == "greet"
        assert functions[1].name == "calculate_price"

    def test_generate_normal_test_cases(self):
        """通常のテストケースが生成されることを確認"""
        # Arrange
        function_info = Mock(
            name="multiply",
            parameters=[
                {"name": "x", "type": "int"},
                {"name": "y", "type": "int"}
            ],
            return_type="int"
        )
        
        # Act
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        test_cases = engine.generate_normal_cases(function_info)
        
        # Assert
        assert len(test_cases) > 0
        assert all(tc.function == "multiply" for tc in test_cases)
        assert all(tc.assertion_type == "return_value" for tc in test_cases)

    def test_generate_edge_cases(self):
        """エッジケースが生成されることを確認"""
        # Arrange
        function_info = Mock(
            name="divide",
            parameters=[
                {"name": "a", "type": "float"},
                {"name": "b", "type": "float"}
            ],
            return_type="float"
        )
        
        # Act
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        edge_cases = engine.edge_case_generator.generate(function_info)
        
        # Assert
        assert len(edge_cases) > 0
        # ゼロ除算のケースが含まれているか
        assert any(tc.inputs.get("b") == 0 for tc in edge_cases)
        # 負の数のケースが含まれているか
        assert any(tc.inputs.get("a") < 0 or tc.inputs.get("b") < 0 for tc in edge_cases)

    def test_generate_tests_for_complete_module(self):
        """完全なモジュールに対してテストが生成されることを確認"""
        # Arrange
        source_code = """
class Calculator:
    def add(self, x: int, y: int) -> int:
        return x + y
    
    def subtract(self, x: int, y: int) -> int:
        return x - y
    
    def multiply(self, x: int, y: int) -> int:
        return x * y
    
    def divide(self, x: float, y: float) -> float:
        if y == 0:
            raise ValueError("Division by zero")
        return x / y
        """
        
        # Act
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        test_cases = engine.generate_tests(source_code)
        
        # Assert
        assert len(test_cases) > 12  # 各メソッドに最低3つのテスト
        # 各メソッドのテストが含まれているか
        method_names = ["add", "subtract", "multiply", "divide"]
        for method in method_names:
            method_tests = [tc for tc in test_cases if method in tc.name]
            assert len(method_tests) >= 3

    @pytest.mark.parametrize("source_type,expected_min_tests", [
        ("function", 3),
        ("class", 10),
        ("module", 20),
    ])
    def test_test_generation_scales_with_complexity(self, source_type, expected_min_tests):
        """コードの複雑さに応じてテスト数が増加することを確認"""
        # Arrange
        source_codes = {
            "function": "def simple_func(x: int) -> int: return x * 2",
            "class": """
class SimpleClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
            """,
            "module": """
def func1(): pass
def func2(): pass
class Class1:
    def method1(self): pass
    def method2(self): pass
class Class2:
    def method1(self): pass
    def method2(self): pass
            """
        }
        
        # Act
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        test_cases = engine.generate_tests(source_codes[source_type])
        
        # Assert
        assert len(test_cases) >= expected_min_tests


class TestCodeAnalyzer:
    """コード解析機能のテスト"""

    def test_analyze_function_complexity(self):
        """関数の複雑度を正しく解析できることを確認"""
        # Arrange
        complex_function = """
def process_data(data: List[dict], filter_key: str, threshold: int) -> List[dict]:
    result = []
    for item in data:
        if filter_key in item:
            value = item[filter_key]
            if isinstance(value, int):
                if value > threshold:
                    result.append(item)
            elif isinstance(value, str):
                if len(value) > threshold:
                    result.append(item)
    return result
        """
        
        # Act
        from src.testing.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        complexity = analyzer.calculate_complexity(complex_function)
        
        # Assert
        assert complexity > 5  # 高い循環複雑度
        
    def test_detect_patterns_in_code(self):
        """コードパターンを検出できることを確認"""
        # Arrange
        code_with_patterns = """
# Singleton pattern
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        pass
        """
        
        # Act
        from src.testing.pattern_detector import PatternDetector
        detector = PatternDetector()
        patterns = detector.detect(code_with_patterns)
        
        # Assert
        assert "singleton" in [p.lower() for p in patterns]


class TestEdgeCaseGenerator:
    """エッジケース生成機能のテスト"""

    def test_generate_numeric_edge_cases(self):
        """数値型のエッジケースが生成されることを確認"""
        # Arrange
        param_info = {"name": "age", "type": "int", "constraints": {"min": 0, "max": 150}}
        
        # Act
        from src.testing.edge_case_generator import EdgeCaseGenerator
        generator = EdgeCaseGenerator()
        edge_cases = generator.generate_for_parameter(param_info)
        
        # Assert
        edge_values = [case["value"] for case in edge_cases]
        assert 0 in edge_values  # 最小値
        assert 150 in edge_values  # 最大値
        assert -1 in edge_values  # 境界外（下限）
        assert 151 in edge_values  # 境界外（上限）

    def test_generate_string_edge_cases(self):
        """文字列型のエッジケースが生成されることを確認"""
        # Arrange
        param_info = {"name": "username", "type": "str", "constraints": {"min_length": 3, "max_length": 20}}
        
        # Act
        from src.testing.edge_case_generator import EdgeCaseGenerator
        generator = EdgeCaseGenerator()
        edge_cases = generator.generate_for_parameter(param_info)
        
        # Assert
        edge_values = [case["value"] for case in edge_cases]
        # 空文字列
        assert "" in edge_values
        # 最小長
        assert any(len(v) == 3 for v in edge_values if isinstance(v, str))
        # 最大長
        assert any(len(v) == 20 for v in edge_values if isinstance(v, str))
        # 特殊文字
        assert any("'" in v or '"' in v or "\n" in v for v in edge_values if isinstance(v, str))

    def test_generate_collection_edge_cases(self):
        """コレクション型のエッジケースが生成されることを確認"""
        # Arrange
        param_info = {"name": "items", "type": "List[int]"}
        
        # Act
        from src.testing.edge_case_generator import EdgeCaseGenerator
        generator = EdgeCaseGenerator()
        edge_cases = generator.generate_for_parameter(param_info)
        
        # Assert
        edge_values = [case["value"] for case in edge_cases]
        # 空リスト
        assert [] in edge_values
        # 単一要素
        assert any(len(v) == 1 for v in edge_values if isinstance(v, list))
        # 大量の要素
        assert any(len(v) > 100 for v in edge_values if isinstance(v, list))
        # 重複要素
        assert any(len(set(v)) < len(v) for v in edge_values if isinstance(v, list) and len(v) > 1)