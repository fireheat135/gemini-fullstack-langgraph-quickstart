#!/usr/bin/env python3
"""
TDD自己回帰ループシステム - TestGenerationEngineのテスト

Red Phase: まず失敗するテストを書く
"""

import pytest
import ast
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

# Test対象のクラスをインポート
from src.testing.test_generation_engine import TestCase, Function


class TestTestGenerationEngine:
    """TestGenerationEngineのテスト群"""
    
    @pytest.fixture
    def sample_source_code(self):
        """テスト用のサンプルソースコード"""
        return '''
def calculate_seo_score(content: str, keywords: List[str]) -> float:
    """SEOスコアを計算する関数"""
    if not content or not keywords:
        return 0.0
    
    total_score = 0.0
    for keyword in keywords:
        count = content.lower().count(keyword.lower())
        density = count / len(content.split()) if content.split() else 0
        total_score += density * 100
    
    return min(total_score, 100.0)

def generate_meta_description(content: str, max_length: int = 160) -> str:
    """メタディスクリプションを生成する関数"""
    if not content:
        return ""
    
    sentences = content.split('。')
    description = ""
    
    for sentence in sentences:
        if len(description + sentence) <= max_length:
            description += sentence + "。"
        else:
            break
    
    return description.strip()
'''

    def test_generate_tests_基本機能(self, sample_source_code):
        """TestGenerationEngineがソースコードからテストケースを生成できること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        # Act
        test_cases = engine.generate_tests(sample_source_code)
        
        # Assert
        assert isinstance(test_cases, list)
        assert len(test_cases) > 0
        
        # 各テストケースが正しい構造を持つこと
        for test_case in test_cases:
            assert isinstance(test_case, TestCase)
            assert test_case.name
            assert test_case.function
            assert isinstance(test_case.inputs, dict)
            assert test_case.expected_behavior
            assert test_case.assertion_type in ['return_value', 'exception', 'side_effect']
    
    def test_generate_normal_cases_通常ケース生成(self, sample_source_code):
        """通常ケースのテスト生成が正しく動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        sample_function = Function(
            name="calculate_seo_score",
            parameters=[
                {"name": "content", "type": "str"},
                {"name": "keywords", "type": "List[str]"}
            ],
            return_type="float",
            docstring="SEOスコアを計算する関数"
        )
        
        # Act
        normal_cases = engine.generate_normal_cases(sample_function)
        
        # Assert
        assert len(normal_cases) >= 3  # 最低3つの通常ケース
        
        # SEO計算関数の通常ケースが含まれること
        function_names = [case.function for case in normal_cases]
        assert "calculate_seo_score" in function_names
        
        # 適切な入力パラメータが生成されること
        for case in normal_cases:
            if case.function == "calculate_seo_score":
                assert "content" in case.inputs
                assert "keywords" in case.inputs
                assert isinstance(case.inputs["content"], str)
                assert isinstance(case.inputs["keywords"], list)

    def test_generate_edge_cases_エッジケース生成(self):
        """エッジケースの自動生成が動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        sample_function = Function(
            name="generate_meta_description",
            parameters=[
                {"name": "content", "type": "str"},
                {"name": "max_length", "type": "int"}
            ],
            return_type="str",
            docstring="メタディスクリプションを生成する関数"
        )
        
        # Act
        edge_cases = engine.generate_edge_cases(sample_function)
        
        # Assert
        assert len(edge_cases) > 0
        
        # エッジケースの例が含まれること
        edge_inputs = [case.inputs for case in edge_cases]
        
        # 空文字列テスト
        assert any("" in case.get("content", "") for case in edge_inputs)
        
        # 境界値テスト（max_length）
        assert any(case.get("max_length") == 0 for case in edge_inputs)
        assert any(case.get("max_length") == 1 for case in edge_inputs)

    def test_generate_error_cases_エラーケース生成(self):
        """エラーケースの生成が正しく動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        sample_function = Function(
            name="calculate_seo_score",
            parameters=[
                {"name": "content", "type": "str"},
                {"name": "keywords", "type": "List[str]"}
            ],
            return_type="float",
            docstring="SEOスコアを計算する関数"
        )
        
        # Act
        error_cases = engine.generate_error_cases(sample_function)
        
        # Assert
        assert len(error_cases) > 0
        
        # None入力のテストが含まれること
        none_cases = [case for case in error_cases 
                     if None in case.inputs.values()]
        assert len(none_cases) > 0
        
        # 型エラーテストが含まれること
        type_error_cases = [case for case in error_cases
                           if case.assertion_type == "exception"]
        assert len(type_error_cases) > 0

    def test_analyze_code_complexity_複雑度分析(self, sample_source_code):
        """コードの複雑度分析が正しく動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        # Act
        complexity_analysis = engine.analyze_code_complexity(sample_source_code)
        
        # Assert
        assert isinstance(complexity_analysis, dict)
        assert "functions" in complexity_analysis
        assert "total_complexity" in complexity_analysis
        assert "average_complexity" in complexity_analysis
        
        # 関数ごとの複雑度が記録されること
        functions = complexity_analysis["functions"]
        assert "calculate_seo_score" in functions
        assert "generate_meta_description" in functions
        
        # 複雑度が適切な範囲であること
        for func_name, complexity in functions.items():
            assert isinstance(complexity, (int, float))
            assert complexity > 0

    def test_generate_parameter_combinations_パラメータ組み合わせ生成(self):
        """パラメータの組み合わせ生成が正しく動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        sample_function = Function(
            name="test_function",
            parameters=[
                {"name": "text", "type": "str"},
                {"name": "count", "type": "int"},
                {"name": "enabled", "type": "bool"}
            ],
            return_type=None,
            docstring="テスト用関数"
        )
        
        # Act
        combinations = engine.generate_parameter_combinations(sample_function)
        
        # Assert
        assert len(combinations) > 0
        
        # 各組み合わせが適切な型を持つこと
        for combo in combinations:
            assert isinstance(combo["text"], str)
            assert isinstance(combo["count"], int)
            assert isinstance(combo["enabled"], bool)

    def test_self_recursive_improvement_自己改善ループ(self, sample_source_code):
        """自己改善ループが動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        # Act & Assert - このテストは最初は失敗することを期待
        with pytest.raises(NotImplementedError):
            # 自己改善ループはまだ実装されていない
            engine.run_self_recursive_loop(
                source_code=sample_source_code,
                coverage_threshold=0.8,
                quality_threshold=90,
                max_iterations=3
            )

    def test_integration_with_coverage_monitor_カバレッジ監視統合(self):
        """CoverageMonitorとの統合が正しく動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        from src.testing.coverage_monitor import CoverageMonitor
        
        engine = TestGenerationEngine()
        monitor = CoverageMonitor(threshold=0.8)
        
        # Act & Assert - 統合テストは最初は失敗することを期待
        with pytest.raises(NotImplementedError):
            # 統合機能はまだ実装されていない
            result = engine.analyze_with_coverage(monitor, "sample_code")
            assert result is not None

    def test_ai_assisted_test_generation_AI支援テスト生成(self):
        """AI支援テスト生成が動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        # Mock AI service
        # AIサービスのモック（簡略化）
        mock_ai = MagicMock()
        mock_ai.return_value.generate_test_suggestions.return_value = [
            {
                "test_name": "test_seo_score_calculation",
                "inputs": {"content": "テスト記事", "keywords": ["SEO", "テスト"]},
                "expected": 75.0
            }
        ]
        
        with patch.object(engine, '_get_ai_service', return_value=mock_ai()):
            mock_ai.return_value.generate_test_suggestions.return_value = [
                {
                    "test_name": "test_seo_score_calculation",
                    "inputs": {"content": "テスト記事", "keywords": ["SEO", "テスト"]},
                    "expected": 75.0
                }
            ]
            
            # Act
            ai_tests = engine.generate_ai_assisted_tests("sample_function")
            
            # Assert
            assert len(ai_tests) > 0
            mock_ai.return_value.generate_test_suggestions.assert_called_once()

    def test_property_based_test_generation_プロパティベース生成(self):
        """プロパティベーステストの生成が動作すること"""
        # Arrange
        from src.testing.test_generation_engine import TestGenerationEngine
        engine = TestGenerationEngine()
        
        function_spec = {
            "name": "calculate_seo_score",
            "properties": [
                "結果は0.0以上100.0以下",
                "キーワードが多いほどスコアが高い",
                "空のコンテンツでは0.0を返す"
            ]
        }
        
        # Act & Assert - プロパティベース機能はまだ実装されていない
        with pytest.raises(NotImplementedError):
            property_tests = engine.generate_property_based_tests(function_spec)
            assert len(property_tests) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])