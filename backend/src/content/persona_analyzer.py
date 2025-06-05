"""
Persona Analyzer
ターゲットペルソナ分析機能
"""
import asyncio
from typing import Dict, Any, List
import re


class PersonaAnalyzer:
    """ペルソナ分析クラス"""
    
    def __init__(self):
        # 誕生花関連のペルソナテンプレート
        self.persona_templates = {
            "ギフト購入者": {
                "demographics": {
                    "age_range": "25-45歳",
                    "gender": "主に女性、一部男性",
                    "occupation": "会社員、主婦、学生",
                    "income_level": "中間層"
                },
                "psychographics": {
                    "values": ["思いやり", "関係性重視", "記念日を大切にする"],
                    "interests": ["ギフト選び", "季節のイベント", "花・ガーデニング"],
                    "lifestyle": "忙しい日常の中で大切な人への気遣いを忘れない"
                },
                "pain_points": [
                    "適切なプレゼント選びに悩む",
                    "花言葉や意味がわからない",
                    "予算内で素敵なギフトを見つけたい",
                    "贈る相手に喜んでもらえるか不安"
                ],
                "goals": [
                    "相手に喜んでもらえるプレゼントを選ぶ",
                    "花言葉を理解して意味のあるギフトにする",
                    "特別感のあるプレゼントを贈る"
                ]
            },
            "花好き愛好家": {
                "demographics": {
                    "age_range": "30-65歳",
                    "gender": "主に女性",
                    "occupation": "多様（ガーデニング愛好家）",
                    "income_level": "中間層以上"
                },
                "psychographics": {
                    "values": ["自然愛好", "美しさの追求", "知識習得"],
                    "interests": ["ガーデニング", "フラワーアレンジメント", "植物の知識"],
                    "lifestyle": "花や植物に囲まれた生活を好む"
                },
                "pain_points": [
                    "より深い花の知識を得たい",
                    "季節の花の特徴を知りたい",
                    "花の育て方がわからない"
                ],
                "goals": [
                    "花に関する知識を深める",
                    "季節に合った花を楽しむ",
                    "美しい花を育てる"
                ]
            },
            "一般学習者": {
                "demographics": {
                    "age_range": "18-50歳",
                    "gender": "男女両方",
                    "occupation": "学生、会社員",
                    "income_level": "様々"
                },
                "psychographics": {
                    "values": ["知識習得", "教養向上", "文化理解"],
                    "interests": ["一般教養", "文化", "季節の話題"],
                    "lifestyle": "学習意欲旺盛で新しい知識を求める"
                },
                "pain_points": [
                    "基本的な花の知識がない",
                    "誕生花の意味がわからない",
                    "文化的背景を知りたい"
                ],
                "goals": [
                    "誕生花について基本的な知識を得る",
                    "花言葉の意味を理解する",
                    "日本の花文化を学ぶ"
                ]
            }
        }
    
    async def analyze_target_persona(self, keyword: str, search_intent: str) -> Dict[str, Any]:
        """キーワードと検索意図からターゲットペルソナを分析"""
        
        # キーワードからペルソナタイプを推定
        persona_type = self._infer_persona_type(keyword, search_intent)
        base_persona = self.persona_templates.get(persona_type, self.persona_templates["一般学習者"])
        
        # キーワード特有の調整を加える
        customized_persona = self._customize_persona_for_keyword(base_persona, keyword)
        
        # 検索意図に基づいた調整
        if search_intent == "商用":
            customized_persona = self._enhance_for_commercial_intent(customized_persona)
        
        # メタデータを追加
        customized_persona["persona_type"] = persona_type
        customized_persona["primary_keyword"] = keyword
        customized_persona["search_intent"] = search_intent
        customized_persona["preferred_content_style"] = self._determine_content_style(persona_type, search_intent)
        
        return customized_persona
    
    async def generate_persona_variations(self, base_keyword: str) -> List[Dict[str, Any]]:
        """ベースキーワードから複数のペルソナバリエーションを生成"""
        variations = []
        
        # 各ペルソナタイプに対してバリエーションを生成
        for persona_type, template in self.persona_templates.items():
            variation = template.copy()
            variation["persona_type"] = persona_type
            variation["relevance_to_keyword"] = self._calculate_keyword_relevance(persona_type, base_keyword)
            variation["content_preferences"] = self._generate_content_preferences(persona_type, base_keyword)
            variations.append(variation)
        
        # 関連性でソート
        variations.sort(key=lambda x: x["relevance_to_keyword"], reverse=True)
        return variations
    
    def extract_persona_from_keywords(self, keyword_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """キーワード分析結果からペルソナインサイトを抽出"""
        primary_keyword = keyword_analysis["primary_keyword"]
        related_keywords = keyword_analysis.get("related_keywords", [])
        search_intent = keyword_analysis.get("search_intent", "情報収集")
        
        # 検索行動パターンを分析
        search_behavior = self._analyze_search_behavior(related_keywords)
        
        # ターゲットオーディエンスを特定
        target_audience = self._identify_target_audience(primary_keyword, related_keywords)
        
        # コンテンツの好みを推定
        content_preferences = self._infer_content_preferences(related_keywords, search_intent)
        
        return {
            "target_audience": target_audience,
            "search_behavior": search_behavior,
            "content_preferences": content_preferences,
            "engagement_factors": self._identify_engagement_factors(related_keywords)
        }
    
    def _infer_persona_type(self, keyword: str, search_intent: str) -> str:
        """キーワードと検索意図からペルソナタイプを推定"""
        if any(word in keyword for word in ["プレゼント", "ギフト", "贈り物"]):
            return "ギフト購入者"
        elif any(word in keyword for word in ["育て方", "種類", "特徴", "栽培"]):
            return "花好き愛好家"
        elif search_intent == "商用":
            return "ギフト購入者"
        else:
            return "一般学習者"
    
    def _customize_persona_for_keyword(self, base_persona: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """キーワードに応じてペルソナをカスタマイズ"""
        customized = base_persona.copy()
        
        # 月別キーワードの場合、季節性を追加
        month_match = re.search(r'(\d+)月', keyword)
        if month_match:
            month = int(month_match.group(1))
            seasonal_interests = self._get_seasonal_interests(month)
            customized["psychographics"]["interests"].extend(seasonal_interests)
        
        # 特定の花の名前が含まれている場合
        flower_names = ["チューリップ", "バラ", "カーネーション", "スズラン", "ヒマワリ"]
        for flower in flower_names:
            if flower in keyword:
                flower_specific_goals = [f"{flower}について詳しく知りたい", f"{flower}を贈り物として選びたい"]
                customized["goals"].extend(flower_specific_goals)
                break
        
        return customized
    
    def _enhance_for_commercial_intent(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """商用検索意図に基づいてペルソナを強化"""
        enhanced = persona.copy()
        
        # 購買関連のペインポイントを追加
        commercial_pain_points = [
            "信頼できる花屋を見つけたい",
            "品質の良い花を購入したい",
            "配送で花が傷まないか心配",
            "適正な価格かわからない"
        ]
        enhanced["pain_points"].extend(commercial_pain_points)
        
        # 購買関連のゴールを追加
        commercial_goals = [
            "最適な花屋・通販サイトを見つける",
            "予算に合った良い花を購入する",
            "安心して花を注文する"
        ]
        enhanced["goals"].extend(commercial_goals)
        
        return enhanced
    
    def _determine_content_style(self, persona_type: str, search_intent: str) -> Dict[str, Any]:
        """ペルソナタイプと検索意図からコンテンツスタイルを決定"""
        styles = {
            "ギフト購入者": {
                "tone": "親しみやすく実用的",
                "structure": "ステップバイステップ形式",
                "visual_needs": "商品画像、比較表",
                "call_to_action": "購入促進、相談促進"
            },
            "花好き愛好家": {
                "tone": "専門的だが親しみやすい",
                "structure": "詳細な解説中心",
                "visual_needs": "高品質な花の写真、図解",
                "call_to_action": "知識共有、コミュニティ参加"
            },
            "一般学習者": {
                "tone": "教育的でわかりやすい",
                "structure": "基本から応用へ段階的",
                "visual_needs": "図解、チャート",
                "call_to_action": "関連記事へ誘導、学習継続"
            }
        }
        
        base_style = styles.get(persona_type, styles["一般学習者"])
        
        # 検索意図に応じた調整
        if search_intent == "商用":
            base_style["call_to_action"] = "購入促進、問い合わせ誘導"
            base_style["visual_needs"] += ", 価格情報"
        
        return base_style
    
    def _calculate_keyword_relevance(self, persona_type: str, keyword: str) -> float:
        """ペルソナタイプとキーワードの関連性スコアを計算"""
        relevance_keywords = {
            "ギフト購入者": ["プレゼント", "ギフト", "贈り物", "母の日", "記念日"],
            "花好き愛好家": ["育て方", "種類", "栽培", "ガーデニング", "アレンジメント"],
            "一般学習者": ["花言葉", "意味", "一覧", "について", "とは"]
        }
        
        keywords_for_type = relevance_keywords.get(persona_type, [])
        matches = sum(1 for kw in keywords_for_type if kw in keyword)
        
        return min(matches / len(keywords_for_type) if keywords_for_type else 0, 1.0)
    
    def _generate_content_preferences(self, persona_type: str, keyword: str) -> Dict[str, Any]:
        """ペルソナタイプとキーワードからコンテンツの好みを生成"""
        preferences = {
            "preferred_length": "medium",  # short, medium, long
            "information_depth": "moderate",  # basic, moderate, detailed
            "visual_importance": "high",
            "actionable_advice": True,
            "personal_stories": False
        }
        
        if persona_type == "花好き愛好家":
            preferences["information_depth"] = "detailed"
            preferences["preferred_length"] = "long"
            preferences["personal_stories"] = True
        elif persona_type == "ギフト購入者":
            preferences["actionable_advice"] = True
            preferences["visual_importance"] = "very_high"
        
        return preferences
    
    def _analyze_search_behavior(self, related_keywords: List[str]) -> Dict[str, Any]:
        """関連キーワードから検索行動を分析"""
        behavior_patterns = {
            "information_seeking": 0,
            "comparison_shopping": 0,
            "購買意欲": 0,
            "problem_solving": 0
        }
        
        for keyword in related_keywords:
            if any(word in keyword for word in ["とは", "意味", "について"]):
                behavior_patterns["information_seeking"] += 1
            elif any(word in keyword for word in ["比較", "おすすめ", "ランキング"]):
                behavior_patterns["comparison_shopping"] += 1
            elif any(word in keyword for word in ["購入", "通販", "価格", "安い"]):
                behavior_patterns["購買意欲"] += 1
            elif any(word in keyword for word in ["選び方", "方法", "コツ"]):
                behavior_patterns["problem_solving"] += 1
        
        # 正規化
        total = sum(behavior_patterns.values())
        if total > 0:
            for key in behavior_patterns:
                behavior_patterns[key] = behavior_patterns[key] / total
        
        return behavior_patterns
    
    def _identify_target_audience(self, primary_keyword: str, related_keywords: List[str]) -> str:
        """メインターゲットオーディエンスを特定"""
        all_keywords = [primary_keyword] + related_keywords
        
        if any(any(word in kw for word in ["母の日", "プレゼント", "ギフト"]) for kw in all_keywords):
            return "プレゼント購入検討者"
        elif any(any(word in kw for word in ["育て方", "栽培", "種類"]) for kw in all_keywords):
            return "ガーデニング愛好家"
        else:
            return "花の知識を求める一般読者"
    
    def _infer_content_preferences(self, related_keywords: List[str], search_intent: str) -> Dict[str, Any]:
        """コンテンツの好みを推定"""
        preferences = {
            "format_preferences": [],
            "content_elements": [],
            "engagement_style": "informative"
        }
        
        # フォーマットの好み
        if any("一覧" in kw for kw in related_keywords):
            preferences["format_preferences"].append("リスト形式")
        if any(any(word in kw for word in ["比較", "選び方"]) for kw in related_keywords):
            preferences["format_preferences"].append("比較表")
        if any(any(word in kw for word in ["方法", "やり方"]) for kw in related_keywords):
            preferences["format_preferences"].append("ステップバイステップ")
        
        # コンテンツ要素
        if search_intent == "商用":
            preferences["content_elements"].extend(["価格情報", "購入リンク", "レビュー"])
            preferences["engagement_style"] = "persuasive"
        else:
            preferences["content_elements"].extend(["詳細説明", "背景情報", "関連知識"])
        
        return preferences
    
    def _identify_engagement_factors(self, related_keywords: List[str]) -> List[str]:
        """エンゲージメント要因を特定"""
        factors = []
        
        if any("画像" in kw or "写真" in kw for kw in related_keywords):
            factors.append("高品質な視覚コンテンツ")
        if any(any(word in kw for word in ["体験", "レビュー", "口コミ"]) for kw in related_keywords):
            factors.append("実体験・レビュー")
        if any("無料" in kw or "お得" in kw for kw in related_keywords):
            factors.append("お得感・特典")
        if any(any(word in kw for word in ["簡単", "初心者"]) for kw in related_keywords):
            factors.append("わかりやすい説明")
        
        # デフォルトの要因
        factors.extend([
            "季節感のある内容",
            "実用的なアドバイス",
            "感情に訴える表現"
        ])
        
        return list(set(factors))
    
    def _get_seasonal_interests(self, month: int) -> List[str]:
        """月に応じた季節的な興味関心を取得"""
        seasonal_interests = {
            3: ["春の訪れ", "新生活", "卒業・入学"],
            4: ["新学期", "桜", "お花見"],
            5: ["母の日", "ゴールデンウィーク", "新緑"],
            6: ["梅雨", "紫陽花", "父の日"],
            12: ["クリスマス", "年末", "冬の装飾"]
        }
        
        return seasonal_interests.get(month, ["季節の移ろい", "自然の美しさ"])