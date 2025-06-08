"""
Content Management System
過去記事管理・重複検出システム

機能:
1. 過去記事のコンテンツ・トンマナ保存機能
2. 記事間重複コンテンツ検出
3. 類似度判定アルゴリズム
4. 重複アラート機能
"""

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import math

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Japanese tokenizer with fallback
try:
    import MeCab
    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False

try:
    from janome.tokenizer import Tokenizer as JanomeTokenizer
    JANOME_AVAILABLE = True
except ImportError:
    JANOME_AVAILABLE = False


class AlertType(Enum):
    """アラートタイプ"""
    EXACT_DUPLICATE = "exact_duplicate"
    HIGH_SIMILARITY = "high_similarity" 
    MODERATE_SIMILARITY = "moderate_similarity"
    TONE_INCONSISTENCY = "tone_inconsistency"
    KEYWORD_OVERLAP = "keyword_overlap"


@dataclass
class ToneManner:
    """トーン&マナー設定"""
    tone: str  # 親しみやすい、フォーマル等
    formality: str  # カジュアル、丁寧等
    target_audience: str  # ターゲット読者
    writing_style: str  # 情報提供型、問題解決型等
    
    def __post_init__(self):
        """バリデーション"""
        if not all([self.tone, self.formality, self.target_audience, self.writing_style]):
            raise ValueError("全てのトンマナ要素を指定してください")


@dataclass
class ArticleContent:
    """記事コンテンツデータ"""
    id: str
    title: str
    content: str
    keyword: str
    tone_manner: ToneManner
    created_at: datetime
    meta_description: Optional[str] = None
    tags: Optional[List[str]] = None
    
    def __post_init__(self):
        """バリデーション"""
        if not all([self.id, self.title, self.content]):
            raise ValueError("記事の必須フィールドが不足しています")


@dataclass
class SimilarityThreshold:
    """類似度閾値設定"""
    exact_match: float = 0.98
    high_similarity: float = 0.80
    moderate_similarity: float = 0.60
    low_similarity: float = 0.40


@dataclass
class SimilarityMatch:
    """類似マッチ結果"""
    article_id: str
    similarity_score: float
    match_type: str
    matched_sections: List[str] = None


@dataclass
class SimilarityAnalysis:
    """類似度分析結果"""
    cosine_score: float
    jaccard_score: float
    semantic_score: float
    overall_score: float
    analysis_details: Dict[str, Any] = None


@dataclass
class DuplicateDetectionResult:
    """重複検出結果"""
    has_duplicates: bool
    exact_matches: List[SimilarityMatch]
    partial_matches: List[SimilarityMatch]
    tone_manner_matches: List[SimilarityMatch]
    analysis_summary: Dict[str, Any] = None


@dataclass
class ContentAlert:
    """コンテンツアラート"""
    alert_type: AlertType
    severity: str  # HIGH, MEDIUM, LOW
    message: str
    article_id: str
    related_articles: List[str] = None
    recommendations: List[str] = None


@dataclass
class StorageResult:
    """保存結果"""
    success: bool
    article_id: str
    message: str
    warnings: List[str] = None


