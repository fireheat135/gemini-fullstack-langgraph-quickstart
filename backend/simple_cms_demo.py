"""
Simple demonstration of Content Management System functionality
Without external dependencies
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from collections import Counter


class AlertType(Enum):
    EXACT_DUPLICATE = "exact_duplicate"
    HIGH_SIMILARITY = "high_similarity"
    TONE_INCONSISTENCY = "tone_inconsistency"


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
    tags: Optional[List[str]] = None


@dataclass
class StorageResult:
    success: bool
    article_id: str
    message: str


@dataclass
class SimilarityMatch:
    article_id: str
    similarity_score: float
    match_type: str


@dataclass
class DuplicateDetectionResult:
    has_duplicates: bool
    exact_matches: List[SimilarityMatch]
    partial_matches: List[SimilarityMatch]
    tone_manner_matches: List[SimilarityMatch]


@dataclass
class ContentAlert:
    alert_type: AlertType
    severity: str
    message: str
    article_id: str


class SimpleContentManagementSystem:
    """Simplified Content Management System for demonstration"""
    
    def __init__(self):
        self.articles: Dict[str, ArticleContent] = {}
        self.content_fingerprints: Dict[str, str] = {}
    
    def store_article(self, article: ArticleContent) -> StorageResult:
        """記事を保存"""
        if not article.id or not article.title or not article.content:
            return StorageResult(
                success=False,
                article_id=article.id,
                message="無効な記事データです"
            )
        
        fingerprint = self.generate_content_fingerprint(article.content)
        self.articles[article.id] = article
        self.content_fingerprints[article.id] = fingerprint
        
        return StorageResult(
            success=True,
            article_id=article.id,
            message="記事が正常に保存されました"
        )
    
    def get_article_by_id(self, article_id: str) -> Optional[ArticleContent]:
        """記事IDで記事を取得"""
        return self.articles.get(article_id)
    
    def get_articles_by_keyword(self, keyword: str) -> List[ArticleContent]:
        """キーワードで記事を検索"""
        results = []
        for article in self.articles.values():
            if (keyword.lower() in article.keyword.lower() or
                keyword.lower() in article.title.lower() or
                keyword.lower() in article.content.lower()):
                results.append(article)
        return results
    
    def generate_content_fingerprint(self, content: str) -> str:
        """コンテンツフィンガープリント生成"""
        normalized = re.sub(r'\s+', ' ', content.strip())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """簡単な類似度計算（Jaccard係数）"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def detect_duplicates(self, new_article: ArticleContent) -> DuplicateDetectionResult:
        """重複検出"""
        exact_matches = []
        partial_matches = []
        tone_manner_matches = []
        
        if not self.articles:
            return DuplicateDetectionResult(
                has_duplicates=False,
                exact_matches=[],
                partial_matches=[],
                tone_manner_matches=[]
            )
        
        new_fingerprint = self.generate_content_fingerprint(new_article.content)
        
        for existing_id, existing_article in self.articles.items():
            # 完全重複チェック
            existing_fingerprint = self.content_fingerprints.get(existing_id)
            if existing_fingerprint == new_fingerprint:
                exact_matches.append(SimilarityMatch(
                    article_id=existing_id,
                    similarity_score=1.0,
                    match_type="exact_duplicate"
                ))
                continue
            
            # 類似度計算
            similarity = self.calculate_simple_similarity(
                new_article.content,
                existing_article.content
            )
            
            if similarity >= 0.7:  # 高い類似度
                partial_matches.append(SimilarityMatch(
                    article_id=existing_id,
                    similarity_score=similarity,
                    match_type="high_similarity"
                ))
            
            # トンマナ類似チェック
            tone_similarity = self.calculate_tone_manner_similarity(
                new_article.tone_manner,
                existing_article.tone_manner
            )
            
            if tone_similarity >= 0.8:
                tone_manner_matches.append(SimilarityMatch(
                    article_id=existing_id,
                    similarity_score=tone_similarity,
                    match_type="tone_manner_match"
                ))
        
        has_duplicates = bool(exact_matches or partial_matches)
        
        return DuplicateDetectionResult(
            has_duplicates=has_duplicates,
            exact_matches=exact_matches,
            partial_matches=partial_matches,
            tone_manner_matches=tone_manner_matches
        )
    
    def calculate_tone_manner_similarity(self, tone1: ToneManner, tone2: ToneManner) -> float:
        """トンマナ類似度計算"""
        if not tone1 or not tone2:
            return 0.0
        
        matches = 0
        total = 4
        
        if tone1.tone == tone2.tone:
            matches += 1
        if tone1.formality == tone2.formality:
            matches += 1
        if tone1.target_audience == tone2.target_audience:
            matches += 1
        if tone1.writing_style == tone2.writing_style:
            matches += 1
        
        return matches / total
    
    def generate_content_alerts(self, new_article: ArticleContent) -> List[ContentAlert]:
        """コンテンツアラート生成"""
        alerts = []
        
        if not self.articles:
            return alerts
        
        duplicate_result = self.detect_duplicates(new_article)
        
        # 完全重複アラート
        for match in duplicate_result.exact_matches:
            alerts.append(ContentAlert(
                alert_type=AlertType.EXACT_DUPLICATE,
                severity="HIGH",
                message=f"完全重複のコンテンツが検出されました（記事ID: {match.article_id}）",
                article_id=new_article.id
            ))
        
        # 高類似度アラート
        for match in duplicate_result.partial_matches:
            alerts.append(ContentAlert(
                alert_type=AlertType.HIGH_SIMILARITY,
                severity="MEDIUM",
                message=f"高い類似度のコンテンツが検出されました（類似度: {match.similarity_score:.2f}）",
                article_id=new_article.id
            ))
        
        return alerts
    
    def calculate_content_quality_score(self, article: ArticleContent) -> Dict[str, float]:
        """コンテンツ品質スコア計算"""
        scores = {}
        
        # 独自性スコア
        if self.articles:
            duplicate_result = self.detect_duplicates(article)
            max_similarity = 0.0
            if duplicate_result.partial_matches:
                max_similarity = max(match.similarity_score for match in duplicate_result.partial_matches)
            scores["uniqueness_score"] = 1.0 - max_similarity
        else:
            scores["uniqueness_score"] = 1.0
        
        # キーワード関連性スコア
        keyword_in_content = article.keyword.lower() in article.content.lower()
        keyword_in_title = article.keyword.lower() in article.title.lower()
        scores["keyword_relevance_score"] = (
            0.7 if keyword_in_content else 0.0
        ) + (0.3 if keyword_in_title else 0.0)
        
        # 総合スコア
        scores["overall_score"] = (
            scores["uniqueness_score"] * 0.6 +
            scores["keyword_relevance_score"] * 0.4
        )
        
        return scores


