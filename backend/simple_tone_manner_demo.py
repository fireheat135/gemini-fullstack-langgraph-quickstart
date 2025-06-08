"""
Simple Tone & Manner Engine Demo
トンマナ一貫性チェック機能のシンプルデモ（依存関係なし）
"""

import re
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional
from collections import Counter


class ToneType(Enum):
    FRIENDLY = "親しみやすい"
    FORMAL = "フォーマル"
    CASUAL = "カジュアル"


class FormalityLevel(Enum):
    CASUAL = "カジュアル"
    POLITE = "丁寧" 
    VERY_FORMAL = "とてもフォーマル"


class WritingStyle(Enum):
    INFORMATIVE = "情報提供型"
    ACADEMIC = "学術的"


class InconsistencyType(Enum):
    TONE_MISMATCH = "tone_mismatch"
    FORMALITY_MISMATCH = "formality_mismatch"
    WRITING_STYLE_MISMATCH = "writing_style_mismatch"


@dataclass
class ToneManner:
    tone: str
    formality: str
    target_audience: str
    writing_style: str


@dataclass
class ArticleContent:
    id: str
    title: str
    content: str
    keyword: str
    tone_manner: ToneManner
    created_at: datetime


@dataclass
class BrandVoiceProfile:
    brand_name: str
    preferred_tone: ToneType
    preferred_formality: FormalityLevel
    preferred_writing_style: WritingStyle
    target_audience: str
    brand_keywords: List[str]
    avoid_keywords: List[str]
    voice_characteristics: Dict[str, float]
    style_guidelines: Dict[str, bool]


@dataclass
class ToneInconsistency:
    inconsistency_type: InconsistencyType
    severity: str
    description: str
    location: str
    suggested_fix: str
    confidence_score: float


@dataclass
class ToneMannerAnalysis:
    article_id: str
    consistency_score: float
    target_tone_match: bool
    formality_match: bool
    style_match: bool
    inconsistencies: List[ToneInconsistency]
    brand_voice_compliance: Optional[float] = None


class SimpleToneMannerEngine:
    """Simplified Tone & Manner Engine for demonstration"""
    
    def __init__(self):
        self.historical_articles: List[ArticleContent] = []
        self.brand_voice_profile: Optional[BrandVoiceProfile] = None
    
    def set_brand_voice_profile(self, profile: BrandVoiceProfile):
        """ブランドボイスプロファイル設定"""
        self.brand_voice_profile = profile
    
    def get_brand_voice_profile(self) -> Optional[BrandVoiceProfile]:
        """ブランドボイスプロファイル取得"""
        return self.brand_voice_profile
    
    def add_historical_article(self, article: ArticleContent):
        """過去記事追加"""
        self.historical_articles.append(article)
    
    def get_historical_articles_count(self) -> int:
        """過去記事数取得"""
        return len(self.historical_articles)
    
    def analyze_tone_manner(self, article: ArticleContent) -> ToneMannerAnalysis:
        """トンマナ分析"""
        if not article.content:
            return ToneMannerAnalysis(
                article_id=article.id,
                consistency_score=0.0,
                target_tone_match=False,
                formality_match=False,
                style_match=False,
                inconsistencies=[],
                brand_voice_compliance=0.0
            )
        
        inconsistencies = []
        
        # 過去記事との比較
        if self.historical_articles:
            tone_consistency = self._analyze_tone_consistency(article)
            formality_consistency = self._analyze_formality_consistency(article)  
            style_consistency = self._analyze_style_consistency(article)
            
            # 不一致検出
            if tone_consistency < 0.7:
                inconsistencies.append(ToneInconsistency(
                    inconsistency_type=InconsistencyType.TONE_MISMATCH,
                    severity="HIGH" if tone_consistency < 0.5 else "MEDIUM",
                    description=f"過去記事とのトーン一致度が低い ({tone_consistency:.2f})",
                    location="全体的な文体",
                    suggested_fix="過去記事のトーンに合わせた表現に調整",
                    confidence_score=1.0 - tone_consistency
                ))
            
            if formality_consistency < 0.7:
                inconsistencies.append(ToneInconsistency(
                    inconsistency_type=InconsistencyType.FORMALITY_MISMATCH,
                    severity="HIGH" if formality_consistency < 0.5 else "MEDIUM",
                    description=f"過去記事との敬語レベル一致度が低い ({formality_consistency:.2f})",
                    location="敬語表現",
                    suggested_fix="一貫した敬語レベルに調整",
                    confidence_score=1.0 - formality_consistency
                ))
            
            overall_consistency = (tone_consistency + formality_consistency + style_consistency) / 3
        else:
            overall_consistency = 0.8
            tone_consistency = formality_consistency = style_consistency = 0.8
        
        # ブランドボイス適合性
        brand_compliance = None
        if self.brand_voice_profile:
            brand_compliance = self._evaluate_brand_voice_compliance(article)
        
        return ToneMannerAnalysis(
            article_id=article.id,
            consistency_score=overall_consistency,
            target_tone_match=tone_consistency >= 0.7,
            formality_match=formality_consistency >= 0.7,
            style_match=style_consistency >= 0.7,
            inconsistencies=inconsistencies,
            brand_voice_compliance=brand_compliance
        )
    
    def evaluate_brand_voice_compliance(self, article: ArticleContent) -> Dict[str, float]:
        """ブランドボイス適合性評価"""
        if not self.brand_voice_profile:
            return {"overall_compliance_score": 0.5, "tone_compliance": 0.5, "formality_compliance": 0.5, "keyword_compliance": 0.5}
        
        tone_compliance = 1.0 if article.tone_manner.tone == self.brand_voice_profile.preferred_tone.value else 0.3
        formality_compliance = 1.0 if article.tone_manner.formality == self.brand_voice_profile.preferred_formality.value else 0.3
        keyword_compliance = self._calculate_keyword_compliance(article.content)
        
        overall_compliance = (tone_compliance + formality_compliance + keyword_compliance) / 3
        
        return {
            "overall_compliance_score": overall_compliance,
            "tone_compliance": tone_compliance,
            "formality_compliance": formality_compliance,
            "keyword_compliance": keyword_compliance
        }
    
    def analyze_brand_keyword_usage(self, content: str) -> Dict[str, Any]:
        """ブランドキーワード使用分析"""
        if not self.brand_voice_profile:
            return {"used_brand_keywords": [], "avoided_keywords_found": [], "keyword_usage_score": 0.0}
        
        content_lower = content.lower()
        
        used_brand_keywords = [kw for kw in self.brand_voice_profile.brand_keywords if kw.lower() in content_lower]
        avoided_keywords_found = [kw for kw in self.brand_voice_profile.avoid_keywords if kw.lower() in content_lower]
        
        brand_keyword_score = len(used_brand_keywords) / max(len(self.brand_voice_profile.brand_keywords), 1)
        avoid_penalty = len(avoided_keywords_found) * 0.2
        keyword_usage_score = max(0, brand_keyword_score - avoid_penalty)
        
        return {
            "used_brand_keywords": used_brand_keywords,
            "avoided_keywords_found": avoided_keywords_found,
            "keyword_usage_score": keyword_usage_score
        }
    
    def suggest_formality_adjustments(self, text: str) -> List[str]:
        """敬語調整提案"""
        suggestions = []
        
        formal_to_casual = {
            "申し上げます": "します",
            "いたします": "します",
            "でございます": "です",
            "させていただきます": "します"
        }
        
        casual_text = text
        for formal, casual in formal_to_casual.items():
            if formal in text:
                casual_text = casual_text.replace(formal, casual)
        
        if casual_text != text:
            suggestions.append(casual_text)
        
        return suggestions
    
    def suggest_expression_modernization(self, text: str) -> List[str]:
        """表現モダン化提案"""
        suggestions = []
        
        modernization_map = {
            "でございます": "です",
            "かような": "このような",
            "拝見いたします": "見ます",
            "存じます": "思います"
        }
        
        modern_text = text
        for old_expr, modern_expr in modernization_map.items():
            if old_expr in text:
                modern_text = modern_text.replace(old_expr, modern_expr)
        
        if modern_text != text:
            suggestions.append(modern_text)
        
        return suggestions
    
    def analyze_expression_patterns(self) -> Dict[str, Any]:
        """表現パターン分析"""
        if not self.historical_articles:
            return {"common_expressions": [], "sentence_patterns": [], "emotional_words": []}
        
        all_content = " ".join([article.content for article in self.historical_articles])
        
        # 共通表現の抽出
        common_expressions = []
        expression_patterns = [r'ですね', r'ますね', r'でしょう', r'ですよ']
        for pattern in expression_patterns:
            if re.search(pattern, all_content):
                common_expressions.append(pattern.replace('\\', ''))
        
        # 感情語の抽出
        emotional_words = []
        emotion_keywords = ["美しい", "素晴らしい", "癒し", "心地よい", "温かい", "優雅", "可憐", "魅力的"]
        for word in emotion_keywords:
            if word in all_content:
                emotional_words.append(word)
        
        return {
            "common_expressions": common_expressions,
            "sentence_patterns": [],
            "emotional_words": emotional_words
        }
    
    def analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """文構造分析"""
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {"sentence_count": 0, "average_sentence_length": 0, "shortest_sentence": 0, "longest_sentence": 0}
        
        sentence_lengths = [len(sentence) for sentence in sentences]
        
        return {
            "sentence_count": len(sentences),
            "average_sentence_length": statistics.mean(sentence_lengths),
            "shortest_sentence": min(sentence_lengths),
            "longest_sentence": max(sentence_lengths)
        }
    
    def track_tone_evolution(self) -> Dict[str, Any]:
        """トーン変化追跡"""
        if len(self.historical_articles) < 2:
            return {"tone_trends": [], "formality_trends": [], "style_changes": []}
        
        sorted_articles = sorted(self.historical_articles, key=lambda x: x.created_at)
        
        tone_trends = []
        for article in sorted_articles:
            tone_trends.append({
                "date": article.created_at.isoformat(),
                "tone": article.tone_manner.tone,
                "formality": article.tone_manner.formality
            })
        
        style_changes = []
        for i in range(1, len(sorted_articles)):
            prev_style = sorted_articles[i-1].tone_manner.writing_style
            curr_style = sorted_articles[i].tone_manner.writing_style
            
            if prev_style != curr_style:
                style_changes.append({
                    "from_style": prev_style,
                    "to_style": curr_style,
                    "change_date": sorted_articles[i].created_at.isoformat()
                })
        
        return {
            "tone_trends": tone_trends,
            "formality_trends": [],
            "style_changes": style_changes
        }
    
    def _analyze_tone_consistency(self, article: ArticleContent) -> float:
        """トーン一貫性分析"""
        if not self.historical_articles:
            return 0.8
        
        target_tone = article.tone_manner.tone
        historical_tones = [a.tone_manner.tone for a in self.historical_articles]
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
        compliance_report = self.evaluate_brand_voice_compliance(article)
        return compliance_report["overall_compliance_score"]
    
    def _calculate_keyword_compliance(self, content: str) -> float:
        """キーワード適合性計算"""
        keyword_analysis = self.analyze_brand_keyword_usage(content)
        return keyword_analysis["keyword_usage_score"]