class ContentManagementSystem:
    """
    コンテンツ管理システム
    過去記事の管理、重複検出、類似度分析を行う
    """
    
    def __init__(self):
        self.articles: Dict[str, ArticleContent] = {}
        self.content_fingerprints: Dict[str, str] = {}
        self.similarity_thresholds = SimilarityThreshold()
        
        # Initialize Japanese tokenizer
        if MECAB_AVAILABLE:
            self.mecab = MeCab.Tagger("-Ochasen")
            self.tokenizer_type = "mecab"
        elif JANOME_AVAILABLE:
            self.janome = JanomeTokenizer()
            self.tokenizer_type = "janome"
        else:
            self.tokenizer_type = "simple"
        
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            max_features=10000
        )
        self._content_vectors = {}
        
    # ===== 記事保存・管理機能 =====
    
    def store_article(self, article: ArticleContent) -> StorageResult:
        """
        記事を保存する
        
        Args:
            article: 保存する記事
            
        Returns:
            StorageResult: 保存結果
        """
        try:
            # バリデーション
            if not article.id or not article.title or not article.content:
                return StorageResult(
                    success=False,
                    article_id=article.id,
                    message="無効な記事データです。必須フィールドが不足しています。"
                )
            
            warnings = []
            
            # 重複チェック
            if article.id in self.articles:
                warnings.append(f"記事ID '{article.id}' は既に存在します。上書きされます。")
            
            # フィンガープリント生成
            fingerprint = self.generate_content_fingerprint(article.content)
            
            # 保存
            self.articles[article.id] = article
            self.content_fingerprints[article.id] = fingerprint
            
            # ベクトル化（類似度計算用）
            self._update_content_vectors()
            
            return StorageResult(
                success=True,
                article_id=article.id,
                message="記事が正常に保存されました",
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            return StorageResult(
                success=False,
                article_id=article.id if hasattr(article, 'id') else "unknown",
                message=f"記事保存中にエラーが発生しました: {str(e)}"
            )
    
    def get_article_by_id(self, article_id: str) -> Optional[ArticleContent]:
        """
        記事IDで記事を取得
        
        Args:
            article_id: 記事ID
            
        Returns:
            ArticleContent: 記事データまたはNone
        """
        return self.articles.get(article_id)
    
    def get_articles_by_keyword(self, keyword: str) -> List[ArticleContent]:
        """
        キーワードで記事を検索
        
        Args:
            keyword: 検索キーワード
            
        Returns:
            List[ArticleContent]: マッチした記事のリスト
        """
        matching_articles = []
        
        for article in self.articles.values():
            if (keyword.lower() in article.keyword.lower() or
                keyword.lower() in article.title.lower() or
                keyword.lower() in article.content.lower()):
                matching_articles.append(article)
        
        return matching_articles
    
    def get_articles_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ArticleContent]:
        """
        日付範囲で記事を検索
        
        Args:
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            List[ArticleContent]: 範囲内の記事のリスト
        """
        matching_articles = []
        
        for article in self.articles.values():
            if start_date <= article.created_at <= end_date:
                matching_articles.append(article)
        
        return sorted(matching_articles, key=lambda x: x.created_at, reverse=True)
    
    # ===== 重複検出機能 =====
    
    def detect_duplicates(self, new_article: ArticleContent) -> DuplicateDetectionResult:
        """
        新しい記事の重複を検出
        
        Args:
            new_article: チェックする記事
            
        Returns:
            DuplicateDetectionResult: 重複検出結果
        """
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
            
            # 類似度分析
            analysis = self.analyze_semantic_similarity(
                new_article.content,
                existing_article.content
            )
            
            # 部分重複チェック
            if analysis.overall_score >= self.similarity_thresholds.high_similarity:
                partial_matches.append(SimilarityMatch(
                    article_id=existing_id,
                    similarity_score=analysis.overall_score,
                    match_type="high_similarity" if analysis.overall_score >= 0.8 else "moderate_similarity"
                ))
            
            # トンマナ類似チェック
            tone_similarity = self.calculate_tone_manner_similarity(
                new_article.tone_manner,
                existing_article.tone_manner
            )
            
            if tone_similarity >= 0.8:  # 高いトンマナ類似度
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
            tone_manner_matches=tone_manner_matches,
            analysis_summary={
                "total_checked": len(self.articles),
                "exact_matches_count": len(exact_matches),
                "partial_matches_count": len(partial_matches),
                "tone_matches_count": len(tone_manner_matches)
            }
        )
    
    # ===== 類似度判定アルゴリズム =====
    
    def calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """
        コサイン類似度を計算
        
        Args:
            text1: テキスト1
            text2: テキスト2
            
        Returns:
            float: コサイン類似度 (0-1)
        """
        try:
            # テキストをベクトル化
            vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            
            # コサイン類似度計算
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return float(similarity_matrix[0, 1])
            
        except Exception:
            return 0.0
    
    def calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Jaccard類似度を計算
        
        Args:
            text1: テキスト1  
            text2: テキスト2
            
        Returns:
            float: Jaccard類似度 (0-1)
        """
        try:
            # 単語に分割
            words1 = set(self._tokenize_japanese(text1))
            words2 = set(self._tokenize_japanese(text2))
            
            # Jaccard係数計算
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def analyze_semantic_similarity(self, text1: str, text2: str) -> SimilarityAnalysis:
        """
        意味的類似度を分析
        
        Args:
            text1: テキスト1
            text2: テキスト2
            
        Returns:
            SimilarityAnalysis: 類似度分析結果
        """
        cosine_score = self.calculate_cosine_similarity(text1, text2)
        jaccard_score = self.calculate_jaccard_similarity(text1, text2)
        
        # 簡易的な意味的類似度（実際はWord2VecやBERTを使用することが多い）
        semantic_score = (cosine_score + jaccard_score) / 2
        
        # 総合スコア（重み付き平均）
        overall_score = (
            cosine_score * 0.4 +
            jaccard_score * 0.3 +
            semantic_score * 0.3
        )
        
        return SimilarityAnalysis(
            cosine_score=cosine_score,
            jaccard_score=jaccard_score,
            semantic_score=semantic_score,
            overall_score=overall_score,
            analysis_details={
                "text1_length": len(text1),
                "text2_length": len(text2),
                "common_words": len(set(self._tokenize_japanese(text1)).intersection(
                    set(self._tokenize_japanese(text2))
                ))
            }
        )
    
    def calculate_tone_manner_similarity(self, tone1: ToneManner, tone2: ToneManner) -> float:
        """
        トンマナ類似度を計算
        
        Args:
            tone1: トンマナ1
            tone2: トンマナ2
            
        Returns:
            float: 類似度 (0-1)
        """
        if not tone1 or not tone2:
            return 0.0
        
        # 各要素の一致度を計算
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
    
    # ===== アラート機能 =====
    
    def generate_content_alerts(self, new_article: ArticleContent) -> List[ContentAlert]:
        """
        コンテンツアラートを生成
        
        Args:
            new_article: チェックする記事
            
        Returns:
            List[ContentAlert]: アラートのリスト
        """
        alerts = []
        
        if not self.articles:
            return alerts
        
        # 重複検出
        duplicate_result = self.detect_duplicates(new_article)
        
        # 完全重複アラート
        for match in duplicate_result.exact_matches:
            alerts.append(ContentAlert(
                alert_type=AlertType.EXACT_DUPLICATE,
                severity="HIGH",
                message=f"完全重複のコンテンツが検出されました（記事ID: {match.article_id}）",
                article_id=new_article.id,
                related_articles=[match.article_id],
                recommendations=[
                    "コンテンツを大幅に修正してください",
                    "異なる視点からのアプローチを検討してください"
                ]
            ))
        
        # 高類似度アラート
        for match in duplicate_result.partial_matches:
            if match.similarity_score >= self.similarity_thresholds.high_similarity:
                alerts.append(ContentAlert(
                    alert_type=AlertType.HIGH_SIMILARITY,
                    severity="HIGH" if match.similarity_score >= 0.9 else "MEDIUM",
                    message=f"高い類似度のコンテンツが検出されました（類似度: {match.similarity_score:.2f}）",
                    article_id=new_article.id,
                    related_articles=[match.article_id],
                    recommendations=[
                        "独自性を高める内容を追加してください",
                        "異なる角度からの情報を盛り込んでください"
                    ]
                ))
        
        # トンマナ一貫性アラート
        existing_tones = [article.tone_manner for article in self.articles.values()]
        if existing_tones:
            most_common_tone = self._find_most_common_tone(existing_tones)
            if most_common_tone:
                tone_similarity = self.calculate_tone_manner_similarity(
                    new_article.tone_manner,
                    most_common_tone
                )
                
                if tone_similarity < 0.5:  # 低い一貫性
                    alerts.append(ContentAlert(
                        alert_type=AlertType.TONE_INCONSISTENCY,
                        severity="MEDIUM" if tone_similarity < 0.3 else "LOW",
                        message=f"トンマナの一貫性が低い可能性があります（一致度: {tone_similarity:.2f}）",
                        article_id=new_article.id,
                        recommendations=[
                            "既存記事のトンマナに合わせることを検討してください",
                            "ブランドガイドラインを確認してください"
                        ]
                    ))
        
        return alerts
    
    # ===== 高度な分析機能 =====
    
    def generate_content_fingerprint(self, content: str) -> str:
        """
        コンテンツのフィンガープリントを生成
        
        Args:
            content: コンテンツ
            
        Returns:
            str: フィンガープリント（ハッシュ値）
        """
        # 正規化（空白、改行、句読点を統一）
        normalized = re.sub(r'\s+', ' ', content.strip())
        normalized = re.sub(r'[。、！？\.\,\\!\?]', '', normalized)
        
        # SHA-256ハッシュ生成
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def batch_duplicate_analysis(self, articles: List[ArticleContent]) -> List[DuplicateDetectionResult]:
        """
        複数記事のバッチ重複分析
        
        Args:
            articles: 分析する記事のリスト
            
        Returns:
            List[DuplicateDetectionResult]: 各記事の重複検出結果
        """
        results = []
        
        for article in articles:
            result = self.detect_duplicates(article)
            results.append(result)
        
        return results
    
    def calculate_content_quality_score(self, article: ArticleContent) -> Dict[str, float]:
        """
        コンテンツ品質スコアを計算
        
        Args:
            article: 分析する記事
            
        Returns:
            Dict[str, float]: 品質スコア
        """
        scores = {}
        
        # 独自性スコア（重複度の逆数）
        if self.articles:
            duplicate_result = self.detect_duplicates(article)
            max_similarity = 0.0
            if duplicate_result.partial_matches:
                max_similarity = max(match.similarity_score for match in duplicate_result.partial_matches)
            scores["uniqueness_score"] = 1.0 - max_similarity
        else:
            scores["uniqueness_score"] = 1.0
        
        # トンマナ一貫性スコア
        existing_tones = [a.tone_manner for a in self.articles.values()]
        if existing_tones:
            most_common_tone = self._find_most_common_tone(existing_tones)
            if most_common_tone:
                scores["tone_consistency_score"] = self.calculate_tone_manner_similarity(
                    article.tone_manner,
                    most_common_tone
                )
            else:
                scores["tone_consistency_score"] = 1.0
        else:
            scores["tone_consistency_score"] = 1.0
        
        # キーワード関連性スコア（簡易計算）
        keyword_in_content = article.keyword.lower() in article.content.lower()
        keyword_in_title = article.keyword.lower() in article.title.lower()
        scores["keyword_relevance_score"] = (
            0.7 if keyword_in_content else 0.0
        ) + (0.3 if keyword_in_title else 0.0)
        
        # 総合スコア
        scores["overall_score"] = (
            scores["uniqueness_score"] * 0.4 +
            scores["tone_consistency_score"] * 0.3 +
            scores["keyword_relevance_score"] * 0.3
        )
        
        return scores
    
    # ===== 設定管理 =====
    
    def set_similarity_thresholds(self, thresholds: SimilarityThreshold):
        """類似度閾値を設定"""
        self.similarity_thresholds = thresholds
    
    def get_similarity_thresholds(self) -> SimilarityThreshold:
        """類似度閾値を取得"""
        return self.similarity_thresholds
    
    # ===== プライベートメソッド =====
    
    def _tokenize_japanese(self, text: str) -> List[str]:
        """
        日本語テキストをトークン化
        
        Args:
            text: 入力テキスト
            
        Returns:
            List[str]: トークンのリスト
        """
        try:
            if self.tokenizer_type == "mecab":
                result = []
                node = self.mecab.parseToNode(text)
                
                while node:
                    if node.surface and node.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞']:
                        result.append(node.surface)
                    node = node.next
                
                return result
                
            elif self.tokenizer_type == "janome":
                result = []
                for token in self.janome.tokenize(text, wakati=False):
                    if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞']:
                        result.append(token.surface)
                
                return result
            
            else:
                # Simple tokenization fallback
                return text.split()
            
        except Exception:
            # Fallback to simple tokenization
            return text.split()
    
    def _update_content_vectors(self):
        """コンテンツベクトルを更新"""
        if not self.articles:
            return
        
        contents = [article.content for article in self.articles.values()]
        article_ids = list(self.articles.keys())
        
        try:
            vectors = self.tfidf_vectorizer.fit_transform(contents)
            self._content_vectors = {
                article_ids[i]: vectors[i] for i in range(len(article_ids))
            }
        except Exception:
            self._content_vectors = {}
    
    def _find_most_common_tone(self, tones: List[ToneManner]) -> Optional[ToneManner]:
        """
        最も一般的なトンマナを特定
        
        Args:
            tones: トンマナのリスト
            
        Returns:
            ToneManner: 最も一般的なトンマナ
        """
        if not tones:
            return None
        
        # 各要素の出現回数をカウント
        tone_strings = [f"{t.tone}|{t.formality}|{t.target_audience}|{t.writing_style}" for t in tones]
        counter = Counter(tone_strings)
        
        if not counter:
            return tones[0]
        
        most_common_string = counter.most_common(1)[0][0]
        parts = most_common_string.split('|')
        
        return ToneManner(
            tone=parts[0],
            formality=parts[1],
            target_audience=parts[2],
            writing_style=parts[3]
        )


# エクスポート
__all__ = [
    'ContentManagementSystem',
    'ArticleContent',
    'DuplicateDetectionResult',
    'SimilarityAnalysis',
    'ContentAlert',
    'ToneManner',
    'AlertType',
    'SimilarityThreshold'
]