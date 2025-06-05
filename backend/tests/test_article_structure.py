"""
TDD: Article Structure & Tone Planning Tests
記事構成・トンマナ提案機能のテスト
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock


class TestPersonaAnalyzer:
    """ペルソナ分析機能のテスト"""

    @pytest.mark.asyncio
    async def test_analyze_target_persona_for_birth_flower_gift(self):
        """誕生花ギフトのターゲットペルソナを分析できることを確認"""
        # Arrange
        keyword = "3月 誕生花 プレゼント"
        search_intent = "商用"
        
        # Act
        from src.content.persona_analyzer import PersonaAnalyzer
        analyzer = PersonaAnalyzer()
        persona = await analyzer.analyze_target_persona(keyword, search_intent)
        
        # Assert
        assert "demographics" in persona
        assert "psychographics" in persona
        assert "pain_points" in persona
        assert "goals" in persona
        assert "preferred_content_style" in persona
        
        # 誕生花プレゼント関連の特徴
        assert "プレゼント選び" in str(persona["pain_points"])
        assert persona["demographics"]["age_range"]

    @pytest.mark.asyncio
    async def test_generate_persona_variations(self):
        """複数のペルソナバリエーションを生成できることを確認"""
        # Arrange
        base_keyword = "誕生花 花言葉"
        
        # Act
        from src.content.persona_analyzer import PersonaAnalyzer
        analyzer = PersonaAnalyzer()
        persona_variations = await analyzer.generate_persona_variations(base_keyword)
        
        # Assert
        assert len(persona_variations) >= 3
        persona_types = [p["persona_type"] for p in persona_variations]
        assert "ギフト購入者" in persona_types
        assert "花好き愛好家" in persona_types
        assert "一般学習者" in persona_types

    def test_extract_persona_from_keyword_analysis(self):
        """キーワード分析結果からペルソナを抽出できることを確認"""
        # Arrange
        keyword_analysis = {
            "primary_keyword": "母の日 誕生花",
            "search_intent": "商用",
            "related_keywords": [
                "母の日 プレゼント", "カーネーション 花言葉", 
                "花束 通販", "母の日 ギフト"
            ],
            "difficulty_scores": {"母の日 誕生花": 45}
        }
        
        # Act
        from src.content.persona_analyzer import PersonaAnalyzer
        analyzer = PersonaAnalyzer()
        persona_insights = analyzer.extract_persona_from_keywords(keyword_analysis)
        
        # Assert
        assert "target_audience" in persona_insights
        assert "search_behavior" in persona_insights
        assert "content_preferences" in persona_insights
        assert "購買意欲" in persona_insights["search_behavior"]


class TestArticlePlanningEngine:
    """記事企画エンジンのテスト"""

    @pytest.mark.asyncio
    async def test_generate_four_article_concepts(self):
        """4パターンの記事企画を生成できることを確認"""
        # Arrange
        topic_info = {
            "month": 6,
            "primary_keyword": "6月 誕生花",
            "target_persona": "プレゼント購入者",
            "search_intent": "商用"
        }
        
        # Act
        from src.content.article_planning_engine import ArticlePlanningEngine
        engine = ArticlePlanningEngine()
        article_concepts = await engine.generate_four_concepts(topic_info)
        
        # Assert
        assert len(article_concepts) == 4
        concept_types = [concept["type"] for concept in article_concepts]
        assert "情報提供型" in concept_types
        assert "問題解決型" in concept_types
        assert "比較検討型" in concept_types
        assert "エンターテイメント型" in concept_types
        
        # 各企画に必要な要素が含まれているか
        for concept in article_concepts:
            assert "title" in concept
            assert "concept_summary" in concept
            assert "target_emotion" in concept
            assert "expected_outcome" in concept

    @pytest.mark.asyncio
    async def test_evaluate_concept_feasibility(self):
        """企画の実現可能性を評価できることを確認"""
        # Arrange
        concept = {
            "type": "情報提供型",
            "title": "6月の誕生花バラとアジサイ完全ガイド",
            "target_keyword": "6月 誕生花",
            "estimated_word_count": 3000
        }
        
        # Act
        from src.content.article_planning_engine import ArticlePlanningEngine
        engine = ArticlePlanningEngine()
        feasibility = await engine.evaluate_concept_feasibility(concept)
        
        # Assert
        assert "feasibility_score" in feasibility
        assert "resource_requirements" in feasibility
        assert "roi_prediction" in feasibility
        assert "risk_factors" in feasibility
        assert 0 <= feasibility["feasibility_score"] <= 100

    @pytest.mark.asyncio
    async def test_birth_flower_specific_concepts(self):
        """誕生花特化の企画コンセプトを生成できることを確認"""
        # Arrange
        month_data = {
            "month": 12,
            "flowers": ["ポインセチア", "カトレア"],
            "season": "冬",
            "events": ["クリスマス", "年末"]
        }
        
        # Act
        from src.content.article_planning_engine import ArticlePlanningEngine
        engine = ArticlePlanningEngine()
        seasonal_concepts = await engine.generate_seasonal_concepts(month_data)
        
        # Assert
        assert len(seasonal_concepts) > 0
        for concept in seasonal_concepts:
            assert "seasonal_angle" in concept
            assert any(flower in concept["title"] for flower in month_data["flowers"])
            assert any(event in concept["seasonal_angle"] for event in month_data["events"])


class TestToneMannnerEngine:
    """トーン&マナー設定エンジンのテスト"""

    def test_define_tone_variations(self):
        """異なるトーンバリエーションを定義できることを確認"""
        # Arrange
        target_audience = "30代女性、プレゼント購入検討中"
        content_purpose = "誕生花選びの支援"
        
        # Act
        from src.content.tone_manner_engine import ToneMannnerEngine
        engine = ToneMannnerEngine()
        tone_options = engine.generate_tone_variations(target_audience, content_purpose)
        
        # Assert
        assert len(tone_options) >= 4
        tone_types = [option["tone_type"] for option in tone_options]
        assert "friendly_casual" in tone_types
        assert "professional_helpful" in tone_types
        assert "warm_emotional" in tone_types
        assert "expert_authoritative" in tone_types
        
        for option in tone_options:
            assert "description" in option
            assert "sample_phrases" in option
            assert "writing_guidelines" in option

    def test_customize_tone_for_birth_flower_content(self):
        """誕生花コンテンツ用のトーンカスタマイズを確認"""
        # Arrange
        base_tone = "friendly_casual"
        flower_context = {
            "flowers": ["チューリップ", "スイートアリッサム"],
            "occasion": "春のプレゼント",
            "emotion": "喜び、新しい始まり"
        }
        
        # Act
        from src.content.tone_manner_engine import ToneMannnerEngine
        engine = ToneMannnerEngine()
        customized_tone = engine.customize_for_flower_content(base_tone, flower_context)
        
        # Assert
        assert "flower_specific_language" in customized_tone
        assert "emotional_expressions" in customized_tone
        assert "seasonal_references" in customized_tone
        assert "禁止表現" in customized_tone
        
        # 花特有の表現が含まれているか
        assert any("春" in expr for expr in customized_tone["seasonal_references"])

    def test_generate_brand_voice_guidelines(self):
        """ブランドボイスガイドラインを生成できることを確認"""
        # Arrange
        brand_characteristics = {
            "brand_personality": "温かい、信頼できる、専門的",
            "target_relationship": "友人のようなアドバイザー",
            "expertise_level": "中級者向け"
        }
        
        # Act
        from src.content.tone_manner_engine import ToneMannnerEngine
        engine = ToneMannnerEngine()
        guidelines = engine.generate_brand_voice_guidelines(brand_characteristics)
        
        # Assert
        assert "voice_attributes" in guidelines
        assert "do_phrases" in guidelines
        assert "dont_phrases" in guidelines
        assert "consistency_rules" in guidelines
        
        # 専門性と親しみやすさのバランス
        assert len(guidelines["do_phrases"]) > 0
        assert len(guidelines["dont_phrases"]) > 0


class TestContentStructureTemplate:
    """コンテンツ構造テンプレートのテスト"""

    @pytest.mark.asyncio
    async def test_generate_article_outline_template(self):
        """記事アウトラインテンプレートを生成できることを確認"""
        # Arrange
        article_concept = {
            "type": "情報提供型",
            "title": "5月の誕生花スズランの魅力と花言葉",
            "target_word_count": 3000,
            "target_audience": "花に興味がある一般読者"
        }
        
        # Act
        from src.content.content_structure_template import ContentStructureTemplate
        template = ContentStructureTemplate()
        outline = await template.generate_outline(article_concept)
        
        # Assert
        assert "introduction" in outline
        assert "main_sections" in outline
        assert "conclusion" in outline
        assert "cta_suggestions" in outline
        
        # 誕生花記事特有の構造
        main_sections = outline["main_sections"]
        section_titles = [section["title"] for section in main_sections]
        assert any("花言葉" in title for title in section_titles)
        assert any("プレゼント" in title or "ギフト" in title for title in section_titles)

    def test_customize_structure_by_intent(self):
        """検索意図に応じた構造カスタマイズを確認"""
        # Arrange
        intents = ["informational", "commercial", "navigational"]
        base_topic = "7月 誕生花 ユリ"
        
        # Act
        from src.content.content_structure_template import ContentStructureTemplate
        template = ContentStructureTemplate()
        
        structures = {}
        for intent in intents:
            structures[intent] = template.customize_structure_by_intent(base_topic, intent)
        
        # Assert
        # Commercial intent should have more CTA and purchase-related sections
        commercial_sections = [s["title"] for s in structures["commercial"]["main_sections"]]
        assert any("購入" in title or "おすすめ" in title for title in commercial_sections)
        
        # Informational intent should focus more on educational content
        info_sections = [s["title"] for s in structures["informational"]["main_sections"]]
        assert any("意味" in title or "由来" in title for title in info_sections)

    def test_validate_structure_completeness(self):
        """構造の完全性を検証できることを確認"""
        # Arrange
        incomplete_structure = {
            "introduction": {"word_count": 200},
            "main_sections": [
                {"title": "花言葉について", "word_count": 800}
            ]
            # conclusion が欠けている
        }
        
        # Act
        from src.content.content_structure_template import ContentStructureTemplate
        template = ContentStructureTemplate()
        validation = template.validate_structure_completeness(incomplete_structure)
        
        # Assert
        assert validation["is_complete"] == False
        assert "missing_elements" in validation
        assert "conclusion" in validation["missing_elements"]
        assert "recommendations" in validation


class TestContentPlanningWorkflow:
    """コンテンツ企画ワークフローの統合テスト"""

    @pytest.mark.asyncio
    async def test_complete_planning_workflow_for_birth_flower(self):
        """誕生花記事の完全な企画ワークフローをテスト"""
        # Arrange
        planning_request = {
            "topic": "8月の誕生花",
            "target_keyword": "8月 誕生花 ヒマワリ",
            "business_goal": "プレゼント販売促進",
            "content_constraints": {
                "max_word_count": 4000,
                "required_sections": ["花言葉", "プレゼント選び", "育て方"]
            }
        }
        
        # Act
        from src.content.content_planning_workflow import ContentPlanningWorkflow
        workflow = ContentPlanningWorkflow()
        planning_result = await workflow.execute_complete_planning(planning_request)
        
        # Assert
        assert "persona_analysis" in planning_result
        assert "article_concepts" in planning_result
        assert "selected_tone" in planning_result
        assert "content_structure" in planning_result
        assert "seo_optimization_plan" in planning_result
        
        # 4つの企画案が生成されている
        assert len(planning_result["article_concepts"]) == 4
        
        # 必須セクションが含まれている
        structure = planning_result["content_structure"]
        section_titles = [s["title"] for s in structure["main_sections"]]
        for required in planning_request["content_constraints"]["required_sections"]:
            assert any(required in title for title in section_titles)

    @pytest.mark.asyncio
    async def test_adaptive_planning_based_on_competition(self):
        """競合分析に基づく適応的企画を確認"""
        # Arrange
        competitor_analysis = {
            "common_sections": ["花言葉", "特徴", "プレゼント"],
            "content_gaps": ["個人的体験談", "具体的な価格情報", "季節感のある表現"],
            "average_word_count": 2500
        }
        
        base_topic = "11月 誕生花 シクラメン"
        
        # Act
        from src.content.content_planning_workflow import ContentPlanningWorkflow
        workflow = ContentPlanningWorkflow()
        adaptive_plan = await workflow.create_competitive_advantage_plan(
            base_topic, competitor_analysis
        )
        
        # Assert
        assert "differentiation_strategy" in adaptive_plan
        assert "unique_value_propositions" in adaptive_plan
        assert "content_enhancements" in adaptive_plan
        
        # 競合のギャップを埋める要素が含まれているか
        enhancements = adaptive_plan["content_enhancements"]
        gap_coverage = [enh for enh in enhancements if any(gap in enh["description"] for gap in competitor_analysis["content_gaps"])]
        assert len(gap_coverage) > 0

    def test_quality_score_prediction(self):
        """企画品質スコアの予測を確認"""
        # Arrange
        planning_elements = {
            "persona_match_score": 85,
            "keyword_optimization_score": 78,
            "content_uniqueness_score": 92,
            "structure_completeness_score": 88,
            "competition_advantage_score": 75
        }
        
        # Act
        from src.content.content_planning_workflow import ContentPlanningWorkflow
        workflow = ContentPlanningWorkflow()
        quality_prediction = workflow.predict_content_quality(planning_elements)
        
        # Assert
        assert "overall_quality_score" in quality_prediction
        assert "strength_areas" in quality_prediction
        assert "improvement_areas" in quality_prediction
        assert "success_probability" in quality_prediction
        
        assert 0 <= quality_prediction["overall_quality_score"] <= 100
        assert 0 <= quality_prediction["success_probability"] <= 1