def main():
    """デモンストレーション実行"""
    print("🚀 Content Management System Demo - Phase 5 Implementation")
    print("=" * 60)
    
    # CMS初期化
    cms = SimpleContentManagementSystem()
    print("✅ CMS initialized")
    
    # サンプル記事作成
    tone1 = ToneManner(
        tone="親しみやすい",
        formality="カジュアル",
        target_audience="花好きの女性",
        writing_style="情報提供型"
    )
    
    article1 = ArticleContent(
        id="article_1",
        title="1月の誕生花「カーネーション」の花言葉と育て方",
        content="カーネーションは1月を代表する美しい花です。花言葉は「母への愛」「感謝」を表しています。育て方のポイントは適切な水やりと日光管理です。",
        keyword="1月 誕生花 カーネーション",
        tone_manner=tone1,
        created_at=datetime.now(),
        tags=["誕生花", "1月", "カーネーション", "花言葉"]
    )
    
    article2 = ArticleContent(
        id="article_2",
        title="2月の誕生花「プリムラ」の特徴と花言葉",
        content="プリムラは2月の代表的な誕生花として親しまれています。可憐な花びらと豊富な色彩が魅力的で、「青春の喜び」という花言葉を持ちます。",
        keyword="2月 誕生花 プリムラ",
        tone_manner=tone1,
        created_at=datetime.now(),
        tags=["誕生花", "2月", "プリムラ", "花言葉"]
    )
    
    # 記事保存テスト
    print("\n📝 記事保存機能テスト")
    result1 = cms.store_article(article1)
    print(f"   記事1: {result1.success} - {result1.message}")
    
    result2 = cms.store_article(article2)
    print(f"   記事2: {result2.success} - {result2.message}")
    
    # 記事取得テスト
    print("\n🔍 記事取得機能テスト")
    retrieved = cms.get_article_by_id("article_1")
    print(f"   取得成功: {retrieved.title if retrieved else 'None'}")
    
    # キーワード検索テスト
    print("\n🔍 キーワード検索機能テスト")
    search_results = cms.get_articles_by_keyword("誕生花")
    print(f"   検索結果: {len(search_results)}件")
    for article in search_results:
        print(f"     - {article.title}")
    
    # 重複検出テスト
    print("\n🔄 重複検出機能テスト")
    duplicate_article = ArticleContent(
        id="duplicate_test",
        title="重複テスト記事",
        content=article1.content,  # 同じコンテンツ
        keyword="重複テスト",
        tone_manner=tone1,
        created_at=datetime.now()
    )
    
    duplicate_result = cms.detect_duplicates(duplicate_article)
    print(f"   重複検出: {duplicate_result.has_duplicates}")
    print(f"   完全一致: {len(duplicate_result.exact_matches)}件")
    print(f"   部分一致: {len(duplicate_result.partial_matches)}件")
    print(f"   トンマナ一致: {len(duplicate_result.tone_manner_matches)}件")
    
    # アラート生成テスト
    print("\n⚠️ アラート機能テスト")
    alerts = cms.generate_content_alerts(duplicate_article)
    print(f"   生成されたアラート: {len(alerts)}件")
    for alert in alerts:
        print(f"     - {alert.severity}: {alert.message}")
    
    # 品質スコアリングテスト
    print("\n📊 品質スコアリング機能テスト")
    quality_score = cms.calculate_content_quality_score(article1)
    print("   品質スコア:")
    for metric, score in quality_score.items():
        print(f"     - {metric}: {score:.3f}")
    
    # フィンガープリント生成テスト
    print("\n🔐 フィンガープリント生成テスト")
    fingerprint = cms.generate_content_fingerprint(article1.content)
    print(f"   フィンガープリント: {fingerprint[:16]}...")
    
    print("\n🎉 Phase 5 Content Management System - 全機能実装完了!")
    print("=" * 60)
    print("✅ 過去記事のコンテンツ・トンマナ保存機能")
    print("✅ 記事間重複コンテンツ検出")
    print("✅ 類似度判定アルゴリズム")
    print("✅ 重複アラート機能")
    print("✅ コンテンツ品質スコアリング")
    print("✅ フィンガープリント生成")


if __name__ == "__main__":
    main()