"""
Code Analyzer Module
コードの複雑度や構造を分析
"""
import ast
from typing import Any


class CodeAnalyzer:
    """コード分析クラス"""
    
    def parse(self, source_code: str) -> ast.Module:
        """ソースコードをパース"""
        return ast.parse(source_code)
    
    def calculate_complexity(self, source_code: str) -> int:
        """循環複雑度を計算"""
        tree = self.parse(source_code)
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity