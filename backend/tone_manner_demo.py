"""
Tone & Manner Engine Demo
トンマナ一貫性チェック機能のデモンストレーション
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from content.tone_manner_engine import (
        ToneMannerEngine,
        BrandVoiceProfile,
        ToneType,
        FormalityLevel,
        WritingStyle
    )
    from content.content_management_system import (
        ArticleContent,
        ToneManner
    )
    
    print("🎨 Tone & Manner Engine Demo - Phase 5 Implementation")
    print("=" * 60)
    
    # Tone & Manner Engine初期化
    tone_engine = ToneMannerEngine()
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
            content="可憐なプリムラは、2月の代表的な誕生花として親しまれています。小さな花びらが集まって咲く姿は、まるで春の妖精のようですね。色とりどりの花色は、まだ寒い季節に心温まる彩りを与えてくれます。",
            keyword="2月 誕生花 プリムラ",
            tone_manner=consistent_tone,
            created_at=datetime.now() - timedelta(days=20)
        ),
        ArticleContent(
            id="hist_3",
            title="3月の誕生花「桜」で感じる日本の美しさ",
            content="日本人にとって特別な花、桜。3月の誕生花としても知られ、その美しさは多くの人の心を魅了し続けています。淡いピンクの花びらが舞い散る様子は、日本ならではの美意識を感じさせてくれますね。",
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
        content="誕生花の概念につきましては、その起源を19世紀のヨーロッパに求めることができます。植物学的観点から申し上げますと、各月に割り当てられた花卉は、その時期の気候条件及び栽培適性を考慮して選定されております。これらの複雑な専門的要因を理解することは極めて困難であります。",
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
    
    # ===== 修正提案生成 =====
    print("\n💡 修正提案生成テスト")
    recommendations = tone_engine.generate_tone_recommendations(inconsistent_article)
    print(f"   生成された提案: {len(recommendations)}件")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"     {i}. {rec.priority}優先度: {rec.explanation}")
    
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
    print(f"   共通表現: {expression_patterns['common_expressions'][:3]}")
    print(f"   感情語: {expression_patterns['emotional_words'][:5]}")
    
    # ===== 文構造分析 =====
    print("\n📝 文構造分析テスト")
    sentence_analysis = tone_engine.analyze_sentence_structure(consistent_article.content)
    print(f"   文数: {sentence_analysis['sentence_count']}")
    print(f"   平均文長: {sentence_analysis['average_sentence_length']:.1f}文字")
    print(f"   最短文: {sentence_analysis['shortest_sentence']}文字")
    print(f"   最長文: {sentence_analysis['longest_sentence']}文字")
    
    # ===== 一貫性レポート生成 =====
    print("\n📋 一貫性レポート生成テスト")
    all_articles = historical_articles + [consistent_article, inconsistent_article]
    consistency_report = tone_engine.generate_consistency_report(all_articles)
    print(f"   全体一貫性スコア: {consistency_report.overall_consistency_score:.3f}")
    print(f"   分析記事数: {len(consistency_report.article_analyses)}")
    print(f"   よくある不一致: {[inc.value for inc in consistency_report.common_inconsistencies[:3]]}")
    print(f"   総合推奨事項: {len(consistency_report.recommendations)}件")
    
    # ===== トーン変化追跡 =====
    print("\n📈 トーン変化追跡テスト")
    tone_evolution = tone_engine.track_tone_evolution()
    print(f"   トーントレンド記録: {len(tone_evolution['tone_trends'])}件")
    print(f"   文体変化: {len(tone_evolution['style_changes'])}件")
    
    print("\n🎉 Tone & Manner Engine - 全機能実装完了!")
    print("=" * 60)
    print("✅ 過去記事とのトンマナ比較")
    print("✅ 文体・表現一貫性チェック")
    print("✅ ブランドボイス適合性評価")
    print("✅ 修正提案生成")
    print("✅ 敬語調整提案")
    print("✅ 表現モダン化提案")
    print("✅ 一貫性レポート生成")
    print("✅ トーン変化追跡")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Missing dependencies - this is expected in test environment")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()