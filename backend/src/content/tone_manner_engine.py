"""
Tone & Manner Engine
トンマナ一貫性チェック機能

機能:
1. 過去記事とのトンマナ比較
2. 文体・表現一貫性チェック
3. ブランドボイス適合性評価
4. 修正提案生成
"""

import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import hashlib
import json

from .content_management_system import ArticleContent, ToneManner


class ToneType(Enum):
    """トーンタイプ"""
    FRIENDLY = "親しみやすい"
    FORMAL = "フォーマル"
    PROFESSIONAL = "プロフェッショナル"
    CASUAL = "カジュアル"
    WARM = "温かい"
    AUTHORITATIVE = "権威的"


class FormalityLevel(Enum):
    """敬語レベル"""
    VERY_CASUAL = "とてもカジュアル"
    CASUAL = "カジュアル"
    NEUTRAL = "中立"
    POLITE = "丁寧"
    VERY_FORMAL = "とてもフォーマル"


class WritingStyle(Enum):
    """文体スタイル"""
    INFORMATIVE = "情報提供型"
    PROBLEM_SOLVING = "問題解決型"
    COMPARISON = "比較検討型"
    ENTERTAINMENT = "エンターテイメント型"
    QA_STYLE = "Q&A型"
    NARRATIVE = "物語型"
    ACADEMIC = "学術的"


class InconsistencyType(Enum):
    """不一致タイプ"""
    TONE_MISMATCH = "tone_mismatch"
    FORMALITY_MISMATCH = "formality_mismatch"
    WRITING_STYLE_MISMATCH = "writing_style_mismatch"
    TARGET_AUDIENCE_MISMATCH = "target_audience_mismatch"
    EXPRESSION_INCONSISTENCY = "expression_inconsistency"
    BRAND_VOICE_VIOLATION = "brand_voice_violation"


class RecommendationType(Enum):
    """修正提案タイプ"""
    TONE_ADJUSTMENT = "tone_adjustment"
    FORMALITY_ADJUSTMENT = "formality_adjustment"
    STYLE_ADJUSTMENT = "style_adjustment"
    EXPRESSION_MODERNIZATION = "expression_modernization"
    BRAND_ALIGNMENT = "brand_alignment"
    AUDIENCE_ALIGNMENT = "audience_alignment"


@dataclass
class BrandVoiceProfile:
    """ブランドボイスプロファイル"""
    brand_name: str
    preferred_tone: ToneType
    preferred_formality: FormalityLevel
    preferred_writing_style: WritingStyle
    target_audience: str
    brand_keywords: List[str]
    avoid_keywords: List[str]
    voice_characteristics: Dict[str, float]  # warmth, professionalism等のスコア
    style_guidelines: Dict[str, bool]
    
    def __post_init__(self):
        """バリデーション"""
        if not all([self.brand_name, self.target_audience]):
            raise ValueError("ブランド名とターゲット読者は必須です")


@dataclass
class ToneInconsistency:
    """トンマナ不一致情報"""
    inconsistency_type: InconsistencyType
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    location: str  # 文章内の位置
    suggested_fix: str
    confidence_score: float


@dataclass
class ToneMannerAnalysis:
    """トンマナ分析結果"""
    article_id: str
    consistency_score: float  # 0-1
    target_tone_match: bool
    formality_match: bool
    style_match: bool
    inconsistencies: List[ToneInconsistency]
    brand_voice_compliance: Optional[float] = None
    recommendations_summary: Optional[str] = None


@dataclass
class ToneRecommendation:
    """トンマナ修正提案"""
    recommendation_type: RecommendationType
    priority: str  # HIGH, MEDIUM, LOW
    original_text: str
    suggested_text: str
    explanation: str
    confidence_score: float


@dataclass
class ConsistencyReport:
    """一貫性レポート"""
    overall_consistency_score: float
    article_analyses: List[ToneMannerAnalysis]
    common_inconsistencies: List[InconsistencyType]
    tone_evolution_trend: Dict[str, Any]
    recommendations: List[ToneRecommendation]
    generated_at: datetime = field(default_factory=datetime.now)


