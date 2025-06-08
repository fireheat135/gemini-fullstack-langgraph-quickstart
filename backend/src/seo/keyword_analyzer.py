"""
Keyword Analyzer
キーワード分析・共起語分析機能
"""
import asyncio
import re
from typing import List, Dict, Any, Optional
from collections import Counter
import math
import aiohttp
from urllib.parse import quote
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class KeywordAnalyzer:
    """キーワード分析クラス"""
    
    def __init__(self, ai_service_manager=None):
        self.session = None
        self.ai_service_manager = ai_service_manager
        # 誕生花の月別データ
        self.birth_flowers_by_month = {
            1: ["スイートピー", "カーネーション"],
            2: ["フリージア", "スノードロップ"],
            3: ["チューリップ", "スイートアリッサム"],
            4: ["かすみ草", "アルストロメリア"],
            5: ["スズラン", "カーネーション"],
            6: ["バラ", "アジサイ"],
            7: ["ユリ", "ヒマワリ"],
            8: ["ヒマワリ", "トルコギキョウ"],
            9: ["リンドウ", "ダリア"],
            10: ["ガーベラ", "コスモス"],
            11: ["シクラメン", "ブバルディア"],
            12: ["ポインセチア", "カトレア"]
        }
    
    async def get_related_keywords(self, primary_keyword: str) -> List[str]:
        """関連キーワードを取得"""
        related_keywords = []
        
        # 基本的な関連キーワードを生成
        base_keywords = [
            f"{primary_keyword} 花言葉",
            f"{primary_keyword} 意味",
            f"{primary_keyword} プレゼント",
            f"{primary_keyword} ギフト",
            f"{primary_keyword} 育て方",
            f"{primary_keyword} 種類"
        ]
        related_keywords.extend(base_keywords)
        
        # 月が指定されている場合、その月の誕生花を追加
        month_match = re.search(r'(\d+)月', primary_keyword)
        if month_match:
            month = int(month_match.group(1))
            if month in self.birth_flowers_by_month:
                flowers = self.birth_flowers_by_month[month]
                for flower in flowers:
                    related_keywords.extend([
                        f"{flower} 花言葉",
                        f"{flower} 誕生花",
                        f"{flower} プレゼント",
                        f"{month}月 {flower}",
                    ])
        
        # 誕生花関連の一般的なキーワード
        general_keywords = [
            "花言葉 一覧",
            "誕生花 ギフト",
            "誕生花 プレゼント",
            "花束 プレゼント",
            "フラワーギフト",
            "花 意味",
            "花 プレゼント"
        ]
        related_keywords.extend(general_keywords)
        
        return list(set(related_keywords))  # 重複削除
    
    async def analyze_difficulty(self, keywords: List[str]) -> Dict[str, float]:
        """キーワード難易度を分析（簡易版）"""
        difficulty_scores = {}
        
        for keyword in keywords:
            # 簡易的な難易度計算
            score = 50.0  # 基本スコア
            
            # 文字数による調整
            if len(keyword) > 10:
                score -= 10  # 長いキーワードは競合が少ない傾向
            
            # 特定の単語による調整
            competitive_words = ["プレゼント", "ギフト", "人気", "ランキング"]
            for word in competitive_words:
                if word in keyword:
                    score += 15  # 競合が多そうなキーワード
            
            # 専門的な単語による調整
            specialized_words = ["花言葉", "育て方", "種類"]
            for word in specialized_words:
                if word in keyword:
                    score -= 5  # 少し競合が少ない
            
            # 月指定による調整
            if re.search(r'\d+月', keyword):
                score -= 10  # 月指定は具体的で競合が少ない
            
            # 0-100の範囲に調整
            score = max(0, min(100, score))
            difficulty_scores[keyword] = score
        
        return difficulty_scores
    
    async def get_search_volume(self, keyword: str) -> Dict[str, Any]:
        """検索ボリュームデータを取得（モック実装）"""
        # 実際の実装では Google Ads API や SEMrush API を使用
        # ここでは簡易的なモック
        
        # キーワードの長さと種類から推定ボリュームを計算
        base_volume = 1000
        
        # 一般的なキーワードはボリュームが高い
        if "誕生花" in keyword:
            base_volume *= 5
        if "プレゼント" in keyword:
            base_volume *= 3
        if "花言葉" in keyword:
            base_volume *= 2
        
        # 具体的な月指定はボリュームが下がる
        if re.search(r'\d+月', keyword):
            base_volume = int(base_volume * 0.3)
        
        # 花の種類が具体的だとボリュームが下がる
        flower_names = ["チューリップ", "バラ", "スズラン", "ヒマワリ"]
        for flower in flower_names:
            if flower in keyword:
                base_volume = int(base_volume * 0.5)
                break
        
        return {
            "monthly_searches": base_volume,
            "competition": "MEDIUM",
            "trend_data": [
                {"month": i, "searches": base_volume + (i * 100)}
                for i in range(1, 13)
            ]
        }
    
    def analyze_co_occurrence(self, content: str, target_keyword: str) -> List[Dict[str, Any]]:
        """共起語分析"""
        # より適切な単語分割
        # 句読点で文を分割してから単語を抽出
        sentences = re.split(r'[。！？\n]', content)
        all_words = []
        target_positions = []
        
        word_index = 0
        for sentence in sentences:
            # より細かく単語を分割
            # 助詞や句読点で分割してより正確な単語を抽出
            parts = re.split(r'[はがをにのでと、。！？]', sentence)
            
            for part in parts:
                # 各部分から日本語の単語を抽出
                words_in_part = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', part)
                
                for word in words_in_part:
                    if len(word) >= 2:  # 2文字以上の単語のみ
                        all_words.append(word)
                        # 対象キーワードを含む単語の位置を記録
                        if target_keyword in word or word == target_keyword:
                            target_positions.append(word_index)
                        word_index += 1
        
        # 共起語をカウント
        co_occurrence_counts = Counter()
        window_size = 3  # 前後3単語の範囲に縮小
        
        for pos in target_positions:
            start = max(0, pos - window_size)
            end = min(len(all_words), pos + window_size + 1)
            
            for i in range(start, end):
                if i != pos:
                    word = all_words[i]
                    # 対象キーワードと同じ単語は除外
                    if target_keyword not in word and word != target_keyword:
                        co_occurrence_counts[word] += 1
        
        # スコア計算（PMI: Pointwise Mutual Information の簡易版）
        total_words = len(all_words)
        target_count = len(target_positions)
        
        co_occurrences = []
        for word, count in co_occurrence_counts.most_common(20):
            if len(word) > 1:  # 1文字の単語は除外
                word_count = all_words.count(word)
                # ゼロ除算を防ぐ
                if target_count > 0 and word_count > 0 and total_words > 0:
                    # 簡易的なPMIスコア
                    pmi_score = math.log2((count * total_words) / (target_count * word_count))
                else:
                    pmi_score = 0
                co_occurrences.append({
                    "word": word,
                    "count": count,
                    "score": round(pmi_score, 3)
                })
        
        return sorted(co_occurrences, key=lambda x: x["score"], reverse=True)
    
    async def analyze_birth_flower_keywords(
        self, 
        month: int, 
        base_keyword: str
    ) -> Dict[str, Any]:
        """誕生花の月別キーワード分析"""
        
        flowers = self.birth_flowers_by_month.get(month, [])
        
        # 関連キーワード生成
        related_keywords = await self.get_related_keywords(base_keyword)
        
        # 花固有のキーワード
        flower_specific_keywords = []
        for flower in flowers:
            flower_keywords = [
                f"{flower} 花言葉",
                f"{flower} 意味",
                f"{flower} プレゼント",
                f"{flower} 特徴",
                f"{flower} 育て方",
                f"{month}月 {flower}"
            ]
            flower_specific_keywords.extend(flower_keywords)
        
        return {
            "primary_keyword": base_keyword,
            "month": month,
            "birth_flowers": flowers,
            "related_keywords": related_keywords,
            "flower_specific_keywords": flower_specific_keywords,
            "total_keywords": len(related_keywords) + len(flower_specific_keywords)
        }
    
    def cluster_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """キーワードをテーマ別にクラスタリング"""
        clusters = {
            "花言葉・意味": [],
            "プレゼント・ギフト": [],
            "花の種類・育て方": [],
            "月別・季節": [],
            "その他": []
        }
        
        for keyword in keywords:
            if "花言葉" in keyword or "意味" in keyword:
                clusters["花言葉・意味"].append(keyword)
            elif "プレゼント" in keyword or "ギフト" in keyword:
                clusters["プレゼント・ギフト"].append(keyword)
            elif "育て方" in keyword or "種類" in keyword:
                clusters["花の種類・育て方"].append(keyword)
            elif re.search(r'\d+月', keyword) or "季節" in keyword:
                clusters["月別・季節"].append(keyword)
            else:
                clusters["その他"].append(keyword)
        
        # 空のクラスターを除去して結果を整形
        result = []
        for theme, cluster_keywords in clusters.items():
            if cluster_keywords:
                result.append({
                    "theme": theme,
                    "keywords": cluster_keywords,
                    "count": len(cluster_keywords)
                })
        
        return result
    
    # ========== 拡張機能: Google Trends API連携とキーワード機能強化 ==========
    
    async def get_related_keywords_suggestions(self, keyword: str) -> Dict[str, Any]:
        """関連キーワード取得機能（サジェスト風）"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            # Google Suggest APIのような機能をシミュレート（実際のAPIは別途設定）
            suggestions = [
                f"{keyword} 一覧",
                f"{keyword} 花言葉",
                f"{keyword} プレゼント",
                f"{keyword} ギフト",
                f"{keyword} 意味",
                f"{keyword} 種類",
                f"{keyword} 育て方",
                f"{keyword} 通販",
                f"{keyword} おすすめ"
            ]
            
            # 誕生花の場合、月別の組み合わせを追加
            if "誕生花" in keyword:
                for month in range(1, 13):
                    suggestions.append(f"{month}月 誕生花")
                    suggestions.append(f"{month}月 誕生花 プレゼント")
            
            return {
                "related_keywords": suggestions,
                "total_count": len(suggestions),
                "source": "internal_generation"
            }
        except Exception as e:
            return {
                "related_keywords": [],
                "total_count": 0,
                "error": str(e)
            }
    
    async def get_google_trends_data(self, keyword: str) -> Dict[str, Any]:
        """Google Trends API連携（シミュレーション版）"""
        # 実際の実装では pytrends ライブラリを使用
        try:
            # シミュレーション データ
            current_date = datetime.now()
            monthly_data = {}
            
            # 12ヶ月分のデータを生成
            for i in range(12):
                month_date = current_date - timedelta(days=30 * i)
                month_key = month_date.strftime("%Y-%m-01")
                
                # 季節性を考慮した検索ボリューム（誕生花の場合）
                base_volume = 80
                if "誕生花" in keyword:
                    # 3月（春）と12月（年末）にピーク
                    month_num = month_date.month
                    if month_num in [3, 4, 5]:  # 春
                        base_volume += 40
                    elif month_num in [12, 1]:  # 年末年始
                        base_volume += 30
                    elif month_num in [6, 7, 8]:  # 夏
                        base_volume -= 20
                
                monthly_data[month_key] = min(100, max(10, base_volume))
            
            related_queries = [
                f"{keyword} 一覧",
                f"{keyword} 花言葉", 
                f"{keyword} プレゼント",
                f"{keyword} 3月",
                f"{keyword} 意味"
            ]
            
            # ピーク月を特定
            peak_months = [month for month, volume in monthly_data.items() 
                          if volume >= max(monthly_data.values()) * 0.9]
            
            return {
                "interest_over_time": {keyword: monthly_data},
                "related_queries": related_queries,
                "peak_months": peak_months,
                "seasonality_detected": len(peak_months) <= 3
            }
            
        except Exception as e:
            return {
                "interest_over_time": {},
                "related_queries": [],
                "peak_months": [],
                "error": str(e)
            }
    
    async def calculate_keyword_difficulty_enhanced(self, keyword: str) -> Dict[str, Any]:
        """強化されたキーワード難易度計算"""
        try:
            # 各要素を分析
            search_volume = await self._get_search_volume(keyword)
            competitor_count = await self._get_competitor_count(keyword)
            serp_analysis = await self._analyze_serp_competition(keyword)
            
            # 難易度スコア計算
            volume_score = min(50, search_volume / 100)  # 検索ボリューム影響
            competition_score = min(30, competitor_count / 1000)  # 競合数影響
            authority_score = serp_analysis.get("domain_authority_avg", 50) * 0.3  # ドメイン権威
            
            difficulty_score = volume_score + competition_score + authority_score
            difficulty_score = min(100, max(0, difficulty_score))
            
            # 推奨レベル
            if difficulty_score <= 30:
                recommendation = "Easy - 積極的に狙うべき"
            elif difficulty_score <= 60:
                recommendation = "Medium - リソース投入で可能"
            else:
                recommendation = "Hard - 長期戦略が必要"
            
            return {
                "difficulty_score": round(difficulty_score, 1),
                "search_volume": search_volume,
                "competitor_count": competitor_count,
                "competition_analysis": serp_analysis,
                "recommendation": recommendation,
                "factors": {
                    "volume_impact": volume_score,
                    "competition_impact": competition_score,
                    "authority_impact": authority_score
                }
            }
            
        except Exception as e:
            return {
                "difficulty_score": 50,
                "search_volume": 0,
                "competitor_count": 0,
                "error": str(e)
            }
    
    async def _get_search_volume(self, keyword: str) -> int:
        """検索ボリューム取得（簡易版）"""
        # 実際の実装では Google Ads API等を使用
        base_volume = 1000
        
        # キーワードの特徴に基づく調整
        if "誕生花" in keyword:
            base_volume += 1500
        if "プレゼント" in keyword or "ギフト" in keyword:
            base_volume += 800
        if re.search(r'\d+月', keyword):
            base_volume += 500
        
        return base_volume
    
    async def _get_competitor_count(self, keyword: str) -> int:
        """競合数取得（簡易版）"""
        # 実際の実装では検索エンジンAPIを使用
        base_count = 25000
        
        if "プレゼント" in keyword:
            base_count += 20000
        if "花言葉" in keyword:
            base_count += 10000
        
        return base_count
    
    async def _analyze_serp_competition(self, keyword: str) -> Dict[str, Any]:
        """SERP競合分析（簡易版）"""
        # 実際の実装では上位サイトを分析
        return {
            "domain_authority_avg": 65,
            "content_quality_score": 78,
            "commercial_intent_ratio": 0.6 if "プレゼント" in keyword else 0.3,
            "top_domains": ["example1.com", "example2.com"]
        }
    
    async def analyze_semantic_keywords(
        self, 
        base_keyword: str, 
        candidate_keywords: List[str], 
        context: str = ""
    ) -> Dict[str, Any]:
        """セマンティック関連キーワード分析"""
        semantic_matches = []
        
        for candidate in candidate_keywords:
            # 簡易的な類似度計算（実際の実装では word embeddings 使用）
            similarity = self._calculate_semantic_similarity(base_keyword, candidate, context)
            
            if similarity >= 0.7:  # 閾値
                semantic_matches.append({
                    "keyword": candidate,
                    "similarity_score": similarity,
                    "context_relevance": self._calculate_context_relevance(candidate, context)
                })
        
        # 類似度でソート
        semantic_matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "semantic_matches": semantic_matches,
            "total_matches": len(semantic_matches),
            "base_keyword": base_keyword,
            "context": context
        }
    
    def _calculate_semantic_similarity(self, keyword1: str, keyword2: str, context: str = "") -> float:
        """セマンティック類似度計算（簡易版）"""
        # 共通単語の割合を計算
        words1 = set(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', keyword1))
        words2 = set(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', keyword2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        base_similarity = intersection / union if union > 0 else 0
        
        # コンテキストによる調整
        context_boost = 0
        if context and any(word in keyword2 for word in context.split()):
            context_boost = 0.2
        
        return min(1.0, base_similarity + context_boost)
    
    def _calculate_context_relevance(self, keyword: str, context: str) -> float:
        """コンテキスト関連性計算"""
        if not context:
            return 0.5
        
        context_words = set(context.split())
        keyword_words = set(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', keyword))
        
        if not keyword_words:
            return 0.0
        
        relevance = len(context_words.intersection(keyword_words)) / len(keyword_words)
        return min(1.0, relevance)
    
    async def analyze_competitor_keywords(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """競合キーワード分析"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        all_keywords = []
        title_keywords = []
        meta_keywords = []
        heading_keywords = []
        
        for url in competitor_urls:
            try:
                async with self.session.get(url) as response:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Title抽出
                    title = soup.find('title')
                    if title:
                        title_text = title.get_text()
                        title_keywords.extend(self._extract_keywords_from_text(title_text))
                    
                    # Meta keywords 抽出
                    meta_kw = soup.find('meta', attrs={'name': 'keywords'})
                    if meta_kw:
                        meta_content = meta_kw.get('content', '')
                        meta_keywords.extend(meta_content.split(','))
                    
                    # Heading抽出
                    for heading in soup.find_all(['h1', 'h2', 'h3']):
                        heading_text = heading.get_text()
                        heading_keywords.extend(self._extract_keywords_from_text(heading_text))
                    
                    # 本文からキーワード抽出
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        p_text = p.get_text()
                        all_keywords.extend(self._extract_keywords_from_text(p_text))
                        
            except Exception as e:
                print(f"Error analyzing {url}: {e}")
                continue
        
        # キーワード頻度分析
        keyword_frequency = Counter(all_keywords)
        
        return {
            "extracted_keywords": list(set(all_keywords)),
            "title_keywords": list(set(title_keywords)),
            "meta_keywords": [kw.strip() for kw in set(meta_keywords) if kw.strip()],
            "heading_keywords": list(set(heading_keywords)),
            "keyword_frequency": dict(keyword_frequency.most_common(20)),
            "total_keywords": len(set(all_keywords)),
            "analyzed_urls": len(competitor_urls)
        }
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # 日本語の単語を抽出
        japanese_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', text)
        # 2文字以上の単語のみ
        return [word for word in japanese_words if len(word) >= 2]
    
    async def analyze_seasonal_trends(self, keyword: str) -> Dict[str, Any]:
        """季節性キーワードトレンド分析"""
        trends_data = await self.get_google_trends_data(keyword)
        monthly_interest = trends_data.get("interest_over_time", {}).get(keyword, {})
        
        if not monthly_interest:
            return {"error": "No trend data available"}
        
        # 月別データを数値で分析
        monthly_values = {}
        for date_str, value in monthly_interest.items():
            month = datetime.strptime(date_str, "%Y-%m-%d").month
            if month not in monthly_values:
                monthly_values[month] = []
            monthly_values[month].append(value)
        
        # 月別平均を計算
        monthly_avg = {}
        for month, values in monthly_values.items():
            monthly_avg[month] = sum(values) / len(values)
        
        # ピーク月とロー月を特定
        avg_value = sum(monthly_avg.values()) / len(monthly_avg)
        peak_months = [month for month, value in monthly_avg.items() if value >= avg_value * 1.2]
        low_months = [month for month, value in monthly_avg.items() if value <= avg_value * 0.8]
        
        # 季節性スコア（変動の大きさ）
        max_val = max(monthly_avg.values())
        min_val = min(monthly_avg.values())
        seasonality_score = (max_val - min_val) / avg_value if avg_value > 0 else 0
        
        return {
            "monthly_distribution": monthly_avg,
            "peak_months": peak_months,
            "low_months": low_months,
            "seasonality_score": round(seasonality_score, 2),
            "is_seasonal": seasonality_score > 0.5,
            "avg_interest": round(avg_value, 1)
        }
    
    async def generate_long_tail_keywords(self, base_keyword: str) -> Dict[str, Any]:
        """ロングテールキーワード生成"""
        modifiers = [
            "おすすめ", "人気", "ランキング", "比較", "選び方", "方法",
            "初心者", "簡単", "安い", "通販", "激安", "口コミ",
            "評判", "レビュー", "効果", "メリット", "デメリット"
        ]
        
        question_words = [
            "とは", "について", "意味", "理由", "なぜ", "どこで",
            "いつ", "どうやって", "どのように"
        ]
        
        long_tail_keywords = []
        
        # 3-4語の組み合わせを生成
        for modifier in modifiers:
            long_tail_keywords.append(f"{base_keyword} {modifier}")
            long_tail_keywords.append(f"{base_keyword} {modifier} 2024")
            
        for question in question_words:
            long_tail_keywords.append(f"{base_keyword} {question}")
        
        # 誕生花特有の組み合わせ
        if "誕生花" in base_keyword:
            seasonal_modifiers = ["春", "夏", "秋", "冬", "季節"]
            for season in seasonal_modifiers:
                long_tail_keywords.append(f"{base_keyword} {season} おすすめ")
        
        # 難易度推定
        difficulty_estimates = {}
        for keyword in long_tail_keywords[:10]:  # 上位10個を分析
            # ロングテールほど難易度が低い傾向
            word_count = len(keyword.split())
            base_difficulty = max(10, 70 - (word_count * 15))
            difficulty_estimates[keyword] = base_difficulty
        
        return {
            "long_tail_keywords": long_tail_keywords[:20],  # 上位20個
            "difficulty_estimates": difficulty_estimates,
            "total_generated": len(long_tail_keywords),
            "base_keyword": base_keyword
        }
    
    async def cluster_keywords_by_intent(self, keywords: List[str]) -> Dict[str, Any]:
        """キーワードを検索意図別にクラスタリング"""
        clusters = {
            "informational": [],  # 情報収集
            "commercial": [],     # 商用
            "navigational": [],   # ナビゲーション
            "transactional": []   # 取引
        }
        
        # 検索意図の判定キーワード
        commercial_indicators = ["プレゼント", "ギフト", "購入", "買う", "通販", "価格", "値段", "安い", "おすすめ"]
        informational_indicators = ["とは", "について", "意味", "方法", "やり方", "理由", "特徴", "種類"]
        navigational_indicators = ["公式", "サイト", "ホームページ", "ログイン", "アクセス"]
        transactional_indicators = ["注文", "申込", "予約", "ダウンロード", "登録", "購入方法"]
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 各意図のスコアを計算
            commercial_score = sum(1 for indicator in commercial_indicators if indicator in keyword)
            informational_score = sum(1 for indicator in informational_indicators if indicator in keyword)
            navigational_score = sum(1 for indicator in navigational_indicators if indicator in keyword)
            transactional_score = sum(1 for indicator in transactional_indicators if indicator in keyword)
            
            # 最も高いスコアの意図に分類
            scores = {
                "commercial": commercial_score,
                "informational": informational_score,
                "navigational": navigational_score,
                "transactional": transactional_score
            }
            
            max_intent = max(scores, key=scores.get)
            
            # スコアが0の場合は informational に分類
            if scores[max_intent] == 0:
                clusters["informational"].append(keyword)
            else:
                clusters[max_intent].append(keyword)
        
        return {
            "clusters": clusters,
            "cluster_sizes": {intent: len(keywords) for intent, keywords in clusters.items()},
            "total_keywords": len(keywords)
        }
    
    # API用の新しいメソッド
    async def analyze_keyword(self, keyword: str, include_trends: bool = True, 
                            include_related: bool = True, include_competitors: bool = False) -> Dict[str, Any]:
        """単一キーワードの総合分析"""
        result = {
            "keyword": keyword,
            "search_volume": 0,
            "difficulty": 0,
            "trend": "stable"
        }
        
        # 検索ボリューム取得
        volume_data = await self.get_search_volume(keyword)
        result["search_volume"] = volume_data.get("monthly_searches", 0)
        
        # 難易度計算
        difficulty_data = await self.analyze_difficulty([keyword])
        result["difficulty"] = difficulty_data.get(keyword, 50)
        
        # トレンド分析
        if include_trends:
            trends_data = await self.get_google_trends_data(keyword)
            if trends_data.get("seasonality_detected"):
                result["trend"] = "seasonal"
            else:
                # 簡易的なトレンド判定
                result["trend"] = "stable"
        
        # 関連キーワード
        if include_related:
            related = await self.get_related_keywords(keyword)
            result["related_keywords"] = related[:10]  # 上位10個
        
        return result
    
    async def suggest_keywords(self, seed_keyword: str, target_audience: str, 
                             content_type: str, count: int = 10) -> List[Dict[str, Any]]:
        """AI支援によるキーワード提案"""
        suggestions = []
        
        # 基本的な提案を生成
        base_suggestions = await self.generate_long_tail_keywords(seed_keyword)
        
        for i, keyword in enumerate(base_suggestions["long_tail_keywords"][:count]):
            suggestions.append({
                "keyword": keyword,
                "relevance_score": max(0.5, 1.0 - (i * 0.05)),  # 順位に基づくスコア
                "reasoning": f"{target_audience}向けの{content_type}に適したキーワード"
            })
        
        return suggestions
    
    async def get_search_volume_history(self, keyword: str) -> List[Dict[str, Any]]:
        """検索ボリューム履歴を取得"""
        volume_data = await self.get_search_volume(keyword)
        trend_data = volume_data.get("trend_data", [])
        
        history = []
        current_year = datetime.now().year
        
        for month_data in trend_data:
            month = month_data["month"]
            history.append({
                "month": f"{current_year}-{month:02d}",
                "search_volume": month_data["searches"],
                "year_over_year_change": 0  # 実装では前年同月比を計算
            })
        
        return history
    
    async def calculate_difficulty(self, keyword: str, include_breakdown: bool = False) -> Dict[str, Any]:
        """詳細な難易度計算"""
        enhanced_data = await self.calculate_keyword_difficulty_enhanced(keyword)
        
        result = {
            "keyword": keyword,
            "difficulty_score": enhanced_data.get("difficulty_score", 50)
        }
        
        if include_breakdown:
            result["breakdown"] = {
                "domain_authority_avg": enhanced_data.get("competition_analysis", {}).get("domain_authority_avg", 0),
                "backlinks_avg": 1000,  # 実装では実際のデータを使用
                "content_quality_avg": enhanced_data.get("competition_analysis", {}).get("content_quality_score", 0),
                "serp_features": ["featured_snippet", "people_also_ask"]  # 実装では実際のSERP機能を分析
            }
        
        return result