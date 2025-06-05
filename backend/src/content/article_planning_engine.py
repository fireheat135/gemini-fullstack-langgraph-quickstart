"""
Article Planning Engine
記事企画エンジン
"""
import asyncio
from typing import Dict, Any, List
import random


class ArticlePlanningEngine:
    """記事企画エンジン"""
    
    def __init__(self):
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
        
        # 季節イベント
        self.seasonal_events = {
            3: ["卒業式", "入学式", "お花見"],
            4: ["新学期", "桜の季節"],
            5: ["母の日", "ゴールデンウィーク"],
            6: ["父の日", "梅雨"],
            12: ["クリスマス", "年末", "お正月準備"]
        }
    
    async def generate_four_concepts(self, topic_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """4つのコンセプトパターンを生成"""
        month = topic_info.get("month")
        primary_keyword = topic_info["primary_keyword"]
        target_persona = topic_info.get("target_persona", "一般読者")
        search_intent = topic_info.get("search_intent", "情報収集")
        
        flowers = self.birth_flowers_by_month.get(month, ["誕生花"])
        
        concepts = []
        
        # 1. 情報提供型
        info_concept = await self._generate_informational_concept(
            month, flowers, primary_keyword, target_persona
        )
        concepts.append(info_concept)
        
        # 2. 問題解決型
        problem_solving_concept = await self._generate_problem_solving_concept(
            month, flowers, primary_keyword, target_persona
        )
        concepts.append(problem_solving_concept)
        
        # 3. 比較検討型
        comparison_concept = await self._generate_comparison_concept(
            month, flowers, primary_keyword, target_persona
        )
        concepts.append(comparison_concept)
        
        # 4. エンターテイメント型
        entertainment_concept = await self._generate_entertainment_concept(
            month, flowers, primary_keyword, target_persona
        )
        concepts.append(entertainment_concept)
        
        return concepts
    
    async def evaluate_concept_feasibility(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """企画の実現可能性を評価"""
        concept_type = concept.get("type", "情報提供型")
        target_keyword = concept.get("target_keyword", "")
        estimated_word_count = concept.get("estimated_word_count", 2000)
        
        # 基本実現可能性スコア
        base_score = 80
        
        # タイプ別調整
        type_adjustments = {
            "情報提供型": 10,    # 作成しやすい
            "問題解決型": 5,     # 中程度
            "比較検討型": -5,    # やや複雑
            "エンターテイメント型": -10  # 創作要素が必要
        }
        
        feasibility_score = base_score + type_adjustments.get(concept_type, 0)
        
        # 文字数による調整
        if estimated_word_count > 4000:
            feasibility_score -= 10
        elif estimated_word_count < 1500:
            feasibility_score += 5
        
        # キーワード競合度の影響（簡易計算）
        keyword_difficulty = self._estimate_keyword_difficulty(target_keyword)
        if keyword_difficulty > 70:
            feasibility_score -= 15
        elif keyword_difficulty < 30:
            feasibility_score += 10
        
        feasibility_score = max(0, min(100, feasibility_score))
        
        # リソース要件の計算
        resource_requirements = self._calculate_resource_requirements(concept)
        
        # ROI予測
        roi_prediction = self._predict_roi(concept, feasibility_score)
        
        # リスク要因
        risk_factors = self._identify_risk_factors(concept, keyword_difficulty)
        
        return {
            "feasibility_score": feasibility_score,
            "resource_requirements": resource_requirements,
            "roi_prediction": roi_prediction,
            "risk_factors": risk_factors,
            "recommendations": self._generate_feasibility_recommendations(
                feasibility_score, risk_factors
            )
        }
    
    async def generate_seasonal_concepts(self, month_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """季節特化のコンセプトを生成"""
        month = month_data["month"]
        flowers = month_data["flowers"]
        season = month_data.get("season", "")
        events = month_data.get("events", [])
        
        seasonal_concepts = []
        
        for event in events:
            concept = {
                "type": "季節特化型",
                "title": f"{event}に贈る{month}月の誕生花{flowers[0]}の魅力",
                "seasonal_angle": f"{event}の特別な贈り物として{flowers[0]}を提案",
                "target_emotion": "季節感と特別感",
                "unique_value": f"{event}の文脈で{flowers[0]}の意味を深掘り",
                "content_highlights": [
                    f"{event}における花の意味",
                    f"{flowers[0]}が{event}に適している理由",
                    f"{season}らしい贈り方のアイデア",
                    "季節限定の花言葉解釈"
                ],
                "estimated_engagement": "高（季節性により検索が集中）",
                "differentiation_factor": f"{event}と{flowers[0]}の特別な組み合わせ"
            }
            seasonal_concepts.append(concept)
        
        # 季節全体を通したコンセプト
        if len(flowers) > 1:
            seasonal_overview = {
                "type": "季節総合型",
                "title": f"{season}を彩る{month}月の誕生花完全ガイド",
                "seasonal_angle": f"{season}の美しさを{' & '.join(flowers)}で表現",
                "target_emotion": "季節の移ろいと自然への感謝",
                "unique_value": f"{season}の特徴と{flowers}の組み合わせの魅力",
                "content_highlights": [
                    f"{season}の特徴と花の関係",
                    "複数の誕生花の比較と選び方",
                    f"{season}らしいアレンジメント提案",
                    "季節の移ろいと花言葉の変化"
                ],
                "estimated_engagement": "中〜高",
                "differentiation_factor": f"包括的な{season}誕生花ガイド"
            }
            seasonal_concepts.append(seasonal_overview)
        
        return seasonal_concepts
    
    async def _generate_informational_concept(
        self, month: int, flowers: List[str], keyword: str, persona: str
    ) -> Dict[str, Any]:
        """情報提供型コンセプトを生成"""
        primary_flower = flowers[0] if flowers else "誕生花"
        
        return {
            "type": "情報提供型",
            "title": f"{month}月の誕生花{primary_flower}の花言葉と魅力を徹底解説",
            "concept_summary": f"{primary_flower}の基本情報から花言葉、歴史まで包括的に紹介",
            "target_emotion": "知識欲の満足、学びの喜び",
            "content_structure": [
                f"{primary_flower}の基本情報",
                "花言葉とその由来",
                "歴史と文化的背景",
                "種類と特徴",
                "季節との関係"
            ],
            "expected_outcome": "読者の知識向上と満足感",
            "engagement_strategy": "詳細な情報と美しい画像で知識欲を満たす",
            "cta_focus": "関連記事への誘導、知識の共有",
            "estimated_word_count": 3000,
            "visual_needs": ["花の種類別写真", "図解", "歴史的資料"]
        }
    
    async def _generate_problem_solving_concept(
        self, month: int, flowers: List[str], keyword: str, persona: str
    ) -> Dict[str, Any]:
        """問題解決型コンセプトを生成"""
        primary_flower = flowers[0] if flowers else "誕生花"
        
        return {
            "type": "問題解決型",
            "title": f"{month}月生まれの人への完璧なプレゼント選び：{primary_flower}ギフトガイド",
            "concept_summary": "プレゼント選びの悩みを解決する実践的なガイド",
            "target_emotion": "安心感、自信、達成感",
            "content_structure": [
                "プレゼント選びの一般的な悩み",
                f"{primary_flower}がプレゼントに最適な理由",
                "予算別おすすめギフト",
                "贈り方のマナーとコツ",
                "失敗しない花屋選び"
            ],
            "expected_outcome": "読者のプレゼント選びの成功",
            "engagement_strategy": "具体的な解決策と実例で信頼感を構築",
            "cta_focus": "購入促進、相談サービスへの誘導",
            "estimated_word_count": 3500,
            "visual_needs": ["商品画像", "価格比較表", "ギフト例写真"]
        }
    
    async def _generate_comparison_concept(
        self, month: int, flowers: List[str], keyword: str, persona: str
    ) -> Dict[str, Any]:
        """比較検討型コンセプトを生成"""
        if len(flowers) >= 2:
            title = f"{month}月の誕生花{flowers[0]}vs{flowers[1]}：どちらを選ぶべき？"
            comparison_focus = f"{flowers[0]}と{flowers[1]}の詳細比較"
        else:
            title = f"{month}月の誕生花 vs 他の季節の花：プレゼント選択ガイド"
            comparison_focus = "誕生花と他の人気な花の比較"
        
        return {
            "type": "比較検討型",
            "title": title,
            "concept_summary": comparison_focus,
            "target_emotion": "納得感、選択の確信",
            "content_structure": [
                "比較対象の紹介",
                "花言葉・意味の比較",
                "見た目・特徴の比較",
                "価格・入手しやすさの比較",
                "シーン別おすすめ判定"
            ],
            "expected_outcome": "読者の最適な選択支援",
            "engagement_strategy": "客観的な比較データで選択を支援",
            "cta_focus": "商品比較、専門相談への誘導",
            "estimated_word_count": 4000,
            "visual_needs": ["比較表", "並列画像", "チャート"]
        }
    
    async def _generate_entertainment_concept(
        self, month: int, flowers: List[str], keyword: str, persona: str
    ) -> Dict[str, Any]:
        """エンターテイメント型コンセプトを生成"""
        primary_flower = flowers[0] if flowers else "誕生花"
        
        return {
            "type": "エンターテイメント型",
            "title": f"あなたの性格を{primary_flower}で占う！{month}月誕生花診断",
            "concept_summary": f"{primary_flower}の特徴と読者の性格を関連付けた楽しいコンテンツ",
            "target_emotion": "楽しさ、興味、共感",
            "content_structure": [
                f"{primary_flower}性格診断テスト",
                "花言葉と性格の関係性",
                "有名人の誕生花エピソード",
                f"{primary_flower}にまつわる伝説・神話",
                "花占いの歴史と文化"
            ],
            "expected_outcome": "読者の楽しみとシェア欲の満足",
            "engagement_strategy": "インタラクティブ要素とシェアしやすい内容",
            "cta_focus": "SNSシェア、診断結果の保存",
            "estimated_word_count": 2500,
            "visual_needs": ["診断フローチャート", "性格タイプ別画像", "インフォグラフィック"]
        }
    
    def _estimate_keyword_difficulty(self, keyword: str) -> float:
        """キーワード難易度を推定（簡易版）"""
        base_difficulty = 50
        
        # 競合が多そうなキーワード
        competitive_terms = ["プレゼント", "ギフト", "人気", "ランキング", "おすすめ"]
        for term in competitive_terms:
            if term in keyword:
                base_difficulty += 15
        
        # ニッチなキーワード
        niche_terms = ["花言葉", "意味", "由来", "特徴"]
        for term in niche_terms:
            if term in keyword:
                base_difficulty -= 10
        
        # 月指定は競合が少ない
        if any(f"{i}月" in keyword for i in range(1, 13)):
            base_difficulty -= 15
        
        return max(10, min(90, base_difficulty))
    
    def _calculate_resource_requirements(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """リソース要件を計算"""
        concept_type = concept.get("type", "情報提供型")
        word_count = concept.get("estimated_word_count", 2000)
        
        # 基本工数（時間）
        base_hours = {
            "情報提供型": 6,
            "問題解決型": 8,
            "比較検討型": 10,
            "エンターテイメント型": 12
        }
        
        writing_hours = base_hours.get(concept_type, 8)
        
        # 文字数による調整
        writing_hours += (word_count - 2000) / 1000 * 2
        
        return {
            "writing_hours": max(4, writing_hours),
            "research_hours": writing_hours * 0.3,
            "visual_creation_hours": 2,
            "editing_hours": writing_hours * 0.2,
            "total_hours": writing_hours * 1.5 + 2,
            "skill_requirements": [
                "花・ガーデニングの基礎知識",
                "SEOライティング",
                "ターゲット読者への共感力"
            ]
        }
    
    def _predict_roi(self, concept: Dict[str, Any], feasibility_score: float) -> Dict[str, Any]:
        """ROI予測"""
        concept_type = concept.get("type", "情報提供型")
        
        # タイプ別期待効果
        type_multipliers = {
            "情報提供型": 0.8,
            "問題解決型": 1.2,
            "比較検討型": 1.1,
            "エンターテイメント型": 0.9
        }
        
        base_traffic_score = 100
        conversion_potential = type_multipliers.get(concept_type, 1.0)
        
        # 実現可能性による調整
        adjusted_score = base_traffic_score * (feasibility_score / 100) * conversion_potential
        
        return {
            "traffic_potential": int(adjusted_score),
            "conversion_rate_expectation": conversion_potential,
            "engagement_score": feasibility_score * conversion_potential,
            "long_term_value": "高" if concept_type in ["情報提供型", "問題解決型"] else "中"
        }
    
    def _identify_risk_factors(self, concept: Dict[str, Any], keyword_difficulty: float) -> List[str]:
        """リスク要因を特定"""
        risks = []
        
        if keyword_difficulty > 70:
            risks.append("高い競合により上位表示が困難")
        
        concept_type = concept.get("type", "")
        if concept_type == "エンターテイメント型":
            risks.append("創作要素が多く品質のばらつきリスク")
        
        word_count = concept.get("estimated_word_count", 2000)
        if word_count > 4000:
            risks.append("長文コンテンツによる読者離脱リスク")
        
        if "比較" in concept_type:
            risks.append("競合他社情報の正確性確保の必要性")
        
        return risks
    
    def _generate_feasibility_recommendations(
        self, feasibility_score: float, risk_factors: List[str]
    ) -> List[str]:
        """実現可能性に基づく推奨事項を生成"""
        recommendations = []
        
        if feasibility_score < 60:
            recommendations.append("企画の簡素化または別アプローチの検討")
        elif feasibility_score < 80:
            recommendations.append("リソース配分の最適化が必要")
        else:
            recommendations.append("高い成功確率、積極的に実行推奨")
        
        if risk_factors:
            recommendations.append("特定されたリスク要因への対策計画を策定")
        
        recommendations.extend([
            "ターゲット読者のフィードバック収集",
            "競合分析の定期的な更新",
            "コンテンツ品質の継続的な改善"
        ])
        
        return recommendations