class ToneMannerEngine:
    """
    トーン&マナーエンジン
    過去記事との一貫性チェックと修正提案を行う
    """
    
    def __init__(self):
        self.historical_articles: List[ArticleContent] = []
        self.brand_voice_profile: Optional[BrandVoiceProfile] = None
        self.tone_patterns: Dict[str, Any] = {}
        self.expression_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # 敬語・表現パターンの辞書
        self._formality_patterns = self._initialize_formality_patterns()
        self._tone_indicators = self._initialize_tone_indicators()
        self._expression_modernization_map = self._initialize_expression_modernization()
    
    # ===== 設定・管理機能 =====
    
    def set_brand_voice_profile(self, profile: BrandVoiceProfile):
        """ブランドボイスプロファイル設定"""
        self.brand_voice_profile = profile
    
    def get_brand_voice_profile(self) -> Optional[BrandVoiceProfile]:
        """ブランドボイスプロファイル取得"""
        return self.brand_voice_profile
    
    def add_historical_article(self, article: ArticleContent):
        """過去記事追加"""
        self.historical_articles.append(article)
        self._update_tone_patterns(article)
        self._update_expression_patterns(article)
    
    def get_historical_articles_count(self) -> int:
        """過去記事数取得"""
        return len(self.historical_articles)
    
    def get_historical_articles(self) -> List[ArticleContent]:
        """過去記事一覧取得"""
        return self.historical_articles.copy()
    
    # ===== メイン分析機能 =====
    
    def analyze_tone_manner(self, article: ArticleContent) -> ToneMannerAnalysis:
        """
        記事のトンマナ分析
        
        Args:
            article: 分析対象記事
            
        Returns:
            ToneMannerAnalysis: 分析結果
        """
        if not article.content or not article.title:
            return ToneMannerAnalysis(
                article_id=article.id,
                consistency_score=0.0,
                target_tone_match=False,
                formality_match=False,
                style_match=False,
                inconsistencies=[
                    ToneInconsistency(
                        inconsistency_type=InconsistencyType.EXPRESSION_INCONSISTENCY,
                        severity="HIGH",
                        description="コンテンツが空または不完全です",
                        location="全体",
                        suggested_fix="適切なコンテンツを提供してください",
                        confidence_score=1.0
                    )
                ]
            )
        
        inconsistencies = []
        
        # 過去記事との比較分析
        if self.historical_articles:
            tone_consistency = self._analyze_tone_consistency(article)
            formality_consistency = self._analyze_formality_consistency(article)
            style_consistency = self._analyze_style_consistency(article)
            
            # 不一致の検出
            if tone_consistency < 0.7:
                inconsistencies.append(ToneInconsistency(
                    inconsistency_type=InconsistencyType.TONE_MISMATCH,
                    severity="HIGH" if tone_consistency < 0.5 else "MEDIUM",
                    description=f"過去記事とのトーン一致度が低い ({tone_consistency:.2f})",
                    location="全体的な文体",
                    suggested_fix="過去記事のトーンに合わせた表現に調整することを推奨",
                    confidence_score=1.0 - tone_consistency
                ))
            
            if formality_consistency < 0.7:
                inconsistencies.append(ToneInconsistency(
                    inconsistency_type=InconsistencyType.FORMALITY_MISMATCH,
                    severity="HIGH" if formality_consistency < 0.5 else "MEDIUM",
                    description=f"過去記事との敬語レベル一致度が低い ({formality_consistency:.2f})",
                    location="敬語表現",
                    suggested_fix="一貫した敬語レベルに調整することを推奨",
                    confidence_score=1.0 - formality_consistency
                ))
            
            if style_consistency < 0.7:
                inconsistencies.append(ToneInconsistency(
                    inconsistency_type=InconsistencyType.WRITING_STYLE_MISMATCH,
                    severity="MEDIUM",
                    description=f"過去記事との文体一致度が低い ({style_consistency:.2f})",
                    location="文章構造",
                    suggested_fix="統一された文体スタイルに調整することを推奨",
                    confidence_score=1.0 - style_consistency
                ))
            
            overall_consistency = (tone_consistency + formality_consistency + style_consistency) / 3
        else:
            # 過去記事がない場合のデフォルト処理
            overall_consistency = 0.8  # 中程度の評価
            tone_consistency = formality_consistency = style_consistency = 0.8
        
        # ブランドボイス適合性チェック
        brand_compliance = None
        if self.brand_voice_profile:
            brand_compliance = self._evaluate_brand_voice_compliance(article)
            
            if brand_compliance < 0.7:
                inconsistencies.append(ToneInconsistency(
                    inconsistency_type=InconsistencyType.BRAND_VOICE_VIOLATION,
                    severity="HIGH" if brand_compliance < 0.5 else "MEDIUM",
                    description=f"ブランドボイス適合度が低い ({brand_compliance:.2f})",
                    location="全体的な表現",
                    suggested_fix="ブランドガイドラインに沿った表現に調整",
                    confidence_score=1.0 - brand_compliance
                ))
        
        return ToneMannerAnalysis(
            article_id=article.id,
            consistency_score=overall_consistency,
            target_tone_match=tone_consistency >= 0.7,
            formality_match=formality_consistency >= 0.7,
            style_match=style_consistency >= 0.7,
            inconsistencies=inconsistencies,
            brand_voice_compliance=brand_compliance,
            recommendations_summary=self._generate_recommendations_summary(inconsistencies)
        )
    
    def analyze_expression_patterns(self) -> Dict[str, Any]:
        """
        表現パターン分析
        
        Returns:
            Dict: 表現パターン分析結果
        """
        if not self.historical_articles:
            return {
                "common_expressions": [],
                "sentence_patterns": [],
                "emotional_words": []
            }
        
        all_content = " ".join([article.content for article in self.historical_articles])
        
        # 共通表現の抽出
        common_expressions = self._extract_common_expressions(all_content)
        
        # 文パターンの分析
        sentence_patterns = self._analyze_sentence_patterns(all_content)
        
        # 感情語の分析
        emotional_words = self._extract_emotional_words(all_content)
        
        return {
            "common_expressions": common_expressions,
            "sentence_patterns": sentence_patterns,
            "emotional_words": emotional_words,
            "analysis_date": datetime.now().isoformat()
        }
    
    def analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """
        文構造分析
        
        Args:
            text: 分析対象テキスト
            
        Returns:
            Dict: 文構造分析結果
        """
        sentences = self._split_sentences(text)
        
        if not sentences:
            return {
                "sentence_count": 0,
                "average_sentence_length": 0,
                "sentence_length_variance": 0
            }
        
        sentence_lengths = [len(sentence) for sentence in sentences]
        
        return {
            "sentence_count": len(sentences),
            "average_sentence_length": statistics.mean(sentence_lengths),
            "sentence_length_variance": statistics.variance(sentence_lengths) if len(sentence_lengths) > 1 else 0,
            "shortest_sentence": min(sentence_lengths),
            "longest_sentence": max(sentence_lengths)
        }
    
    # ===== ブランドボイス評価機能 =====
    
    def evaluate_brand_voice_compliance(self, article: ArticleContent) -> Dict[str, float]:
        """
        ブランドボイス適合性評価
        
        Args:
            article: 評価対象記事
            
        Returns:
            Dict: 適合性評価結果
        """
        if not self.brand_voice_profile:
            return {
                "overall_compliance_score": 0.5,
                "tone_compliance": 0.5,
                "formality_compliance": 0.5,
                "keyword_compliance": 0.5
            }
        
        # トーン適合性
        tone_compliance = self._evaluate_tone_compliance(article)
        
        # 敬語レベル適合性
        formality_compliance = self._evaluate_formality_compliance(article)
        
        # キーワード適合性
        keyword_compliance = self._evaluate_keyword_compliance(article)
        
        # 総合適合性
        overall_compliance = (tone_compliance + formality_compliance + keyword_compliance) / 3
        
        return {
            "overall_compliance_score": overall_compliance,
            "tone_compliance": tone_compliance,
            "formality_compliance": formality_compliance,
            "keyword_compliance": keyword_compliance
        }
    
    def analyze_brand_keyword_usage(self, content: str) -> Dict[str, Any]:
        """
        ブランドキーワード使用分析
        
        Args:
            content: 分析対象コンテンツ
            
        Returns:
            Dict: キーワード使用分析結果
        """
        if not self.brand_voice_profile:
            return {
                "used_brand_keywords": [],
                "avoided_keywords_found": [],
                "keyword_usage_score": 0.0
            }
        
        content_lower = content.lower()
        
        # ブランドキーワードの使用チェック
        used_brand_keywords = [
            keyword for keyword in self.brand_voice_profile.brand_keywords
            if keyword.lower() in content_lower
        ]
        
        # 避けるべきキーワードのチェック
        avoided_keywords_found = [
            keyword for keyword in self.brand_voice_profile.avoid_keywords
            if keyword.lower() in content_lower
        ]
        
        # スコア計算
        brand_keyword_score = len(used_brand_keywords) / max(len(self.brand_voice_profile.brand_keywords), 1)
        avoid_penalty = len(avoided_keywords_found) * 0.2
        keyword_usage_score = max(0, brand_keyword_score - avoid_penalty)
        
        return {
            "used_brand_keywords": used_brand_keywords,
            "avoided_keywords_found": avoided_keywords_found,
            "keyword_usage_score": keyword_usage_score,
            "brand_keyword_ratio": brand_keyword_score
        }
    
    # ===== 修正提案生成機能 =====
    
    def generate_tone_recommendations(self, article: ArticleContent) -> List[ToneRecommendation]:
        """
        トンマナ修正提案生成
        
        Args:
            article: 修正対象記事
            
        Returns:
            List[ToneRecommendation]: 修正提案リスト
        """
        recommendations = []
        
        analysis = self.analyze_tone_manner(article)
        
        for inconsistency in analysis.inconsistencies:
            if inconsistency.inconsistency_type == InconsistencyType.FORMALITY_MISMATCH:
                formal_recs = self._generate_formality_recommendations(article.content)
                recommendations.extend(formal_recs)
            
            elif inconsistency.inconsistency_type == InconsistencyType.TONE_MISMATCH:
                tone_recs = self._generate_tone_adjustment_recommendations(article.content)
                recommendations.extend(tone_recs)
            
            elif inconsistency.inconsistency_type == InconsistencyType.BRAND_VOICE_VIOLATION:
                brand_recs = self._generate_brand_alignment_recommendations(article.content)
                recommendations.extend(brand_recs)
        
        return recommendations[:5]  # 上位5つの提案を返す
    
    def suggest_formality_adjustments(self, text: str) -> List[str]:
        """
        敬語調整提案
        
        Args:
            text: 調整対象テキスト
            
        Returns:
            List[str]: 調整提案リスト
        """
        suggestions = []
        
        # 過度にフォーマルな表現をカジュアル化
        casual_text = text
        for formal_pattern, casual_replacement in self._formality_patterns["formal_to_casual"].items():
            if formal_pattern in text:
                casual_text = casual_text.replace(formal_pattern, casual_replacement)
        
        if casual_text != text:
            suggestions.append(casual_text)
        
        # その他の調整パターン
        if "申し上げます" in text:
            suggestions.append(text.replace("申し上げます", "します"))
        
        if "いたします" in text:
            suggestions.append(text.replace("いたします", "します"))
        
        return suggestions[:3]
    
    def suggest_expression_modernization(self, text: str) -> List[str]:
        """
        表現モダン化提案
        
        Args:
            text: モダン化対象テキスト
            
        Returns:
            List[str]: モダン化提案リスト
        """
        suggestions = []
        modern_text = text
        
        for old_expr, modern_expr in self._expression_modernization_map.items():
            if old_expr in text:
                modern_text = modern_text.replace(old_expr, modern_expr)
        
        if modern_text != text:
            suggestions.append(modern_text)
        
        return suggestions
    
    def suggest_audience_alignment(self, text: str) -> List[str]:
        """
        ターゲット読者向け調整提案
        
        Args:
            text: 調整対象テキスト
            
        Returns:
            List[str]: 調整提案リスト
        """
        suggestions = []
        
        # 専門用語の一般化
        accessible_text = text
        
        technical_terms = {
            "学名": "正式な名前（学名",
            "精油成分": "香りの成分",
            "ゲラニオール": "バラのような香り成分",
            "ネロール": "柑橘系の香り成分"
        }
        
        for technical, accessible in technical_terms.items():
            if technical in text:
                accessible_text = accessible_text.replace(technical, accessible)
        
        if accessible_text != text:
            suggestions.append(accessible_text)
        
        return suggestions
    
    # ===== 高度な分析機能 =====
    
    def generate_consistency_report(self, articles: List[ArticleContent]) -> ConsistencyReport:
        """
        一貫性レポート生成
        
        Args:
            articles: 分析対象記事リスト
            
        Returns:
            ConsistencyReport: 一貫性レポート
        """
        article_analyses = []
        all_inconsistencies = []
        
        for article in articles:
            analysis = self.analyze_tone_manner(article)
            article_analyses.append(analysis)
            all_inconsistencies.extend([inc.inconsistency_type for inc in analysis.inconsistencies])
        
        # 全体的な一貫性スコア
        overall_score = statistics.mean([analysis.consistency_score for analysis in article_analyses]) if article_analyses else 0.0
        
        # よくある不一致パターン
        common_inconsistencies = [
            inconsistency for inconsistency, count in Counter(all_inconsistencies).most_common(5)
        ]
        
        # トーン変化トレンド
        tone_trend = self._analyze_tone_evolution_trend(articles)
        
        # 全体的な推奨事項
        overall_recommendations = self._generate_overall_recommendations(article_analyses)
        
        return ConsistencyReport(
            overall_consistency_score=overall_score,
            article_analyses=article_analyses,
            common_inconsistencies=common_inconsistencies,
            tone_evolution_trend=tone_trend,
            recommendations=overall_recommendations
        )
    
    def track_tone_evolution(self) -> Dict[str, Any]:
        """
        トンマナ変化追跡
        
        Returns:
            Dict: トーン変化分析結果
        """
        if len(self.historical_articles) < 2:
            return {
                "tone_trends": [],
                "formality_trends": [],
                "style_changes": []
            }
        
        # 時系列でソート
        sorted_articles = sorted(self.historical_articles, key=lambda x: x.created_at)
        
        tone_trends = []
        formality_trends = []
        
        for article in sorted_articles:
            tone_trends.append({
                "date": article.created_at.isoformat(),
                "tone": article.tone_manner.tone,
                "formality": article.tone_manner.formality
            })
        
        return {
            "tone_trends": tone_trends,
            "formality_trends": formality_trends,
            "style_changes": self._detect_style_changes(sorted_articles)
        }
    
    def analyze_batch_tone_manner(self, articles: List[ArticleContent]) -> List[ToneMannerAnalysis]:
        """
        バッチトンマナ分析
        
        Args:
            articles: 分析対象記事リスト
            
        Returns:
            List[ToneMannerAnalysis]: 分析結果リスト
        """
        return [self.analyze_tone_manner(article) for article in articles]
    
    # ===== プライベートメソッド =====
    
    def _analyze_tone_consistency(self, article: ArticleContent) -> float:
        """トーン一貫性分析"""
        if not self.historical_articles:
            return 0.8
        
        target_tone = article.tone_manner.tone
        historical_tones = [a.tone_manner.tone for a in self.historical_articles]
        
        # 最も一般的なトーンとの一致度
        most_common_tone = Counter(historical_tones).most_common(1)[0][0]
        
        return 1.0 if target_tone == most_common_tone else 0.4
    
    def _analyze_formality_consistency(self, article: ArticleContent) -> float:
        """敬語レベル一貫性分析"""
        if not self.historical_articles:
            return 0.8
        
        target_formality = article.tone_manner.formality
        historical_formalities = [a.tone_manner.formality for a in self.historical_articles]
        
        most_common_formality = Counter(historical_formalities).most_common(1)[0][0]
        
        return 1.0 if target_formality == most_common_formality else 0.4
    
    def _analyze_style_consistency(self, article: ArticleContent) -> float:
        """文体一貫性分析"""
        if not self.historical_articles:
            return 0.8
        
        target_style = article.tone_manner.writing_style
        historical_styles = [a.tone_manner.writing_style for a in self.historical_articles]
        
        most_common_style = Counter(historical_styles).most_common(1)[0][0]
        
        return 1.0 if target_style == most_common_style else 0.6
    
    def _evaluate_brand_voice_compliance(self, article: ArticleContent) -> float:
        """ブランドボイス適合性評価"""
        if not self.brand_voice_profile:
            return 0.5
        
        compliance_report = self.evaluate_brand_voice_compliance(article)
        return compliance_report["overall_compliance_score"]
    
    def _evaluate_tone_compliance(self, article: ArticleContent) -> float:
        """トーン適合性評価"""
        if not self.brand_voice_profile:
            return 0.5
        
        article_tone = article.tone_manner.tone
        preferred_tone = self.brand_voice_profile.preferred_tone.value
        
        return 1.0 if article_tone == preferred_tone else 0.3
    
    def _evaluate_formality_compliance(self, article: ArticleContent) -> float:
        """敬語レベル適合性評価"""
        if not self.brand_voice_profile:
            return 0.5
        
        article_formality = article.tone_manner.formality
        preferred_formality = self.brand_voice_profile.preferred_formality.value
        
        return 1.0 if article_formality == preferred_formality else 0.3
    
    def _evaluate_keyword_compliance(self, article: ArticleContent) -> float:
        """キーワード適合性評価"""
        if not self.brand_voice_profile:
            return 0.5
        
        keyword_analysis = self.analyze_brand_keyword_usage(article.content)
        return keyword_analysis["keyword_usage_score"]
    
    def _generate_recommendations_summary(self, inconsistencies: List[ToneInconsistency]) -> str:
        """推奨事項サマリー生成"""
        if not inconsistencies:
            return "トンマナは一貫しています"
        
        high_priority = len([inc for inc in inconsistencies if inc.severity == "HIGH"])
        medium_priority = len([inc for inc in inconsistencies if inc.severity == "MEDIUM"])
        
        return f"高優先度: {high_priority}件, 中優先度: {medium_priority}件の調整が推奨されます"
    
    def _update_tone_patterns(self, article: ArticleContent):
        """トーンパターン更新"""
        tone_key = f"{article.tone_manner.tone}_{article.tone_manner.formality}"
        if tone_key not in self.tone_patterns:
            self.tone_patterns[tone_key] = []
        self.tone_patterns[tone_key].append(article.content)
    
    def _update_expression_patterns(self, article: ArticleContent):
        """表現パターン更新"""
        sentences = self._split_sentences(article.content)
        for sentence in sentences:
            if len(sentence) > 10:  # 短すぎる文は除外
                self.expression_patterns[article.tone_manner.tone].append(sentence)
    
    def _split_sentences(self, text: str) -> List[str]:
        """文分割"""
        sentences = re.split(r'[。！？]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_common_expressions(self, text: str) -> List[str]:
        """共通表現抽出"""
        # 簡易的な共通表現抽出
        patterns = [
            r'です[ね。]',
            r'ます[ね。]',
            r'でしょう[ね。]',
            r'ですよ[ね。]'
        ]
        
        common_expressions = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            common_expressions.extend(matches)
        
        return list(set(common_expressions))
    
    def _analyze_sentence_patterns(self, text: str) -> List[str]:
        """文パターン分析"""
        sentences = self._split_sentences(text)
        
        patterns = []
        for sentence in sentences[:5]:  # 最初の5文をサンプル
            if len(sentence) > 20:
                pattern = sentence[:20] + "..."
                patterns.append(pattern)
        
        return patterns
    
    def _extract_emotional_words(self, text: str) -> List[str]:
        """感情語抽出"""
        emotional_words = [
            "美しい", "素晴らしい", "癒し", "心地よい", "温かい",
            "優雅", "可憐", "魅力的", "感動", "喜び"
        ]
        
        found_words = []
        for word in emotional_words:
            if word in text:
                found_words.append(word)
        
        return found_words
    
    def _generate_formality_recommendations(self, content: str) -> List[ToneRecommendation]:
        """敬語調整推奨事項生成"""
        recommendations = []
        
        if "申し上げます" in content:
            recommendations.append(ToneRecommendation(
                recommendation_type=RecommendationType.FORMALITY_ADJUSTMENT,
                priority="MEDIUM",
                original_text="申し上げます",
                suggested_text="します",
                explanation="よりカジュアルな表現に調整",
                confidence_score=0.8
            ))
        
        return recommendations
    
    def _generate_tone_adjustment_recommendations(self, content: str) -> List[ToneRecommendation]:
        """トーン調整推奨事項生成"""
        recommendations = []
        
        if len(content) > 100:  # 簡易的なチェック
            recommendations.append(ToneRecommendation(
                recommendation_type=RecommendationType.TONE_ADJUSTMENT,
                priority="MEDIUM",
                original_text="全体的なトーン",
                suggested_text="より親しみやすい表現",
                explanation="過去記事との一貫性のため",
                confidence_score=0.7
            ))
        
        return recommendations
    
    def _generate_brand_alignment_recommendations(self, content: str) -> List[ToneRecommendation]:
        """ブランド整合性推奨事項生成"""
        recommendations = []
        
        if self.brand_voice_profile:
            for avoid_word in self.brand_voice_profile.avoid_keywords:
                if avoid_word in content:
                    recommendations.append(ToneRecommendation(
                        recommendation_type=RecommendationType.BRAND_ALIGNMENT,
                        priority="HIGH",
                        original_text=avoid_word,
                        suggested_text="より適切な表現",
                        explanation=f"ブランドガイドラインに従い「{avoid_word}」の使用を避ける",
                        confidence_score=0.9
                    ))
        
        return recommendations
    
    def _analyze_tone_evolution_trend(self, articles: List[ArticleContent]) -> Dict[str, Any]:
        """トーン変化トレンド分析"""
        if len(articles) < 2:
            return {}
        
        sorted_articles = sorted(articles, key=lambda x: x.created_at)
        
        tone_changes = []
        for i in range(1, len(sorted_articles)):
            prev_tone = sorted_articles[i-1].tone_manner.tone
            curr_tone = sorted_articles[i].tone_manner.tone
            
            if prev_tone != curr_tone:
                tone_changes.append({
                    "from": prev_tone,
                    "to": curr_tone,
                    "date": sorted_articles[i].created_at.isoformat()
                })
        
        return {
            "total_changes": len(tone_changes),
            "changes": tone_changes
        }
    
    def _generate_overall_recommendations(self, analyses: List[ToneMannerAnalysis]) -> List[ToneRecommendation]:
        """全体的な推奨事項生成"""
        recommendations = []
        
        # 一貫性スコアが低い記事の数をチェック
        low_consistency_count = len([a for a in analyses if a.consistency_score < 0.6])
        
        if low_consistency_count > len(analyses) * 0.3:  # 30%以上が低い一貫性
            recommendations.append(ToneRecommendation(
                recommendation_type=RecommendationType.TONE_ADJUSTMENT,
                priority="HIGH",
                original_text="全体的なトンマナ",
                suggested_text="統一されたトンマナ",
                explanation="サイト全体のトンマナ統一が必要",
                confidence_score=0.9
            ))
        
        return recommendations
    
    def _detect_style_changes(self, sorted_articles: List[ArticleContent]) -> List[Dict[str, Any]]:
        """文体変化検出"""
        changes = []
        
        for i in range(1, len(sorted_articles)):
            prev_style = sorted_articles[i-1].tone_manner.writing_style
            curr_style = sorted_articles[i].tone_manner.writing_style
            
            if prev_style != curr_style:
                changes.append({
                    "from_style": prev_style,
                    "to_style": curr_style,
                    "change_date": sorted_articles[i].created_at.isoformat()
                })
        
        return changes
    
    def _initialize_formality_patterns(self) -> Dict[str, Dict[str, str]]:
        """敬語パターン初期化"""
        return {
            "formal_to_casual": {
                "申し上げます": "します",
                "いたします": "します",
                "でございます": "です",
                "させていただきます": "します",
                "恐れ入りますが": "すみませんが",
            },
            "casual_to_formal": {
                "です": "でございます",
                "します": "いたします",
                "すみません": "申し訳ございません",
            }
        }
    
    def _initialize_tone_indicators(self) -> Dict[str, List[str]]:
        """トーン指標初期化"""
        return {
            "friendly": ["ですね", "ですよ", "でしょう", "かもしれません"],
            "formal": ["であります", "いたします", "でございます"],
            "casual": ["だよ", "だね", "かな", "みたい"]
        }
    
    def _initialize_expression_modernization(self) -> Dict[str, str]:
        """表現モダン化マップ初期化"""
        return {
            "でございます": "です",
            "かような": "このような",
            "拝見いたします": "見ます",
            "存じます": "思います",
            "承知いたしました": "わかりました"
        }


# エクスポート
__all__ = [
    'ToneMannerEngine',
    'ToneMannerAnalysis',
    'ConsistencyReport',
    'BrandVoiceProfile',
    'ToneRecommendation',
    'WritingStyle',
    'FormalityLevel',
    'ToneType',
    'InconsistencyType',
    'RecommendationType'
]