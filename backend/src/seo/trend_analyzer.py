"""
Trend Analyzer
トレンド分析機能
"""
import asyncio
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta


class TrendAnalyzer:
    """トレンド分析クラス"""
    
    async def get_google_trends(self, keyword: str) -> Dict[str, Any]:
        """Google Trendsデータを取得（モック実装）"""
        # 実際の実装では pytrends ライブラリを使用
        
        # 過去12ヶ月のトレンドデータを生成
        interest_over_time = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * i)
            # 季節性を考慮したランダムなトレンド値
            base_value = 50
            
            # 誕生花関連の季節性
            if "誕生花" in keyword:
                # 春（3-5月）と冬（12月）は高め
                if date.month in [3, 4, 5, 12]:
                    base_value += 20
                elif date.month in [6, 7, 8]:
                    base_value += 10
            
            # 母の日関連
            if "母の日" in keyword and date.month == 5:
                base_value += 50
            
            # ランダムなばらつきを追加
            value = base_value + random.randint(-15, 15)
            interest_over_time.append({
                "date": date.strftime("%Y-%m"),
                "value": max(0, min(100, value))
            })
        
        # 関連クエリ
        related_queries = [
            f"{keyword} プレゼント",
            f"{keyword} 花言葉",
            f"{keyword} ギフト",
            f"{keyword} 意味",
            "花束 プレゼント"
        ]
        
        return {
            "keyword": keyword,
            "interest_over_time": interest_over_time,
            "related_queries": related_queries,
            "peak_value": max(item["value"] for item in interest_over_time),
            "average_interest": sum(item["value"] for item in interest_over_time) / len(interest_over_time)
        }
    
    async def analyze_seasonal_trends(self, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """季節性トレンドを分析"""
        seasonal_analysis = {}
        
        for keyword in keywords:
            trend_data = await self.get_google_trends(keyword)
            
            # 月別の平均値を計算
            monthly_averages = {}
            for item in trend_data["interest_over_time"]:
                month = int(item["date"].split("-")[1])
                if month not in monthly_averages:
                    monthly_averages[month] = []
                monthly_averages[month].append(item["value"])
            
            # 各月の平均を計算
            monthly_scores = {}
            for month, values in monthly_averages.items():
                monthly_scores[month] = sum(values) / len(values)
            
            # ピーク月を特定
            if monthly_scores:
                max_score = max(monthly_scores.values())
                peak_months = [month for month, score in monthly_scores.items() 
                              if score >= max_score * 0.8]
            else:
                peak_months = []
            
            # 季節性スコアを計算（標準偏差）
            if len(monthly_scores) > 1:
                avg_score = sum(monthly_scores.values()) / len(monthly_scores)
                variance = sum((score - avg_score) ** 2 for score in monthly_scores.values()) / len(monthly_scores)
                seasonality_score = variance ** 0.5
            else:
                seasonality_score = 0
            
            seasonal_analysis[keyword] = {
                "peak_months": peak_months,
                "seasonality_score": round(seasonality_score, 2),
                "monthly_scores": monthly_scores,
                "trend_pattern": self._identify_trend_pattern(monthly_scores)
            }
        
        return seasonal_analysis
    
    def _identify_trend_pattern(self, monthly_scores: Dict[int, float]) -> str:
        """トレンドパターンを識別"""
        if not monthly_scores:
            return "no_data"
        
        # 春にピークがある場合
        spring_months = [3, 4, 5]
        spring_avg = sum(monthly_scores.get(m, 0) for m in spring_months) / 3
        
        # 冬にピークがある場合
        winter_months = [12, 1, 2]
        winter_avg = sum(monthly_scores.get(m, 0) for m in winter_months) / 3
        
        # 夏にピークがある場合
        summer_months = [6, 7, 8]
        summer_avg = sum(monthly_scores.get(m, 0) for m in summer_months) / 3
        
        # 秋にピークがある場合
        autumn_months = [9, 10, 11]
        autumn_avg = sum(monthly_scores.get(m, 0) for m in autumn_months) / 3
        
        max_seasonal_avg = max(spring_avg, winter_avg, summer_avg, autumn_avg)
        
        if max_seasonal_avg == spring_avg:
            return "spring_peak"
        elif max_seasonal_avg == winter_avg:
            return "winter_peak"
        elif max_seasonal_avg == summer_avg:
            return "summer_peak"
        elif max_seasonal_avg == autumn_avg:
            return "autumn_peak"
        else:
            return "consistent"