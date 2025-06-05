"""
Keyword Research Workflow
キーワードリサーチワークフロー
"""
import asyncio
from typing import Dict, Any, List
from .keyword_analyzer import KeywordAnalyzer
from .trend_analyzer import TrendAnalyzer
from .competitor_analyzer import CompetitorAnalyzer
from .data_sources import GoogleSuggestAPI, RakkoStyleKeywordExtractor


class KeywordResearchWorkflow:
    """キーワードリサーチの統合ワークフロー"""
    
    def __init__(self):
        self.keyword_analyzer = KeywordAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.suggest_api = GoogleSuggestAPI()
        self.rakko_extractor = RakkoStyleKeywordExtractor()
    
    async def conduct_full_research(self, article_topic: Dict[str, Any]) -> Dict[str, Any]:
        """完全なキーワードリサーチを実行"""
        
        primary_keyword = article_topic["primary_keyword"]
        month = article_topic.get("month")
        target_audience = article_topic.get("target_audience", "一般")
        
        # 並行してデータを取得
        tasks = [
            self._primary_keyword_analysis(primary_keyword),
            self._related_keyword_research(primary_keyword),
            self._trend_analysis(primary_keyword),
            self._competitor_research(primary_keyword),
            self._difficulty_analysis(primary_keyword)
        ]
        
        if month:
            tasks.append(self._month_specific_analysis(month, primary_keyword))
        
        results = await asyncio.gather(*tasks)
        
        # 結果を統合
        research_result = {
            "primary_analysis": results[0],
            "related_keywords": results[1],
            "trend_analysis": results[2],
            "competitor_analysis": results[3],
            "difficulty_scores": results[4],
            "content_opportunities": await self._identify_content_opportunities(results),
            "target_audience": target_audience
        }
        
        if month:
            research_result["month_specific_analysis"] = results[5]
        
        return research_result
    
    async def _primary_keyword_analysis(self, keyword: str) -> Dict[str, Any]:
        """主要キーワードの分析"""
        volume_data = await self.keyword_analyzer.get_search_volume(keyword)
        
        return {
            "keyword": keyword,
            "search_volume": volume_data,
            "keyword_type": self._classify_keyword_type(keyword),
            "search_intent": self._analyze_search_intent(keyword)
        }
    
    async def _related_keyword_research(self, primary_keyword: str) -> List[str]:
        """関連キーワードリサーチ"""
        # 複数ソースから関連キーワードを取得
        tasks = [
            self.keyword_analyzer.get_related_keywords(primary_keyword),
            self.suggest_api.get_suggestions(primary_keyword),
            self.rakko_extractor.extract_keywords(primary_keyword)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 結果を統合
        all_keywords = []
        all_keywords.extend(results[0])  # keyword_analyzer
        all_keywords.extend(results[1])  # suggest_api
        
        # rakko_extractor結果の統合
        rakko_data = results[2]
        all_keywords.extend(rakko_data["suggest_keywords"])
        all_keywords.extend(rakko_data["related_keywords"])
        all_keywords.extend(rakko_data["qa_keywords"])
        
        # 重複削除と優先度付け
        unique_keywords = list(set(all_keywords))
        
        # 誕生花関連の優先度付け
        prioritized_keywords = []
        high_priority_terms = ["花言葉", "プレゼント", "ギフト", "意味"]
        
        for keyword in unique_keywords:
            if any(term in keyword for term in high_priority_terms):
                prioritized_keywords.insert(0, keyword)
            else:
                prioritized_keywords.append(keyword)
        
        return prioritized_keywords[:50]  # 上位50個
    
    async def _trend_analysis(self, keyword: str) -> Dict[str, Any]:
        """トレンド分析"""
        trend_data = await self.trend_analyzer.get_google_trends(keyword)
        
        # 関連キーワードのトレンドも分析
        related_keywords = [
            f"{keyword} プレゼント",
            f"{keyword} 花言葉",
            f"{keyword} ギフト"
        ]
        
        seasonal_analysis = await self.trend_analyzer.analyze_seasonal_trends(related_keywords)
        
        return {
            "main_trend": trend_data,
            "seasonal_analysis": seasonal_analysis,
            "trend_summary": self._summarize_trends(trend_data, seasonal_analysis)
        }
    
    async def _competitor_research(self, keyword: str) -> Dict[str, Any]:
        """競合リサーチ"""
        # 競合URLを自動で生成（実際にはGoogle検索APIで取得）
        competitor_urls = [
            "https://example-flower1.com",
            "https://example-flower2.com",
            "https://example-flower3.com"
        ]
        
        tasks = [
            self.competitor_analyzer.analyze_competitor_keywords(competitor_urls),
            self.competitor_analyzer.analyze_competitor_content_structure(competitor_urls)
        ]
        
        keywords_analysis, content_analysis = await asyncio.gather(*tasks)
        
        gap_analysis = await self.competitor_analyzer.generate_content_gap_analysis(content_analysis)
        
        return {
            "competitor_keywords": keywords_analysis,
            "content_structure": content_analysis,
            "gap_analysis": gap_analysis
        }
    
    async def _difficulty_analysis(self, primary_keyword: str) -> Dict[str, float]:
        """難易度分析"""
        # 主要キーワードとその関連キーワードの難易度を分析
        keywords_to_analyze = [
            primary_keyword,
            f"{primary_keyword} 花言葉",
            f"{primary_keyword} プレゼント",
            f"{primary_keyword} 意味",
            f"{primary_keyword} ギフト"
        ]
        
        return await self.keyword_analyzer.analyze_difficulty(keywords_to_analyze)
    
    async def _month_specific_analysis(self, month: int, base_keyword: str) -> Dict[str, Any]:
        """月別特化分析"""
        month_analysis = await self.keyword_analyzer.analyze_birth_flower_keywords(month, base_keyword)
        
        # その月の花の詳細分析
        flowers = month_analysis["birth_flowers"]
        flower_analysis = {}
        
        for flower in flowers:
            flower_keywords = [
                f"{flower} 花言葉",
                f"{flower} プレゼント",
                f"{flower} 意味"
            ]
            flower_difficulty = await self.keyword_analyzer.analyze_difficulty(flower_keywords)
            flower_analysis[flower] = {
                "keywords": flower_keywords,
                "difficulty": flower_difficulty
            }
        
        month_analysis["flower_detailed_analysis"] = flower_analysis
        return month_analysis
    
    async def _identify_content_opportunities(self, research_results: List[Any]) -> List[Dict[str, Any]]:
        """コンテンツ機会を特定"""
        opportunities = []
        
        # 低競合・高ボリュームキーワードの特定
        if len(research_results) >= 5:
            difficulty_scores = research_results[4]
            
            for keyword, difficulty in difficulty_scores.items():
                if difficulty < 40:  # 低競合
                    opportunities.append({
                        "type": "low_competition",
                        "keyword": keyword,
                        "difficulty": difficulty,
                        "description": f"競合が少ないキーワード: {keyword}"
                    })
        
        # 季節性のあるコンテンツ機会
        if len(research_results) >= 3:
            trend_analysis = research_results[2]
            seasonal_data = trend_analysis.get("seasonal_analysis", {})
            
            for keyword, data in seasonal_data.items():
                if data["seasonality_score"] > 10:
                    opportunities.append({
                        "type": "seasonal",
                        "keyword": keyword,
                        "peak_months": data["peak_months"],
                        "description": f"季節性のあるキーワード: {keyword}"
                    })
        
        # コンテンツギャップ機会
        if len(research_results) >= 4:
            competitor_analysis = research_results[3]
            gap_analysis = competitor_analysis.get("gap_analysis", {})
            
            for gap in gap_analysis.get("content_gaps", []):
                opportunities.append({
                    "type": "content_gap",
                    "gap": gap,
                    "description": f"競合が対応していない分野: {gap}"
                })
        
        return opportunities
    
    def _classify_keyword_type(self, keyword: str) -> str:
        """キーワードタイプを分類"""
        if any(word in keyword for word in ["プレゼント", "ギフト", "買う", "購入"]):
            return "commercial"
        elif any(word in keyword for word in ["花言葉", "意味", "とは", "種類"]):
            return "informational"
        elif any(word in keyword for word in ["おすすめ", "人気", "ランキング", "比較"]):
            return "navigational"
        else:
            return "informational"
    
    def _analyze_search_intent(self, keyword: str) -> str:
        """検索意図を分析"""
        commercial_signals = ["プレゼント", "ギフト", "購入", "通販", "価格"]
        informational_signals = ["花言葉", "意味", "とは", "について", "種類"]
        
        if any(signal in keyword for signal in commercial_signals):
            return "商用"
        elif any(signal in keyword for signal in informational_signals):
            return "情報収集"
        else:
            return "一般"
    
    def _summarize_trends(self, trend_data: Dict[str, Any], seasonal_data: Dict[str, Any]) -> Dict[str, Any]:
        """トレンドをサマライズ"""
        summary = {
            "overall_trend": "安定" if trend_data["average_interest"] > 40 else "低調",
            "peak_period": None,
            "recommended_timing": [],
            "seasonal_patterns": []
        }
        
        # ピーク期間の特定
        max_interest = max(item["value"] for item in trend_data["interest_over_time"])
        for item in trend_data["interest_over_time"]:
            if item["value"] >= max_interest * 0.8:
                summary["recommended_timing"].append(item["date"])
        
        # 季節パターンの要約
        for keyword, data in seasonal_data.items():
            if data["seasonality_score"] > 10:
                summary["seasonal_patterns"].append({
                    "keyword": keyword,
                    "pattern": data["trend_pattern"],
                    "peak_months": data["peak_months"]
                })
        
        return summary