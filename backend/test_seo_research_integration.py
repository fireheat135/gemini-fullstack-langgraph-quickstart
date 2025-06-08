"""
Test SEO Research integration with LangGraph
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.seo_research_graph import run_seo_research


async def test_seo_research_workflow():
    """Test the complete SEO research workflow"""
    print("🔍 Testing SEO Research Workflow with LangGraph...")
    
    # Test parameters
    primary_keyword = "SEO最適化"
    target_audience = "マーケティング担当者"
    
    try:
        print(f"📊 Starting research for keyword: {primary_keyword}")
        print(f"👥 Target audience: {target_audience}")
        print("⏳ Running workflow...")
        
        # Run the SEO research workflow
        result = await run_seo_research(
            primary_keyword=primary_keyword,
            target_audience=target_audience
        )
        
        print("\n✅ SEO Research Workflow completed!")
        print("=" * 50)
        
        # Display results
        if "keyword_data" in result:
            print("📈 Keyword Analysis:")
            keyword_data = result["keyword_data"]
            if "primary_analysis" in keyword_data:
                analysis = keyword_data["primary_analysis"]
                print(f"  - Search Volume: {analysis.get('search_volume', 'N/A')}")
                print(f"  - Difficulty: {analysis.get('difficulty', 'N/A')}")
                print(f"  - Trend: {analysis.get('trend', 'N/A')}")
            
            if "related_keywords" in keyword_data:
                related = keyword_data["related_keywords"]
                print(f"  - Related Keywords: {len(related)} found")
                for i, kw in enumerate(related[:5]):
                    print(f"    {i+1}. {kw}")
        
        if "competitor_data" in result:
            competitors = result["competitor_data"]
            print(f"\n🏆 Competitor Analysis: {len(competitors)} competitors analyzed")
        
        if "content_gaps" in result:
            gaps = result["content_gaps"]
            print(f"\n📝 Content Gaps: {len(gaps)} opportunities identified")
            for i, gap in enumerate(gaps):
                print(f"  {i+1}. {gap}")
        
        if "seo_recommendations" in result:
            recommendations = result["seo_recommendations"]
            print(f"\n💡 SEO Recommendations:")
            for i, rec in enumerate(recommendations):
                print(f"  {i+1}. {rec}")
        
        if "seo_insights" in result:
            print("\n📋 SEO Insights Report:")
            print("-" * 30)
            insights = result["seo_insights"]
            # Print first 500 characters of insights
            print(insights[:500] + "..." if len(insights) > 500 else insights)
        
        print(f"\n⏱️  Generated at: {result.get('generated_at', 'N/A')}")
        print("🎉 Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_integration():
    """Test API integration"""
    print("\n🌐 Testing API Integration...")
    
    try:
        from src.api.v1.seo_research import execute_seo_research
        
        # Simulate API call
        research_id = "test_research_123"
        
        # Add test session
        from src.api.v1.seo_research import research_sessions
        research_sessions[research_id] = {
            "status": "started",
            "primary_keyword": "テストキーワード",
            "target_audience": "テストユーザー",
            "user_id": 1,
            "progress": 0
        }
        
        # Execute research
        await execute_seo_research(
            research_id=research_id,
            primary_keyword="テストキーワード",
            target_audience="テストユーザー"
        )
        
        # Check results
        session = research_sessions[research_id]
        print(f"✅ API Integration test completed!")
        print(f"📊 Status: {session.get('status')}")
        print(f"⚡ Processing time: {session.get('processing_time', 'N/A')}s")
        
        return True
        
    except Exception as e:
        print(f"❌ API Integration test failed: {e}")
        return False


if __name__ == "__main__":
    async def main():
        print("🚀 Starting SEO Research Integration Tests")
        print("=" * 60)
        
        # Test 1: Core workflow
        test1_success = await test_seo_research_workflow()
        
        # Test 2: API integration
        test2_success = await test_api_integration()
        
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        print(f"✅ Core Workflow: {'PASSED' if test1_success else 'FAILED'}")
        print(f"✅ API Integration: {'PASSED' if test2_success else 'FAILED'}")
        
        if test1_success and test2_success:
            print("🎉 All tests passed! SEO Research integration is working.")
        else:
            print("❌ Some tests failed. Check the output above.")
    
    asyncio.run(main())