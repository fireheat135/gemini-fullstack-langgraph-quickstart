"""
Tone & Manner Engine
トーン&マナー設定エンジン

Phase 5: コンテンツ管理・品質担保
- 過去記事とのトンマナ比較機能
- 文体・表現一貫性チェック機能
- ブランドボイス適合性評価システム
- 修正提案生成機能

TDD Green Phase: 最小限の実装
"""
from typing import Dict, Any, List, Tuple, Optional
import re
import math
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ToneMannnerEngine:
    """トーン&マナー設定エンジン"""
    
    def __init__(self):
        # 基本トーンテンプレート
        self.tone_templates = {
            "friendly_casual": {
                "tone_type": "friendly_casual",
                "description": "親しみやすく気軽な雰囲気で、友人に話すような自然な文体",
                "characteristics": [
                    "敬語と丁寧語のバランス",
                    "親近感のある表現",
                    "読者との距離感を縮める"
                ],
                "sample_phrases": [
                    "～ですよね",
                    "実は～なんです",
                    "ちょっと気になるのが",
                    "おすすめしたいのが",
                    "きっと喜んでもらえると思います"
                ],
                "writing_guidelines": [
                    "硬すぎない敬語を使用",
                    "読者への共感を示す",
                    "具体例を多用する",
                    "疑問形で読者の関心を引く"
                ]
            },
            "professional_helpful": {
                "tone_type": "professional_helpful",
                "description": "専門的でありながら親切で、信頼できるアドバイザーとしての文体",
                "characteristics": [
                    "専門知識の提供",
                    "客観的で正確な情報",
                    "読者の問題解決に焦点"
                ],
                "sample_phrases": [
                    "専門的な観点から申し上げますと",
                    "経験上おすすめできるのは",
                    "注意していただきたいポイントは",
                    "確実な方法としては",
                    "最適な選択肢は"
                ],
                "writing_guidelines": [
                    "根拠のある情報を提供",
                    "段階的な説明を心がける",
                    "専門用語には説明を付ける",
                    "実践的なアドバイスを含める"
                ]
            },
            "warm_emotional": {
                "tone_type": "warm_emotional",
                "description": "温かく感情的で、読者の心に寄り添うような共感的な文体",
                "characteristics": [
                    "感情に訴える表現",
                    "ストーリー性のある内容",
                    "読者の気持ちへの共感"
                ],
                "sample_phrases": [
                    "心を込めて選んだ",
                    "特別な想いを伝える",
                    "きっと心に響く",
                    "大切な人への愛情を",
                    "感動を与えてくれる"
                ],
                "writing_guidelines": [
                    "エモーショナルな表現を活用",
                    "読者の体験に共感する",
                    "ストーリーテリングを取り入れる",
                    "温かみのある言葉選びを重視"
                ]
            },
            "expert_authoritative": {
                "tone_type": "expert_authoritative",
                "description": "専門家としての権威性を示し、確実で信頼性の高い情報を提供する文体",
                "characteristics": [
                    "高い専門性の表現",
                    "データに基づく内容",
                    "権威的だが親しみやすい"
                ],
                "sample_phrases": [
                    "園芸専門家の視点から",
                    "研究結果によると",
                    "長年の経験から言えることは",
                    "確実にお伝えできるのは",
                    "専門的な知見として"
                ],
                "writing_guidelines": [
                    "専門的な根拠を示す",
                    "データや統計を活用",
                    "業界用語を適切に使用",
                    "権威性と親しみやすさのバランス"
                ]
            }
        }
        
        # 花・季節特有の表現集
        self.flower_expressions = {
            "季節感": [
                "春の訪れとともに",
                "季節の移ろいとともに",
                "〜の季節にふさわしい",
                "この時期ならではの",
                "季節の恵みとして"
            ],
            "感情表現": [
                "心を癒してくれる",
                "優雅な美しさ",
                "気品ある佇まい",
                "凛とした美しさ",
                "華やかな存在感"
            ],
            "ギフト関連": [
                "心を込めた贈り物",
                "特別な日にふさわしい",
                "想いを伝える",
                "記念に残る",
                "喜びを分かち合う"
            ]
        }
        
    def generate_tone_variations(self, target_audience: str, content_purpose: str) -> List[Dict[str, Any]]:
        """ターゲットオーディエンスとコンテンツ目的に応じたトーンバリエーションを生成"""
        
        variations = []
        
        for tone_type, template in self.tone_templates.items():
            # ターゲットオーディエンスに応じた調整
            adjusted_template = self._adjust_for_audience(template.copy(), target_audience)
            
            # コンテンツ目的に応じた調整
            adjusted_template = self._adjust_for_purpose(adjusted_template, content_purpose)
            
            # 適合度スコアを計算
            suitability_score = self._calculate_suitability(
                tone_type, target_audience, content_purpose
            )
            adjusted_template["suitability_score"] = suitability_score
            
            variations.append(adjusted_template)
        
        # 適合度でソート
        variations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return variations
    
    def customize_for_flower_content(self, base_tone: str, flower_context: Dict[str, Any]) -> Dict[str, Any]:
        """誕生花コンテンツ用のトーンカスタマイズ"""
        
        base_template = self.tone_templates.get(base_tone, self.tone_templates["friendly_casual"])
        customized = base_template.copy()
        
        flowers = flower_context.get("flowers", [])
        occasion = flower_context.get("occasion", "")
        emotion = flower_context.get("emotion", "")
        
        # 花特有の言語表現を追加
        flower_language = []
        for flower in flowers:
            flower_language.extend(self._get_flower_specific_expressions(flower))
        
        # 感情表現を追加
        emotional_expressions = self._get_emotional_expressions_for_context(emotion, occasion)
        
        # 季節への言及を追加
        seasonal_references = self._get_seasonal_references(flowers)
        
        # 禁止表現を定義
        prohibited_expressions = self._define_prohibited_expressions()
        
        customized.update({
            "flower_specific_language": flower_language,
            "emotional_expressions": emotional_expressions,
            "seasonal_references": seasonal_references,
            "禁止表現": prohibited_expressions,
            "flower_context": flower_context
        })
        
        return customized
    
    def generate_brand_voice_guidelines(self, brand_characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """ブランドボイスガイドラインを生成"""
        
        brand_personality = brand_characteristics.get("brand_personality", "")
        target_relationship = brand_characteristics.get("target_relationship", "")
        expertise_level = brand_characteristics.get("expertise_level", "")
        
        # ブランドの属性を分析
        voice_attributes = self._extract_voice_attributes(brand_personality)
        
        # 推奨フレーズと禁止フレーズを生成
        do_phrases = self._generate_do_phrases(voice_attributes, target_relationship)
        dont_phrases = self._generate_dont_phrases(voice_attributes)
        
        # 一貫性ルール
        consistency_rules = self._create_consistency_rules(expertise_level, target_relationship)
        
        return {
            "voice_attributes": voice_attributes,
            "do_phrases": do_phrases,
            "dont_phrases": dont_phrases,
            "consistency_rules": consistency_rules,
            "tone_examples": self._generate_tone_examples(voice_attributes),
            "brand_characteristics": brand_characteristics
        }
    
    def _adjust_for_audience(self, template: Dict[str, Any], audience: str) -> Dict[str, Any]:
        """オーディエンスに応じた調整"""
        
        if "30代女性" in audience and "プレゼント" in audience:
            # プレゼント購入検討中の30代女性向け調整
            template["sample_phrases"].extend([
                "同じくらいの年代の女性として",
                "実際に選んでみた経験から",
                "私も悩んだのですが",
                "きっと気に入ってもらえると思います"
            ])
            template["writing_guidelines"].append("共感と実体験を重視")
        
        return template
    
    def _adjust_for_purpose(self, template: Dict[str, Any], purpose: str) -> Dict[str, Any]:
        """コンテンツ目的に応じた調整"""
        
        if "誕生花選び" in purpose:
            template["sample_phrases"].extend([
                "誕生花を選ぶ際のポイントは",
                "花言葉を知ることで",
                "その人らしい花を",
                "特別な意味を込めて"
            ])
            template["writing_guidelines"].append("花選びの実用性を重視")
        
        return template
    
    def _calculate_suitability(self, tone_type: str, audience: str, purpose: str) -> float:
        """適合度スコアを計算"""
        
        base_score = 50
        
        # オーディエンス適合度
        if "プレゼント購入" in audience:
            if tone_type == "professional_helpful":
                base_score += 20
            elif tone_type == "warm_emotional":
                base_score += 15
        
        if "30代女性" in audience:
            if tone_type == "friendly_casual":
                base_score += 15
            elif tone_type == "warm_emotional":
                base_score += 10
        
        # 目的適合度
        if "誕生花選び" in purpose:
            if tone_type == "professional_helpful":
                base_score += 15
            elif tone_type == "friendly_casual":
                base_score += 10
        
        return min(100, max(0, base_score))
    
    def _get_flower_specific_expressions(self, flower: str) -> List[str]:
        """花固有の表現を取得"""
        
        flower_expressions = {
            "チューリップ": [
                "色とりどりの",
                "春の使者",
                "可憐な佇まい",
                "明るい印象"
            ],
            "バラ": [
                "気品ある",
                "永遠の美しさ",
                "愛の象徴",
                "華やかな魅力"
            ],
            "カーネーション": [
                "優しい印象",
                "母への愛",
                "温かな気持ち",
                "包容力のある"
            ],
            "スズラン": [
                "可憐で上品",
                "清楚な美しさ",
                "繊細な魅力",
                "初夏の訪れ"
            ]
        }
        
        return flower_expressions.get(flower, ["美しい", "魅力的な", "素敵な"])
    
    def _get_emotional_expressions_for_context(self, emotion: str, occasion: str) -> List[str]:
        """文脈に応じた感情表現を取得"""
        
        expressions = []
        
        if "喜び" in emotion:
            expressions.extend([
                "心躍る", "嬉しくなる", "明るい気持ちに", "笑顔になれる"
            ])
        
        if "新しい始まり" in emotion:
            expressions.extend([
                "希望に満ちた", "新たなスタート", "前向きな気持ち", "フレッシュな"
            ])
        
        if "春" in occasion or "プレゼント" in occasion:
            expressions.extend([
                "心温まる", "特別な想い", "優しい気持ち", "感謝の気持ち"
            ])
        
        return expressions
    
    def _get_seasonal_references(self, flowers: List[str]) -> List[str]:
        """季節への言及を取得"""
        
        seasonal_refs = []
        
        # 花から季節を推定
        spring_flowers = ["チューリップ", "スイートアリッサム", "スイートピー"]
        summer_flowers = ["ヒマワリ", "ユリ"]
        winter_flowers = ["ポインセチア", "カトレア"]
        
        for flower in flowers:
            if flower in spring_flowers:
                seasonal_refs.extend([
                    "春の陽だまりのような",
                    "新緑の季節にふさわしい",
                    "桜の季節と同じく"
                ])
            elif flower in summer_flowers:
                seasonal_refs.extend([
                    "夏の太陽のような",
                    "暑い季節に爽やかな",
                    "青空に映える"
                ])
            elif flower in winter_flowers:
                seasonal_refs.extend([
                    "冬の華やかさを",
                    "寒い季節に暖かさを",
                    "年末年始にふさわしい"
                ])
        
        if not seasonal_refs:
            seasonal_refs = ["季節を彩る", "時期にぴったりの", "この時季ならではの"]
        
        return seasonal_refs
    
    def _define_prohibited_expressions(self) -> List[str]:
        """禁止表現を定義"""
        
        return [
            "絶対に",
            "必ず",
            "100%",
            "確実に",
            "間違いなく",
            "誰でも",
            "みんな",
            "最高の",
            "最安値",
            "業界No.1"
        ]
    
    def _extract_voice_attributes(self, personality: str) -> List[str]:
        """ブランドパーソナリティから音声属性を抽出"""
        
        attributes = []
        
        if "温かい" in personality:
            attributes.extend(["親しみやすい", "共感的", "支援的"])
        
        if "信頼できる" in personality:
            attributes.extend(["正確", "客観的", "根拠のある"])
        
        if "専門的" in personality:
            attributes.extend(["知識豊富", "権威的", "教育的"])
        
        return attributes
    
    def _generate_do_phrases(self, attributes: List[str], relationship: str) -> List[str]:
        """推奨フレーズを生成"""
        
        do_phrases = []
        
        if "親しみやすい" in attributes:
            do_phrases.extend([
                "一緒に考えてみましょう",
                "お手伝いさせていただきます",
                "ご相談ください"
            ])
        
        if "知識豊富" in attributes:
            do_phrases.extend([
                "専門的な観点から",
                "経験に基づいて",
                "詳しくご説明します"
            ])
        
        if "友人のような" in relationship:
            do_phrases.extend([
                "実は〜なんです",
                "個人的におすすめなのは",
                "一緒に選んでみませんか"
            ])
        
        return do_phrases
    
    def _generate_dont_phrases(self, attributes: List[str]) -> List[str]:
        """禁止フレーズを生成"""
        
        dont_phrases = [
            "買わないと損",
            "今すぐ購入",
            "限定価格",
            "特別価格",
            "他では手に入らない"
        ]
        
        if "親しみやすい" in attributes:
            dont_phrases.extend([
                "申し上げます",
                "恐縮ですが",
                "失礼いたします"
            ])
        
        return dont_phrases
    
    def _create_consistency_rules(self, expertise_level: str, relationship: str) -> List[str]:
        """一貫性ルールを作成"""
        
        rules = [
            "同じトーンを記事全体で維持する",
            "読者との距離感を一定に保つ",
            "専門用語の使用レベルを統一する"
        ]
        
        if "中級者向け" in expertise_level:
            rules.append("専門用語には簡潔な説明を付ける")
        
        if "友人のような" in relationship:
            rules.append("親しみやすさと専門性のバランスを保つ")
        
        return rules
    
    def _generate_tone_examples(self, attributes: List[str]) -> Dict[str, str]:
        """トーンの例文を生成"""
        
        examples = {}
        
        if "親しみやすい" in attributes:
            examples["greeting"] = "こんにちは！今日は〜についてお話ししますね。"
            examples["explanation"] = "実は、〜ということなんです。"
            examples["closing"] = "いかがでしたでしょうか？何かご質問があればお気軽にどうぞ！"
        
        if "専門的" in attributes:
            examples["greeting"] = "〜の専門家として、詳しくご説明いたします。"
            examples["explanation"] = "専門的な観点から申し上げますと、〜"
            examples["closing"] = "より詳しい情報が必要でしたら、お気軽にお問い合わせください。"
        
        return examples
    
    # ========================================
    # Phase 5: 一貫性チェック機能
    # ========================================
    
    def compare_with_past_articles(self, current_article: Dict[str, Any], past_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """過去記事とのトーン&マナー比較機能"""
        if not current_article or not current_article.get("tone_profile"):
            raise ValueError("Article with tone profile is required")
        
        current_tone = current_article["tone_profile"]
        matching_articles = []
        tone_variations = []
        
        for past_article in past_articles:
            if not past_article.get("tone_profile"):
                continue
                
            past_tone = past_article["tone_profile"]
            similarity_score = self._calculate_tone_similarity(current_tone, past_tone)
            
            if similarity_score > 0.7:  # 70%以上の類似度
                matching_articles.append({
                    "article_id": past_article["id"],
                    "similarity_score": similarity_score
                })
            else:
                tone_variations.append({
                    "article_id": past_article["id"], 
                    "variation_score": 1.0 - similarity_score,
                    "differences": self._identify_tone_differences(current_tone, past_tone)
                })
        
        overall_consistency = len(matching_articles) / len(past_articles) if past_articles else 1.0
        
        return {
            "consistency_score": overall_consistency,
            "matching_articles": matching_articles,
            "tone_variations": tone_variations,
            "recommendation": "consistent" if overall_consistency > 0.8 else "review_needed"
        }
    
    def check_writing_consistency(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """文体・表現一貫性チェック機能"""
        if not article or not article.get("content"):
            raise ValueError("Article content is required")
        
        if not article.get("tone_profile"):
            raise ValueError("Tone profile is required")
        
        content = article["content"]
        tone_profile = article["tone_profile"]
        
        # 文体の一貫性をチェック
        consistency_issues = []
        
        # 敬語レベルの一貫性
        formality_issues = self._check_formality_consistency_internal(content, tone_profile)
        consistency_issues.extend(formality_issues)
        
        # 禁止表現のチェック
        prohibited_issues = self._check_prohibited_expressions_internal(content, tone_profile)
        consistency_issues.extend(prohibited_issues)
        
        # トーンドリフトのチェック  
        drift_issues = self._check_tone_drift_internal(content, tone_profile)
        consistency_issues.extend(drift_issues)
        
        # 一貫性スコアを計算
        consistency_score = max(0.0, 1.0 - (len(consistency_issues) * 0.1))
        is_consistent = consistency_score >= 0.8
        
        return {
            "is_consistent": is_consistent,
            "consistency_score": consistency_score,
            "consistency_issues": consistency_issues,
            "total_issues": len(consistency_issues)
        }
    
    def evaluate_brand_voice_compatibility(self, article: Dict[str, Any], brand_guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """ブランドボイス適合性評価システム"""
        if not article or not article.get("content"):
            raise ValueError("Article content is required")
        
        if not brand_guidelines:
            raise ValueError("Brand guidelines are required")
        
        content = article["content"]
        compliance_issues = []
        
        # DO/DON'T フレーズのチェック
        dont_phrases = brand_guidelines.get("dont_phrases", [])
        prohibited_violations = self.detect_prohibited_expressions(content, dont_phrases)
        
        if prohibited_violations["violations_found"]:
            compliance_issues.extend(prohibited_violations["violation_details"])
        
        # ブランド属性との整合性チェック
        voice_attributes = brand_guidelines.get("voice_attributes", [])
        attribute_alignment = self._check_attribute_alignment(content, voice_attributes)
        
        # 適合性スコアを計算
        compatibility_score = max(0.0, 1.0 - (len(compliance_issues) * 0.15))
        
        return {
            "compatibility_score": compatibility_score,
            "compliance_issues": compliance_issues,
            "brand_alignment": attribute_alignment,
            "overall_status": "compliant" if compatibility_score > 0.8 else "needs_review"
        }
    
    def detect_prohibited_expressions(self, content: str, prohibited_list: List[str]) -> Dict[str, Any]:
        """禁止表現の検出"""
        if not content:
            return {"violations_found": False, "violation_details": []}
        
        violations = []
        
        for prohibited in prohibited_list:
            # 大文字小文字を区別しない検索
            pattern = re.compile(re.escape(prohibited), re.IGNORECASE)
            matches = pattern.finditer(content)
            
            for match in matches:
                violations.append({
                    "expression": prohibited,
                    "found_text": match.group(),
                    "position": match.start(),
                    "context": content[max(0, match.start()-20):match.end()+20]
                })
        
        return {
            "violations_found": len(violations) > 0,
            "violation_details": violations,
            "violation_count": len(violations)
        }
    
    def detect_tone_drift(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """記事内でのトーンの変化（ドリフト）検出"""
        if not article or not article.get("content"):
            raise ValueError("Article content is required")
        
        content = article["content"]
        
        # 段落に分割
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        if len(paragraphs) < 2:
            return {
                "has_tone_drift": False,
                "drift_locations": [],
                "severity_score": 0.0
            }
        
        drift_locations = []
        
        # 隣接する段落間でトーンの変化をチェック
        for i in range(len(paragraphs) - 1):
            current_para = paragraphs[i]
            next_para = paragraphs[i + 1]
            
            # 簡単なトーン変化検出（敬語レベルの変化）
            current_formality = self._calculate_formality_score(current_para)
            next_formality = self._calculate_formality_score(next_para)
            
            formality_diff = abs(current_formality - next_formality)
            
            if formality_diff > 0.3:  # 30%以上の変化
                drift_locations.append({
                    "paragraph_index": i,
                    "drift_type": "formality_change",
                    "severity": formality_diff,
                    "description": f"段落{i+1}から{i+2}で敬語レベルが大きく変化"
                })
        
        has_drift = len(drift_locations) > 0
        severity_score = max([loc["severity"] for loc in drift_locations]) if drift_locations else 0.0
        
        return {
            "has_tone_drift": has_drift,
            "drift_locations": drift_locations,
            "severity_score": severity_score
        }
    
    def check_formality_consistency(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """敬語・丁寧語レベルの一貫性チェック"""
        if not article or not article.get("content"):
            raise ValueError("Article content is required")
        
        content = article["content"]
        expected_level = article.get("tone_profile", {}).get("formality_level", "やや丁寧")
        
        # 文章を文単位に分割
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        formality_scores = []
        inconsistent_patterns = []
        
        for i, sentence in enumerate(sentences):
            score = self._calculate_formality_score(sentence)
            formality_scores.append(score)
            
            # 期待値との差をチェック
            expected_score = self._get_expected_formality_score(expected_level)
            if abs(score - expected_score) > 0.3:
                inconsistent_patterns.append({
                    "sentence_index": i,
                    "sentence": sentence,
                    "actual_score": score,
                    "expected_score": expected_score
                })
        
        overall_score = 1.0 - (len(inconsistent_patterns) / len(sentences)) if sentences else 1.0
        
        return {
            "formality_score": overall_score,
            "inconsistent_patterns": inconsistent_patterns,
            "recommended_level": expected_level,
            "average_formality": sum(formality_scores) / len(formality_scores) if formality_scores else 0.0
        }
    
    def analyze_emotional_tone(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """感情トーンの分析と一貫性チェック"""
        if not article or not article.get("content"):
            raise ValueError("Article content is required")
        
        content = article["content"]
        
        # 感情キーワードの定義
        emotion_keywords = {
            "positive": ["美しい", "素晴らしい", "魅力的", "喜び", "幸せ", "嬉しい"],
            "neutral": ["です", "ます", "について", "として", "により"],
            "warm": ["温かい", "優しい", "心地よい", "癒し", "安らぎ"],
            "professional": ["専門的", "確実", "正確", "適切", "効果的"]
        }
        
        emotion_scores = {}
        total_words = 0
        
        for emotion, keywords in emotion_keywords.items():
            count = 0
            for keyword in keywords:
                count += content.count(keyword)
            emotion_scores[emotion] = count
            total_words += count
        
        # 感情分布を正規化
        emotion_distribution = {}
        if total_words > 0:
            for emotion, count in emotion_scores.items():
                emotion_distribution[emotion] = count / total_words
        
        # 主要感情を特定
        dominant_emotion = max(emotion_distribution.items(), key=lambda x: x[1])[0] if emotion_distribution else "neutral"
        
        # 一貫性を計算（最大値と最小値の差が小さいほど一貫）
        if emotion_distribution:
            max_score = max(emotion_distribution.values())
            min_score = min(emotion_distribution.values())
            emotion_consistency = 1.0 - (max_score - min_score)
        else:
            emotion_consistency = 1.0
        
        return {
            "dominant_emotion": dominant_emotion,
            "emotion_consistency": emotion_consistency,
            "emotion_distribution": emotion_distribution,
            "total_emotional_words": total_words
        }
    
    def check_audience_alignment(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """読者層との適合性チェック"""
        if not article or not article.get("tone_profile"):
            raise ValueError("Article with tone profile is required")
        
        tone_profile = article["tone_profile"]
        target_audience = tone_profile.get("target_audience", "")
        content = article.get("content", "")
        
        misalignment_issues = []
        alignment_score = 1.0
        
        # 読者層別のチェック
        if "30代女性" in target_audience:
            # 30代女性向けのチェック
            if "申し上げます" in content or "ご説明いたします" in content:
                misalignment_issues.append({
                    "issue": "過度に丁寧な表現",
                    "description": "30代女性には親しみやすいトーンの方が適切"
                })
                alignment_score -= 0.2
        
        if "プレゼント購入" in target_audience:
            # プレゼント購入検討者向けのチェック
            practical_words = ["選ぶ", "おすすめ", "ポイント", "注意"]
            practical_count = sum(content.count(word) for word in practical_words)
            
            if practical_count < 2:
                misalignment_issues.append({
                    "issue": "実用性の不足",
                    "description": "プレゼント選びの実用的な情報が不足"
                })
                alignment_score -= 0.3
        
        recommendations = []
        if misalignment_issues:
            recommendations.append("読者層により適したトーンへの調整")
            recommendations.append("実用的な情報の追加")
        
        return {
            "alignment_score": max(0.0, alignment_score),
            "misalignment_issues": misalignment_issues,
            "recommendations": recommendations,
            "target_audience": target_audience
        }
    
    def generate_improvement_suggestions(self, article: Dict[str, Any], brand_guidelines: Dict[str, Any]) -> Dict[str, Any]:
        """改善提案生成機能"""
        if not article or not article.get("content"):
            raise ValueError("Article content is required")
        
        content = article["content"]
        priority_issues = []
        specific_recommendations = []
        revised_sentences = []
        
        # 一貫性チェック結果を取得
        consistency_result = self.check_writing_consistency(article)
        
        # ブランド適合性チェック結果を取得
        if brand_guidelines:
            brand_result = self.evaluate_brand_voice_compatibility(article, brand_guidelines)
            
            if brand_result["compatibility_score"] < 0.8:
                priority_issues.append({
                    "type": "brand_compliance",
                    "severity": "high",
                    "description": "ブランドガイドラインとの整合性が不足"
                })
        
        # 具体的な改善提案を生成
        if not consistency_result["is_consistent"]:
            priority_issues.append({
                "type": "consistency",
                "severity": "high",
                "description": "文体の一貫性に問題があります"
            })
            
            specific_recommendations.extend([
                "記事全体で同一の敬語レベルを維持してください",
                "禁止表現を適切な表現に置き換えてください",
                "読者との距離感を一定に保ってください"
            ])
        
        # 文章の改善例を提案
        sentences = re.split(r'[。！？]', content)
        for sentence in sentences[:3]:  # 最初の3文のみ
            if sentence.strip():
                improved = self._suggest_sentence_improvement(sentence.strip(), brand_guidelines)
                if improved != sentence.strip():
                    revised_sentences.append({
                        "original": sentence.strip(),
                        "improved": improved,
                        "reason": "トーンの改善"
                    })
        
        return {
            "priority_issues": priority_issues,
            "specific_recommendations": specific_recommendations,
            "revised_sentences": revised_sentences,
            "improvement_score": 1.0 - len(priority_issues) * 0.2
        }
    
    def analyze_bulk_consistency(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """複数記事の一括一貫性分析"""
        if not articles:
            raise ValueError("Articles list is required")
        
        article_scores = []
        all_issues = []
        
        for i, article in enumerate(articles):
            try:
                consistency_result = self.check_writing_consistency(article)
                
                article_scores.append({
                    "article_id": article.get("id", f"article_{i}"),
                    "consistency_score": consistency_result["consistency_score"],
                    "is_consistent": consistency_result["is_consistent"],
                    "issue_count": len(consistency_result["consistency_issues"])
                })
                
                all_issues.extend(consistency_result["consistency_issues"])
                
            except Exception as e:
                logger.warning(f"Failed to analyze article {i}: {e}")
                article_scores.append({
                    "article_id": article.get("id", f"article_{i}"),
                    "consistency_score": 0.0,
                    "is_consistent": False,
                    "error": str(e)
                })
        
        # 全体の一貫性を計算
        valid_scores = [score["consistency_score"] for score in article_scores if "error" not in score]
        overall_consistency = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        
        # 共通の問題を特定
        issue_types = [issue.get("type", "unknown") for issue in all_issues]
        common_issues = [item for item, count in Counter(issue_types).most_common(3)]
        
        return {
            "overall_consistency": overall_consistency,
            "article_scores": article_scores,
            "common_issues": common_issues,
            "total_articles": len(articles),
            "consistent_articles": sum(1 for score in article_scores if score.get("is_consistent", False))
        }
    
    # ========================================
    # ヘルパーメソッド
    # ========================================
    
    def _calculate_tone_similarity(self, tone1: Dict[str, Any], tone2: Dict[str, Any]) -> float:
        """トーン間の類似度を計算"""
        similarity_score = 0.0
        total_factors = 0
        
        # 基本的な属性の比較
        comparable_keys = ["writing_style", "formality_level", "emotional_tone"]
        
        for key in comparable_keys:
            if key in tone1 and key in tone2:
                if tone1[key] == tone2[key]:
                    similarity_score += 1.0
                total_factors += 1
        
        return similarity_score / total_factors if total_factors > 0 else 0.0
    
    def _identify_tone_differences(self, tone1: Dict[str, Any], tone2: Dict[str, Any]) -> List[str]:
        """トーン間の差異を特定"""
        differences = []
        
        comparable_keys = ["writing_style", "formality_level", "emotional_tone"]
        
        for key in comparable_keys:
            if key in tone1 and key in tone2 and tone1[key] != tone2[key]:
                differences.append(f"{key}: {tone1[key]} vs {tone2[key]}")
        
        return differences
    
    def _check_formality_consistency_internal(self, content: str, tone_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """内部用：敬語レベルの一貫性チェック"""
        issues = []
        
        # 敬語表現のパターン
        formal_patterns = ["いたします", "申し上げます", "ございます"]
        casual_patterns = ["です", "ます", "～ですよね"]
        
        formal_count = sum(content.count(pattern) for pattern in formal_patterns)
        casual_count = sum(content.count(pattern) for pattern in casual_patterns)
        
        expected_level = tone_profile.get("formality_level", "やや丁寧")
        
        if expected_level == "やや丁寧" and formal_count > casual_count:
            issues.append({
                "type": "formality_mismatch",
                "description": "過度に丁寧な表現が多用されています",
                "severity": "medium"
            })
        
        return issues
    
    def _check_prohibited_expressions_internal(self, content: str, tone_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """内部用：禁止表現のチェック"""
        issues = []
        
        prohibited = tone_profile.get("prohibited_expressions", [])
        
        for expr in prohibited:
            if expr in content:
                issues.append({
                    "type": "prohibited_expression",
                    "description": f"禁止表現「{expr}」が使用されています",
                    "severity": "high"
                })
        
        return issues
    
    def _check_tone_drift_internal(self, content: str, tone_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """内部用：トーンドリフトのチェック"""
        issues = []
        
        drift_result = self.detect_tone_drift({"content": content})
        
        if drift_result["has_tone_drift"]:
            for drift in drift_result["drift_locations"]:
                issues.append({
                    "type": "tone_drift",
                    "description": drift["description"],
                    "severity": "medium" if drift["severity"] < 0.5 else "high"
                })
        
        return issues
    
    def _check_attribute_alignment(self, content: str, voice_attributes: List[str]) -> Dict[str, Any]:
        """ブランド属性との整合性チェック"""
        alignment_score = 1.0
        
        # 属性別のキーワードチェック
        attribute_indicators = {
            "親しみやすい": ["一緒に", "おすすめ", "ですよね", "実は"],
            "知識豊富": ["専門的", "経験", "データ", "研究"],
            "共感的": ["お気持ち", "理解", "共感", "寄り添う"]
        }
        
        for attr in voice_attributes:
            if attr in attribute_indicators:
                indicators = attribute_indicators[attr]
                found_indicators = sum(content.count(indicator) for indicator in indicators)
                
                if found_indicators == 0:
                    alignment_score -= 0.2
        
        return {
            "alignment_score": max(0.0, alignment_score),
            "missing_attributes": [attr for attr in voice_attributes if attr in attribute_indicators]
        }
    
    def _calculate_formality_score(self, text: str) -> float:
        """文章の敬語レベルスコアを計算"""
        formal_indicators = ["いたします", "申し上げます", "ございます", "していただく"]
        casual_indicators = ["です", "ます", "ですね", "ですよ"]
        
        formal_count = sum(text.count(indicator) for indicator in formal_indicators)
        casual_count = sum(text.count(indicator) for indicator in casual_indicators)
        
        total_indicators = formal_count + casual_count
        
        if total_indicators == 0:
            return 0.5  # 中性
        
        return formal_count / total_indicators
    
    def _get_expected_formality_score(self, formality_level: str) -> float:
        """期待される敬語レベルスコアを取得"""
        level_scores = {
            "カジュアル": 0.2,
            "やや丁寧": 0.5,
            "丁寧": 0.8,
            "非常に丁寧": 0.9
        }
        
        return level_scores.get(formality_level, 0.5)
    
    def _suggest_sentence_improvement(self, sentence: str, brand_guidelines: Optional[Dict[str, Any]]) -> str:
        """文章の改善案を提案"""
        improved = sentence
        
        # 基本的な改善パターン
        if brand_guidelines:
            dont_phrases = brand_guidelines.get("dont_phrases", [])
            
            for dont_phrase in dont_phrases:
                if dont_phrase in improved:
                    # 簡単な置換ルール
                    if dont_phrase == "絶対に":
                        improved = improved.replace("絶対に", "とても")
                    elif dont_phrase == "必ず":
                        improved = improved.replace("必ず", "ぜひ")
                    elif dont_phrase == "100%":
                        improved = improved.replace("100%", "しっかりと")
        
        return improved