"""
Pattern Detector Module
コードパターンを検出
"""
from typing import List


class PatternDetector:
    """コードパターン検出クラス"""
    
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
        
        if "def __iter__" in source_code:
            patterns.append("Iterator")
        
        if "@classmethod" in source_code:
            patterns.append("ClassMethod")
        
        if "@staticmethod" in source_code:
            patterns.append("StaticMethod")
        
        return patterns