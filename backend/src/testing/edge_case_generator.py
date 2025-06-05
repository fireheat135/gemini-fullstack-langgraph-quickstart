"""
Edge Case Generator Module
エッジケースを生成
"""
from typing import List, Dict, Any


class EdgeCaseGenerator:
    """エッジケース生成クラス"""
    
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