def main():
    """デモンストレーション実行"""
    print("🎨 Tone & Manner Engine Demo - Phase 5 Implementation")
    print("=" * 60)
    
    # Engine初期化
    tone_engine = SimpleToneMannerEngine()
    print("✅ Tone & Manner Engine initialized")
    
    # ブランドボイスプロファイル設定
    brand_profile = BrandVoiceProfile(
        brand_name="花の専門サイト",
        preferred_tone=ToneType.FRIENDLY,
        preferred_formality=FormalityLevel.CASUAL,
        preferred_writing_style=WritingStyle.INFORMATIVE,
        target_audience="花好きの女性（20-50代）",
        brand_keywords=["美しい", "癒し", "自然", "優雅", "心地よい"],
        avoid_keywords=["難しい", "複雑", "専門的すぎる"],
        voice_characteristics={
            "warmth": 0.8,
            "professionalism": 0.6,
            "friendliness": 0.9,
            "expertise": 0.7,
            "accessibility": 0.8
        },
        style_guidelines={
            "use_honorifics": False,
            "use_casual_expressions": True,
            "include_seasonal_references": True,
            "focus_on_emotions": True
        }
    )
    
    tone_engine.set_brand_voice_profile(brand_profile)
    print("✅ Brand voice profile configured")
    
    # 一貫したトンマナの過去記事を追加
    consistent_tone = ToneManner(
        tone="親しみやすい",
        formality="カジュアル",
        target_audience="花好きの女性",
        writing_style="情報提供型"
    )
    
    historical_articles = [
        ArticleContent(
            id="hist_1",
            title="1月の誕生花「カーネーション」で心も温まる冬の彩り",
            content="寒い冬にも美しく咲くカーネーションは、1月の誕生花として多くの人に愛されています。その温かみのある色合いは、見る人の心を優しく包み込んでくれますね。お部屋に飾ると、一気に明るい雰囲気になりますよ。",
            keyword="1月 誕生花 カーネーション",
            tone_manner=consistent_tone,
            created_at=datetime.now() - timedelta(days=30)
        ),
        ArticleContent(
            id="hist_2",
            title="2月の誕生花「プリムラ」が運ぶ春の便り",
            content="可憐なプリムラは、2月の代表的な誕生花として親しまれています。小さな花びらが集まって咲く姿は、まるで春の妖精のようですね。色とりどりの花色は、まだ寒い季節に心温まる癒しを与えてくれます。",
            keyword="2月 誕生花 プリムラ",
            tone_manner=consistent_tone,
            created_at=datetime.now() - timedelta(days=20)
        ),
        ArticleContent(
            id="hist_3",
            title="3月の誕生花「桜」で感じる日本の美しさ",
            content="日本人にとって特別な花、桜。3月の誕生花としても知られ、その美しさは多くの人の心を魅了し続けています。淡いピンクの花びらが舞い散る様子は、日本ならではの優雅な美意識を感じさせてくれますね。",
            keyword="3月 誕生花 桜",
            tone_manner=consistent_tone,
            created_at=datetime.now() - timedelta(days=10)
        )
    ]
    
    print("\n📚 過去記事追加テスト")
    for article in historical_articles:
        tone_engine.add_historical_article(article)
    print(f"   追加完了: {tone_engine.get_historical_articles_count()}件の過去記事")
    
    # ===== 一貫した記事の分析 =====
    print("\n✅ 一貫したトンマナ記事の分析テスト")
    consistent_article = ArticleContent(
        id="consistent_test",
        title="4月の誕生花「桜草」の愛らしい魅力",
        content="春らしい桜草は、4月の誕生花として親しまれています。小さくて可愛らしい花は、見ているだけで心が癒されますね。ガーデニング初心者の方でも育てやすく、春のお庭を美しく彩ってくれますよ。",
        keyword="4月 誕生花 桜草",
        tone_manner=consistent_tone,
        created_at=datetime.now()
    )
    
    analysis = tone_engine.analyze_tone_manner(consistent_article)
    print(f"   一貫性スコア: {analysis.consistency_score:.3f}")
    print(f"   トーン一致: {analysis.target_tone_match}")
    print(f"   敬語レベル一致: {analysis.formality_match}")
    print(f"   文体一致: {analysis.style_match}")
    print(f"   不一致件数: {len(analysis.inconsistencies)}")
    
    # ===== 不一致記事の分析 =====
    print("\n⚠️ 不一致トンマナ記事の分析テスト")
    inconsistent_article = ArticleContent(
        id="inconsistent_test",
        title="誕生花に関する学術的考察",
        content="誕生花の概念につきましては、その起源を19世紀のヨーロッパに求めることができます。植物学的観点から申し上げますと、各月に割り当てられた花卉は、その時期の気候条件及び栽培適性を考慮して選定されております。これらの複雑で難しい専門的要因を理解することは極めて困難であります。",
        keyword="誕生花 学術 研究",
        tone_manner=ToneManner(
            tone="フォーマル",
            formality="非常に丁寧",
            target_audience="研究者・専門家",
            writing_style="学術的"
        ),
        created_at=datetime.now()
    )
    
    inconsistent_analysis = tone_engine.analyze_tone_manner(inconsistent_article)
    print(f"   一貫性スコア: {inconsistent_analysis.consistency_score:.3f}")
    print(f"   トーン一致: {inconsistent_analysis.target_tone_match}")
    print(f"   敬語レベル一致: {inconsistent_analysis.formality_match}")
    print(f"   文体一致: {inconsistent_analysis.style_match}")
    print(f"   不一致件数: {len(inconsistent_analysis.inconsistencies)}")
    
    # 不一致詳細の表示
    print("   検出された不一致:")
    for inc in inconsistent_analysis.inconsistencies:
        print(f"     - {inc.severity}: {inc.description}")
    
    # ===== ブランドボイス適合性評価 =====
    print("\n🎯 ブランドボイス適合性評価テスト")
    brand_compliance = tone_engine.evaluate_brand_voice_compliance(consistent_article)
    print(f"   総合適合度: {brand_compliance['overall_compliance_score']:.3f}")
    print(f"   トーン適合度: {brand_compliance['tone_compliance']:.3f}")
    print(f"   敬語レベル適合度: {brand_compliance['formality_compliance']:.3f}")
    print(f"   キーワード適合度: {brand_compliance['keyword_compliance']:.3f}")
    
    # ブランドキーワード使用分析
    print("\n🔍 ブランドキーワード使用分析テスト")
    keyword_usage = tone_engine.analyze_brand_keyword_usage(consistent_article.content)
    print(f"   使用されたブランドキーワード: {keyword_usage['used_brand_keywords']}")
    print(f"   避けるべきキーワード検出: {keyword_usage['avoided_keywords_found']}")
    print(f"   キーワード使用スコア: {keyword_usage['keyword_usage_score']:.3f}")
    
    # 問題のある記事でのキーワード分析
    problematic_keyword_usage = tone_engine.analyze_brand_keyword_usage(inconsistent_article.content)
    print(f"   問題記事 - 避けるべきキーワード: {problematic_keyword_usage['avoided_keywords_found']}")
    
    # ===== 敬語調整提案 =====
    print("\n🔄 敬語調整提案テスト")
    formal_text = "申し上げますが、この花につきましてはご説明させていただきます"
    formality_suggestions = tone_engine.suggest_formality_adjustments(formal_text)
    print(f"   元の文章: {formal_text}")
    print("   調整提案:")
    for i, suggestion in enumerate(formality_suggestions, 1):
        print(f"     {i}. {suggestion}")
    
    # ===== 表現モダン化提案 =====
    print("\n🆕 表現モダン化提案テスト")
    old_text = "かような美しき花を拝見いたしますと、心が洗われる思いでございます"
    modern_suggestions = tone_engine.suggest_expression_modernization(old_text)
    print(f"   元の文章: {old_text}")
    print("   モダン化提案:")
    for i, suggestion in enumerate(modern_suggestions, 1):
        print(f"     {i}. {suggestion}")
    
    # ===== 表現パターン分析 =====
    print("\n📊 表現パターン分析テスト")
    expression_patterns = tone_engine.analyze_expression_patterns()
    print(f"   共通表現: {expression_patterns['common_expressions']}")
    print(f"   感情語: {expression_patterns['emotional_words']}")
    
    # ===== 文構造分析 =====
    print("\n📝 文構造分析テスト")
    sentence_analysis = tone_engine.analyze_sentence_structure(consistent_article.content)
    print(f"   文数: {sentence_analysis['sentence_count']}")
    print(f"   平均文長: {sentence_analysis['average_sentence_length']:.1f}文字")
    print(f"   最短文: {sentence_analysis['shortest_sentence']}文字")
    print(f"   最長文: {sentence_analysis['longest_sentence']}文字")
    
    # ===== トーン変化追跡 =====
    print("\n📈 トーン変化追跡テスト")
    tone_evolution = tone_engine.track_tone_evolution()
    print(f"   トーントレンド記録: {len(tone_evolution['tone_trends'])}件")
    print(f"   文体変化: {len(tone_evolution['style_changes'])}件")
    if tone_evolution['tone_trends']:
        latest_trend = tone_evolution['tone_trends'][-1]
        print(f"   最新のトーン: {latest_trend['tone']} ({latest_trend['formality']})")
    
    print("\n🎉 Tone & Manner Engine - 全機能実装完了!")
    print("=" * 60)
    print("✅ 過去記事とのトンマナ比較")
    print("✅ 文体・表現一貫性チェック")
    print("✅ ブランドボイス適合性評価")
    print("✅ 修正提案生成")
    print("✅ 敬語調整提案")
    print("✅ 表現モダン化提案")
    print("✅ 表現パターン分析")
    print("✅ 文構造分析")
    print("✅ トーン変化追跡")


if __name__ == "__main__":
    main()