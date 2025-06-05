"""
Competitor Research Engine Tests
競合記事調査機能のTDDテスト
"""
import asyncio
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, AsyncMock

# srcパスを追加
sys.path.append(str(Path(__file__).parent / "src"))

from seo.competitor_research_engine import CompetitorResearchEngine


class TestCompetitorResearchEngine:
    """競合記事調査機能のテスト"""
    
    @pytest.fixture
    def research_engine(self):
        return CompetitorResearchEngine()
    
    async def test_google_search_serp_analysis(self):
        """Google検索結果（SERP）分析のテスト"""
        engine = CompetitorResearchEngine()
        keyword = "3月 誕生花 プレゼント"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock Google検索結果
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value="""
            <div class="g">
                <h3><a href="https://example1.com/birth-flowers">3月の誕生花プレゼントガイド</a></h3>
                <span class="st">3月生まれの方への誕生花プレゼント選び。チューリップやスイートアリッサムなど...</span>
            </div>
            <div class="g">
                <h3><a href="https://example2.com/tulip-gift">チューリップギフト特集</a></h3>
                <span class="st">春の贈り物として人気のチューリップ。花言葉や贈り方のマナーを紹介...</span>
            </div>
            """)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await engine.analyze_google_serp(keyword, limit=10)
            
            assert "serp_results" in result
            assert "total_results" in result
            assert "competitor_domains" in result
            assert "content_patterns" in result
            assert len(result["serp_results"]) >= 2
            print(f"✅ Google SERP分析テスト成功: {len(result['serp_results'])}件の結果")
    
    async def test_competitor_content_analysis(self):
        """競合コンテンツ分析のテスト"""
        engine = CompetitorResearchEngine()
        competitor_urls = [
            "https://example1.com/birth-flowers",
            "https://example2.com/tulip-gift"
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value="""
            <html>
                <title>3月の誕生花完全ガイド - 花言葉とプレゼント選び</title>
                <meta name="description" content="3月の誕生花チューリップの花言葉と、プレゼントとしての選び方を詳しく解説">
                <h1>3月の誕生花について</h1>
                <h2>チューリップの花言葉</h2>
                <h2>プレゼント選びのポイント</h2>
                <h3>色別の花言葉</h3>
                <p>チューリップは3月の代表的な誕生花です。「思いやり」「美しい瞳」という花言葉を持ちます。</p>
                <p>プレゼントとして贈る場合は、相手の好みや関係性を考慮することが大切です。</p>
            </html>
            """)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await engine.analyze_competitor_content(competitor_urls)
            
            assert "content_analysis" in result
            assert "heading_structure" in result
            assert "meta_data" in result
            assert "content_gaps" in result
            assert "recommendations" in result
            print(f"✅ 競合コンテンツ分析テスト成功: {len(result['content_analysis'])}サイト分析")
    
    async def test_content_gap_analysis(self):
        """コンテンツギャップ分析のテスト"""
        engine = CompetitorResearchEngine()
        
        # 競合記事のサンプルデータ
        competitor_data = [
            {
                "url": "https://example1.com",
                "title": "3月の誕生花ガイド",
                "headings": ["チューリップについて", "花言葉の意味", "プレゼント選び"],
                "content_topics": ["チューリップ", "花言葉", "プレゼント", "春の花"],
                "word_count": 2500
            },
            {
                "url": "https://example2.com", 
                "title": "春の花プレゼント特集",
                "headings": ["人気の春の花", "ギフトマナー", "価格帯別選択"],
                "content_topics": ["春の花", "ギフト", "マナー", "価格"],
                "word_count": 1800
            }
        ]
        
        result = await engine.analyze_content_gaps(competitor_data, "3月 誕生花 プレゼント")
        
        assert "missing_topics" in result
        assert "coverage_gaps" in result
        assert "opportunity_keywords" in result
        assert "content_suggestions" in result
        assert len(result["missing_topics"]) > 0
        print(f"✅ コンテンツギャップ分析テスト成功: {len(result['missing_topics'])}個のギャップ発見")
    
    async def test_serp_feature_analysis(self):
        """SERP機能分析のテスト（Featured Snippets, PAA等）"""
        engine = CompetitorResearchEngine()
        keyword = "誕生花 3月"
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.text = AsyncMock(return_value="""
            <div class="xpdopen">
                <div class="kp-blk">
                    <span>3月の誕生花はチューリップやスイートアリッサムです。チューリップの花言葉は「思いやり」...</span>
                </div>
            </div>
            <div class="related-question-pair">
                <span>3月の誕生花は何ですか？</span>
                <span>3月の誕生花の花言葉は？</span>
                <span>チューリップをプレゼントする意味は？</span>
            </div>
            """)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await engine.analyze_serp_features(keyword)
            
            assert "featured_snippet" in result
            assert "people_also_ask" in result
            assert "knowledge_panel" in result
            assert "optimization_opportunities" in result
            print(f"✅ SERP機能分析テスト成功")
    
    async def test_competitor_ranking_analysis(self):
        """競合順位分析のテスト"""
        engine = CompetitorResearchEngine()
        
        keywords = ["3月 誕生花", "チューリップ プレゼント", "誕生花 花言葉"]
        
        with patch.object(engine, 'analyze_google_serp') as mock_serp:
            mock_serp.return_value = {
                "serp_results": [
                    {"position": 1, "url": "https://example1.com", "title": "Example 1"},
                    {"position": 2, "url": "https://example2.com", "title": "Example 2"},
                    {"position": 3, "url": "https://example3.com", "title": "Example 3"}
                ]
            }
            
            result = await engine.analyze_competitor_rankings(keywords)
            
            assert "keyword_rankings" in result
            assert "domain_performance" in result
            assert "ranking_patterns" in result
            assert "opportunity_analysis" in result
            print(f"✅ 競合順位分析テスト成功: {len(result['keyword_rankings'])}キーワード分析")
    
    async def test_content_quality_scoring(self):
        """コンテンツ品質スコアリングのテスト"""
        engine = CompetitorResearchEngine()
        
        content_data = {
            "url": "https://example.com",
            "title": "3月の誕生花完全ガイド - チューリップの花言葉と贈り方",
            "meta_description": "3月の誕生花チューリップについて、花言葉から贈り方まで詳しく解説します。",
            "headings": ["H1: 3月の誕生花について", "H2: チューリップの特徴", "H2: 花言葉の意味"],
            "word_count": 2500,
            "images": 8,
            "internal_links": 5,
            "external_links": 3,
            "schema_markup": True,
            "load_speed": 2.1
        }
        
        result = await engine.score_content_quality(content_data)
        
        assert "overall_score" in result
        assert "detailed_scores" in result
        assert "improvement_suggestions" in result
        assert 0 <= result["overall_score"] <= 100
        print(f"✅ コンテンツ品質スコアリングテスト成功: {result['overall_score']}/100点")
    
    async def test_generate_competitive_report(self):
        """競合分析レポート生成のテスト"""
        engine = CompetitorResearchEngine()
        
        analysis_data = {
            "keyword": "3月 誕生花 プレゼント",
            "serp_analysis": {"total_results": 10},
            "content_analysis": {"analyzed_sites": 5},
            "gap_analysis": {"missing_topics": ["育て方", "季節性"]},
            "quality_scores": {"average": 75.5}
        }
        
        result = await engine.generate_competitive_report(analysis_data)
        
        assert "executive_summary" in result
        assert "key_findings" in result
        assert "competitive_landscape" in result
        assert "content_opportunities" in result
        assert "action_items" in result
        assert "priority_recommendations" in result
        print(f"✅ 競合分析レポート生成テスト成功")


async def run_competitor_research_tests():
    """競合記事調査機能のテスト実行"""
    print("🧪 Testing Competitor Research Engine...")
    print("=" * 60)
    
    test_instance = TestCompetitorResearchEngine()
    
    tests = [
        ("Google SERP分析", test_instance.test_google_search_serp_analysis),
        ("競合コンテンツ分析", test_instance.test_competitor_content_analysis),
        ("コンテンツギャップ分析", test_instance.test_content_gap_analysis),
        ("SERP機能分析", test_instance.test_serp_feature_analysis),
        ("競合順位分析", test_instance.test_competitor_ranking_analysis),
        ("コンテンツ品質スコアリング", test_instance.test_content_quality_scoring),
        ("競合分析レポート生成", test_instance.test_generate_competitive_report)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 {test_name}...")
            await test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n🎉 All Competitor Research tests completed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    asyncio.run(run_competitor_research_tests())