"""
Content Structure Template
コンテンツ構造テンプレート
"""
from typing import Dict, Any, List


class ContentStructureTemplate:
    """コンテンツ構造テンプレート"""
    
    def __init__(self):
        # 基本的な記事構造テンプレート
        self.base_structures = {
            "informational": {
                "introduction": {
                    "purpose": "読者の関心を引き、記事の価値を示す",
                    "elements": ["問題提起", "記事の価値", "読了後の期待効果"],
                    "recommended_length": 200
                },
                "main_sections": [
                    {"title": "基本情報・概要", "purpose": "基礎知識の提供"},
                    {"title": "詳細解説", "purpose": "深い理解の促進"},
                    {"title": "実例・具体例", "purpose": "理解の定着"},
                    {"title": "関連情報", "purpose": "知識の拡張"}
                ],
                "conclusion": {
                    "purpose": "要点のまとめと次のアクションの提示",
                    "elements": ["要点まとめ", "読者へのメッセージ", "関連記事紹介"],
                    "recommended_length": 150
                }
            },
            "commercial": {
                "introduction": {
                    "purpose": "購入検討の背景と記事の信頼性を示す",
                    "elements": ["読者の悩み共感", "解決策の提示", "記事の信頼性"],
                    "recommended_length": 250
                },
                "main_sections": [
                    {"title": "選び方のポイント", "purpose": "購入判断基準の提供"},
                    {"title": "おすすめ商品・サービス", "purpose": "具体的な選択肢の提示"},
                    {"title": "価格・予算ガイド", "purpose": "費用面の不安解消"},
                    {"title": "購入方法・注意点", "purpose": "安心な購入の支援"}
                ],
                "conclusion": {
                    "purpose": "購入決定の後押しとサポート情報",
                    "elements": ["決定のポイント再確認", "購入サポート", "アフターフォロー"],
                    "recommended_length": 200
                }
            },
            "navigational": {
                "introduction": {
                    "purpose": "比較検討の必要性と記事の客観性を示す",
                    "elements": ["比較の重要性", "客観的評価の約束", "判断基準の提示"],
                    "recommended_length": 180
                },
                "main_sections": [
                    {"title": "比較対象の紹介", "purpose": "選択肢の明確化"},
                    {"title": "項目別比較", "purpose": "客観的な比較情報"},
                    {"title": "シーン別おすすめ", "purpose": "状況に応じた推奨"},
                    {"title": "最終判断ガイド", "purpose": "決定支援"}
                ],
                "conclusion": {
                    "purpose": "最適な選択の確信と次のステップ",
                    "elements": ["判断基準の再確認", "選択の確信", "行動促進"],
                    "recommended_length": 160
                }
            }
        }
        
        # 誕生花記事特有のセクション
        self.birth_flower_sections = {
            "flower_basics": {
                "title": "基本情報と特徴",
                "subsections": ["学名・分類", "見た目の特徴", "開花時期", "原産地"]
            },
            "flower_language": {
                "title": "花言葉と意味",
                "subsections": ["主な花言葉", "花言葉の由来", "色別の花言葉", "文化的背景"]
            },
            "gift_ideas": {
                "title": "プレゼント・ギフトアイデア",
                "subsections": ["おすすめギフト", "予算別選択肢", "贈り方のマナー", "メッセージ例"]
            },
            "care_tips": {
                "title": "育て方・お手入れ",
                "subsections": ["基本的な育て方", "季節ごとのケア", "よくある問題", "長持ちのコツ"]
            },
            "seasonal_context": {
                "title": "季節との関係",
                "subsections": ["季節の特徴", "他の花との組み合わせ", "季節イベントとの関連"]
            }
        }
    
    async def generate_outline(self, article_concept: Dict[str, Any]) -> Dict[str, Any]:
        """記事コンセプトからアウトラインを生成"""
        
        concept_type = article_concept.get("type", "情報提供型")
        title = article_concept.get("title", "")
        target_word_count = article_concept.get("target_word_count", 3000)
        target_audience = article_concept.get("target_audience", "一般読者")
        
        # 検索意図を推定
        search_intent = self._infer_search_intent(concept_type, title)
        
        # 基本構造を取得
        base_structure = self.base_structures.get(search_intent, self.base_structures["informational"])
        
        # 誕生花特有のセクションを統合
        main_sections = self._integrate_birth_flower_sections(
            base_structure["main_sections"], concept_type, title
        )
        
        # 文字数配分を計算
        word_distribution = self._calculate_word_distribution(
            target_word_count, len(main_sections)
        )
        
        # CTA提案を生成
        cta_suggestions = self._generate_cta_suggestions(search_intent, target_audience)
        
        return {
            "introduction": {
                **base_structure["introduction"],
                "estimated_word_count": word_distribution["introduction"]
            },
            "main_sections": [
                {
                    **section,
                    "estimated_word_count": word_distribution["main_section"],
                    "subsections": self._generate_subsections(section["title"], concept_type)
                }
                for section in main_sections
            ],
            "conclusion": {
                **base_structure["conclusion"],
                "estimated_word_count": word_distribution["conclusion"]
            },
            "cta_suggestions": cta_suggestions,
            "total_estimated_words": target_word_count,
            "structure_type": search_intent,
            "seo_considerations": self._generate_seo_considerations(title)
        }
    
    def customize_structure_by_intent(self, base_topic: str, intent: str) -> Dict[str, Any]:
        """検索意図に応じた構造カスタマイズ"""
        
        base_structure = self.base_structures.get(intent, self.base_structures["informational"])
        
        if intent == "commercial":
            # 商用意図の場合、購入関連セクションを強化
            commercial_sections = [
                {"title": "選び方のポイント", "purpose": "購入決定要因の提供"},
                {"title": "おすすめ商品・サービス", "purpose": "具体的選択肢の提示"},
                {"title": "価格帯と予算ガイド", "purpose": "コスト面の不安解消"},
                {"title": "購入方法と信頼できる販売店", "purpose": "安心な購入方法の案内"},
                {"title": "よくある質問と注意点", "purpose": "購入時の疑問解消"}
            ]
            base_structure["main_sections"] = commercial_sections
            
        elif intent == "informational":
            # 情報収集意図の場合、教育的コンテンツを強化
            info_sections = [
                {"title": f"{base_topic}の基本知識", "purpose": "基礎理解の構築"},
                {"title": "歴史と文化的背景", "purpose": "深い理解の促進"},
                {"title": "種類と分類", "purpose": "詳細知識の提供"},
                {"title": "関連する話題・豆知識", "purpose": "興味の拡張"}
            ]
            base_structure["main_sections"] = info_sections
            
        elif intent == "navigational":
            # ナビゲーション意図の場合、比較・選択支援を強化
            nav_sections = [
                {"title": "比較対象の概要", "purpose": "選択肢の明確化"},
                {"title": "詳細比較・評価", "purpose": "客観的判断材料の提供"},
                {"title": "用途・シーン別おすすめ", "purpose": "状況別最適解の提示"},
                {"title": "最終選択のためのチェックリスト", "purpose": "決定支援"}
            ]
            base_structure["main_sections"] = nav_sections
        
        return base_structure
    
    def validate_structure_completeness(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """構造の完全性を検証"""
        
        required_elements = ["introduction", "main_sections", "conclusion"]
        missing_elements = []
        
        for element in required_elements:
            if element not in structure:
                missing_elements.append(element)
        
        # メインセクションの妥当性チェック
        issues = []
        if "main_sections" in structure:
            main_sections = structure["main_sections"]
            if len(main_sections) < 3:
                issues.append("メインセクションが少なすぎます（最低3つ推奨）")
            if len(main_sections) > 8:
                issues.append("メインセクションが多すぎます（最大8つ推奨）")
        
        # 文字数配分のチェック
        if "total_estimated_words" in structure:
            total_words = structure["total_estimated_words"]
            if total_words < 1500:
                issues.append("総文字数が少なすぎます（最低1500字推奨）")
            elif total_words > 6000:
                issues.append("総文字数が多すぎます（最大6000字推奨）")
        
        # 改善提案の生成
        recommendations = self._generate_structure_recommendations(structure, issues)
        
        return {
            "is_complete": len(missing_elements) == 0 and len(issues) == 0,
            "missing_elements": missing_elements,
            "structural_issues": issues,
            "recommendations": recommendations,
            "completeness_score": self._calculate_completeness_score(structure, missing_elements, issues)
        }
    
    def _infer_search_intent(self, concept_type: str, title: str) -> str:
        """コンセプトタイプとタイトルから検索意図を推定"""
        
        if concept_type == "比較検討型":
            return "navigational"
        elif any(word in title for word in ["プレゼント", "ギフト", "選び方", "おすすめ"]):
            return "commercial"
        else:
            return "informational"
    
    def _integrate_birth_flower_sections(
        self, base_sections: List[Dict[str, Any]], concept_type: str, title: str
    ) -> List[Dict[str, Any]]:
        """誕生花特有のセクションを統合"""
        
        integrated_sections = []
        
        # 基本情報は常に含める
        integrated_sections.append({
            "title": "誕生花の基本情報と特徴",
            "purpose": "花の基礎知識を提供"
        })
        
        # 花言葉セクションも常に含める
        integrated_sections.append({
            "title": "花言葉と込められた意味",
            "purpose": "花言葉の理解を深める"
        })
        
        # コンセプトタイプに応じて追加セクション決定
        if "プレゼント" in title or "ギフト" in title or concept_type == "問題解決型":
            integrated_sections.append({
                "title": "プレゼント・ギフトアイデア",
                "purpose": "具体的な贈り物提案"
            })
        
        if concept_type == "情報提供型":
            integrated_sections.append({
                "title": "育て方とお手入れ方法",
                "purpose": "実用的な栽培情報"
            })
        
        # 季節性のセクション
        integrated_sections.append({
            "title": "季節感と他の花との組み合わせ",
            "purpose": "季節コンテキストの提供"
        })
        
        return integrated_sections
    
    def _calculate_word_distribution(self, total_words: int, main_section_count: int) -> Dict[str, int]:
        """文字数配分を計算"""
        
        # 基本配分比率
        intro_ratio = 0.08  # 8%
        conclusion_ratio = 0.07  # 7%
        main_ratio = 0.85  # 85%
        
        introduction_words = int(total_words * intro_ratio)
        conclusion_words = int(total_words * conclusion_ratio)
        main_total_words = total_words - introduction_words - conclusion_words
        main_section_words = main_total_words // main_section_count
        
        return {
            "introduction": introduction_words,
            "main_section": main_section_words,
            "conclusion": conclusion_words,
            "main_total": main_total_words
        }
    
    def _generate_subsections(self, section_title: str, concept_type: str) -> List[str]:
        """セクションタイトルとコンセプトに基づいてサブセクションを生成"""
        
        subsections = []
        
        if "基本情報" in section_title or "特徴" in section_title:
            subsections = ["学名と分類", "外見の特徴", "開花時期・季節", "原産地と分布"]
            
        elif "花言葉" in section_title:
            subsections = ["代表的な花言葉", "花言葉の由来・歴史", "色別の花言葉", "文化による違い"]
            
        elif "プレゼント" in section_title or "ギフト" in section_title:
            subsections = ["おすすめギフトアイデア", "予算別選択肢", "贈る際のマナー", "メッセージカード例文"]
            
        elif "育て方" in section_title:
            subsections = ["基本的な栽培方法", "季節ごとのお手入れ", "よくあるトラブル対処", "長持ちさせるコツ"]
            
        elif "季節" in section_title:
            subsections = ["季節の特徴と花の関係", "他の花との組み合わせ", "季節イベントでの活用"]
            
        else:
            # デフォルトのサブセクション
            subsections = ["概要", "詳細解説", "実例・応用", "まとめ"]
        
        return subsections
    
    def _generate_cta_suggestions(self, intent: str, audience: str) -> List[Dict[str, Any]]:
        """CTAの提案を生成"""
        
        cta_suggestions = []
        
        if intent == "commercial":
            cta_suggestions.extend([
                {
                    "type": "購入促進",
                    "text": "おすすめの花屋さんをチェック",
                    "placement": "記事中盤"
                },
                {
                    "type": "相談促進",
                    "text": "花選びでお悩みの方はお気軽にご相談ください",
                    "placement": "記事終盤"
                }
            ])
        
        elif intent == "informational":
            cta_suggestions.extend([
                {
                    "type": "関連記事誘導",
                    "text": "他の月の誕生花も見てみる",
                    "placement": "記事終盤"
                },
                {
                    "type": "知識共有",
                    "text": "この記事をSNSでシェアする",
                    "placement": "記事末尾"
                }
            ])
        
        else:  # navigational
            cta_suggestions.extend([
                {
                    "type": "比較支援",
                    "text": "あなたに最適な花を診断してみる",
                    "placement": "記事中盤"
                },
                {
                    "type": "詳細相談",
                    "text": "専門家に相談してみる",
                    "placement": "記事終盤"
                }
            ])
        
        return cta_suggestions
    
    def _generate_seo_considerations(self, title: str) -> Dict[str, Any]:
        """SEO考慮事項を生成"""
        
        return {
            "title_optimization": [
                "タイトルにメインキーワードを含める",
                "タイトル長は32文字以内に収める",
                "読者の関心を引く表現を使用"
            ],
            "heading_structure": [
                "H1タグはタイトルのみに使用",
                "H2タグでメインセクションを構成",
                "H3タグでサブセクションを整理"
            ],
            "content_optimization": [
                "メインキーワードを適切な密度で配置",
                "関連キーワードを自然に挿入",
                "読者にとって価値のある情報を提供"
            ],
            "meta_description": "花言葉、プレゼント、特徴など主要な要素を含めた160文字以内の説明文"
        }
    
    def _generate_structure_recommendations(
        self, structure: Dict[str, Any], issues: List[str]
    ) -> List[str]:
        """構造改善の提案を生成"""
        
        recommendations = []
        
        if issues:
            recommendations.append("構造的な問題を修正することを優先してください")
        
        if "main_sections" in structure:
            section_count = len(structure["main_sections"])
            if section_count < 4:
                recommendations.append("読者により価値のある情報を提供するため、追加セクションを検討してください")
            elif section_count > 6:
                recommendations.append("読みやすさのため、関連セクションの統合を検討してください")
        
        recommendations.extend([
            "各セクションの目的を明確に定義してください",
            "読者の検索意図に合わせた構成を心がけてください",
            "CTAの配置を戦略的に計画してください",
            "SEO要件を満たす見出し構造を使用してください"
        ])
        
        return recommendations
    
    def _calculate_completeness_score(
        self, structure: Dict[str, Any], missing_elements: List[str], issues: List[str]
    ) -> float:
        """完全性スコアを計算"""
        
        base_score = 100
        
        # 欠落要素によるペナルティ
        base_score -= len(missing_elements) * 25
        
        # 構造的問題によるペナルティ
        base_score -= len(issues) * 10
        
        # ボーナス要素
        if "cta_suggestions" in structure:
            base_score += 5
        
        if "seo_considerations" in structure:
            base_score += 5
        
        return max(0, min(100, base_score))