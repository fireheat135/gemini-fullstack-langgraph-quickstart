"""
Simple test to verify the keyword research API works
"""
import asyncio
from src.seo.keyword_analyzer import KeywordAnalyzer

async def test_keyword_analyzer():
    """Test the keyword analyzer directly"""
    analyzer = KeywordAnalyzer()
    
    # Test basic keyword analysis
    result = await analyzer.analyze_keyword("SEO最適化")
    print("Keyword Analysis Result:")
    print(f"Keyword: {result['keyword']}")
    print(f"Search Volume: {result['search_volume']}")
    print(f"Difficulty: {result['difficulty']}")
    print(f"Trend: {result['trend']}")
    print(f"Related Keywords: {len(result.get('related_keywords', []))}")
    
    # Test keyword suggestions
    suggestions = await analyzer.suggest_keywords(
        seed_keyword="SEO最適化",
        target_audience="マーケティング担当者",
        content_type="ブログ記事"
    )
    print(f"\nKeyword Suggestions: {len(suggestions)}")
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"{i+1}. {suggestion['keyword']} (score: {suggestion['relevance_score']})")
    
    print("\nKeyword Analyzer test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_keyword_analyzer())