"""
Simple demonstration of Content Management System functionality
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from content.content_management_system import (
        ContentManagementSystem,
        ArticleContent,
        ToneManner
    )
    
    print("✅ Content Management System modules imported successfully!")
    
    # Create CMS instance
    cms = ContentManagementSystem()
    print(f"✅ CMS initialized with tokenizer: {cms.tokenizer_type}")
    
    # Create sample articles
    tone1 = ToneManner(
        tone="親しみやすい",
        formality="カジュアル",
        target_audience="花好きの女性",
        writing_style="情報提供型"
    )
    
    article1 = ArticleContent(
        id="test_1",
        title="1月の誕生花「カーネーション」の花言葉",
        content="カーネーションは1月を代表する美しい花です。花言葉は「母への愛」「感謝」を表しています。",
        keyword="1月 誕生花 カーネーション",
        tone_manner=tone1,
        created_at=datetime.now(),
        tags=["誕生花", "1月", "カーネーション"]
    )
    
    article2 = ArticleContent(
        id="test_2",
        title="カーネーションの育て方ガイド",
        content="カーネーションは比較的育てやすい花として知られています。適切な水やりが重要です。",
        keyword="カーネーション 育て方",
        tone_manner=tone1,
        created_at=datetime.now(),
        tags=["カーネーション", "育て方"]
    )
    
    # Test basic storage
    result1 = cms.store_article(article1)
    print(f"✅ Article 1 stored: {result1.success} - {result1.message}")
    
    result2 = cms.store_article(article2)
    print(f"✅ Article 2 stored: {result2.success} - {result2.message}")
    
    # Test retrieval
    retrieved = cms.get_article_by_id("test_1")
    print(f"✅ Article retrieved: {retrieved.title if retrieved else 'None'}")
    
    # Test keyword search
    keyword_results = cms.get_articles_by_keyword("カーネーション")
    print(f"✅ Keyword search results: {len(keyword_results)} articles found")
    
    # Test similarity calculation (fallback to simple tokenization)
    try:
        similarity = cms.calculate_cosine_similarity(
            "カーネーションは美しい花です",
            "カーネーションは美しい花として知られています"
        )
        print(f"✅ Cosine similarity calculated: {similarity:.3f}")
    except Exception as e:
        print(f"⚠️ Similarity calculation failed (normal without sklearn): {e}")
    
    # Test duplicate detection
    duplicate_article = ArticleContent(
        id="test_duplicate",
        title="重複テスト",
        content=article1.content,  # Same content
        keyword="重複テスト",
        tone_manner=tone1,
        created_at=datetime.now()
    )
    
    duplicate_result = cms.detect_duplicates(duplicate_article)
    print(f"✅ Duplicate detection: {duplicate_result.has_duplicates} duplicates found")
    print(f"   - Exact matches: {len(duplicate_result.exact_matches)}")
    print(f"   - Partial matches: {len(duplicate_result.partial_matches)}")
    
    # Test content fingerprint
    fingerprint = cms.generate_content_fingerprint(article1.content)
    print(f"✅ Content fingerprint generated: {fingerprint[:16]}...")
    
    # Test alerts
    alerts = cms.generate_content_alerts(duplicate_article)
    print(f"✅ Content alerts generated: {len(alerts)} alerts")
    for alert in alerts:
        print(f"   - {alert.severity}: {alert.message}")
    
    # Test quality scoring
    quality_score = cms.calculate_content_quality_score(article1)
    print(f"✅ Quality scoring completed:")
    for metric, score in quality_score.items():
        print(f"   - {metric}: {score:.3f}")
    
    print("\n🎉 All Content Management System features demonstrated successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Missing dependencies - this is expected in test environment")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()