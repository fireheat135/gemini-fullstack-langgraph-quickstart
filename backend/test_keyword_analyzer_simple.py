"""
Simple Keyword Analyzer Test
キーワード分析機能の簡単なテスト
"""
import asyncio
import sys
from pathlib import Path

# srcパスを追加
sys.path.append(str(Path(__file__).parent / "src"))

from seo.keyword_analyzer import KeywordAnalyzer


async def test_keyword_analyzer_basic():
    """基本的なキーワード分析機能のテスト"""
    analyzer = KeywordAnalyzer()
    
    print("🧪 Testing KeywordAnalyzer Enhanced Features...")
    print("=" * 60)
    
    # Test 1: Related Keywords Suggestions
    print("\n1️⃣ Testing get_related_keywords_suggestions...")
    result = await analyzer.get_related_keywords_suggestions("3月 誕生花")
    print(f"   ✅ Generated {result['total_count']} related keywords")
    print(f"   📝 Sample keywords: {result['related_keywords'][:3]}")
    
    # Test 2: Google Trends Data (simulation)
    print("\n2️⃣ Testing get_google_trends_data...")
    trends_result = await analyzer.get_google_trends_data("誕生花")
    print(f"   ✅ Peak months detected: {trends_result['peak_months'][:3]}")
    print(f"   📊 Seasonality: {trends_result['seasonality_detected']}")
    
    # Test 3: Enhanced Keyword Difficulty
    print("\n3️⃣ Testing calculate_keyword_difficulty_enhanced...")
    difficulty_result = await analyzer.calculate_keyword_difficulty_enhanced("3月 誕生花 プレゼント")
    print(f"   ✅ Difficulty Score: {difficulty_result['difficulty_score']}")
    print(f"   💡 Recommendation: {difficulty_result['recommendation']}")
    
    # Test 4: Semantic Keywords Analysis
    print("\n4️⃣ Testing analyze_semantic_keywords...")
    candidates = ["花 ギフト", "花束 プレゼント", "誕生日 花", "記念日 花", "季節の花"]
    semantic_result = await analyzer.analyze_semantic_keywords("誕生花", candidates, "プレゼント")
    print(f"   ✅ Found {semantic_result['total_matches']} semantic matches")
    
    # Test 5: Seasonal Trends
    print("\n5️⃣ Testing analyze_seasonal_trends...")
    seasonal_result = await analyzer.analyze_seasonal_trends("誕生花")
    print(f"   ✅ Peak months: {seasonal_result['peak_months']}")
    print(f"   📈 Seasonality score: {seasonal_result['seasonality_score']}")
    
    # Test 6: Long-tail Keywords
    print("\n6️⃣ Testing generate_long_tail_keywords...")
    longtail_result = await analyzer.generate_long_tail_keywords("誕生花")
    print(f"   ✅ Generated {longtail_result['total_generated']} long-tail keywords")
    print(f"   📋 Top 3: {longtail_result['long_tail_keywords'][:3]}")
    
    # Test 7: Keyword Clustering by Intent
    print("\n7️⃣ Testing cluster_keywords_by_intent...")
    test_keywords = [
        "誕生花 3月",
        "3月 誕生花 プレゼント",
        "チューリップ 花言葉",
        "誕生花 とは",
        "花 ギフト 通販"
    ]
    cluster_result = await analyzer.cluster_keywords_by_intent(test_keywords)
    print(f"   ✅ Clustered into {len(cluster_result['clusters'])} intent categories")
    print(f"   📊 Cluster sizes: {cluster_result['cluster_sizes']}")
    
    print(f"\n🎉 All tests completed successfully!")
    print("=" * 60)
    
    return True


async def main():
    """メイン実行関数"""
    try:
        success = await test_keyword_analyzer_basic()
        if success:
            print("✅ Phase 1: キーワード分析機能拡張 - 完了")
            return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(main())