"""
Content Management System
コンテンツ管理システム

過去記事管理・重複検出システム
- 記事コンテンツの保存と管理
- コンテンツ重複検出
- 類似度判定アルゴリズム
- 重複アラート機能

TDD Green Phase: 最小限の実装
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import hashlib
import re
import math
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ContentManagementSystem:
    """
    コンテンツ管理システム
    
    記事の保存、重複検出、類似度計算などを行う
    単一責任原則に従い、コンテンツ管理に特化
    """
    
    def __init__(self):
        # 一時的にメモリ内ストレージを使用（後でDB実装）
        self.articles_storage: Dict[str, Dict[str, Any]] = {}
        self.versions_storage: Dict[str, List[Dict[str, Any]]] = {}
        self.duplicate_threshold = 0.4  # より実用的な閾値に設定
        
    def _validate_article_data(self, article_data: Dict[str, Any]) -> None:
        """記事データのバリデーション（防御的プログラミング）"""
        if not article_data:
            raise ValueError("Article data is required")
        
        if not article_data.get("id"):
            raise ValueError("Article ID is required")
        
        if not article_data.get("content") or not article_data.get("content").strip():
            raise ValueError("Content is required")
    
    def save_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """記事コンテンツを保存する"""
        self._validate_article_data(article_data)
        
        article_id = article_data["id"]
        
        # フィンガープリント生成
        fingerprint = self.generate_content_fingerprint(article_data["content"])
        
        # バージョン管理
        if article_id in self.articles_storage:
            current_version = self.articles_storage[article_id].get("version", 1)
            new_version = current_version + 1
        else:
            new_version = 1
        
        # 記事データ準備
        saved_article = {
            **article_data,
            "fingerprint": fingerprint,
            "version": new_version,
            "saved_at": datetime.now(),
            "tone_profile": article_data.get("tone_manner_profile", {})
        }
        
        # 保存
        self.articles_storage[article_id] = saved_article
        
        # バージョン履歴に追加
        if article_id not in self.versions_storage:
            self.versions_storage[article_id] = []
        self.versions_storage[article_id].append(saved_article.copy())
        
        return {
            "status": "saved",
            "article_id": article_id,
            "fingerprint": fingerprint,
            "version": new_version,
            "tone_profile": saved_article["tone_profile"]
        }
    
    def generate_content_fingerprint(self, content: str) -> str:
        """コンテンツのフィンガープリントを生成"""
        if not content:
            raise ValueError("Content is required for fingerprinting")
        
        # コンテンツを正規化してハッシュ化
        normalized_content = self.clean_content(content)
        content_hash = hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()
        return content_hash[:16]  # 短縮版
    
    def detect_duplicates(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """重複コンテンツを検出"""
        self._validate_article_data(article_data)
        
        target_content = article_data["content"]
        max_similarity = 0.0
        most_similar_article = None
        
        # 既存記事との類似度を計算
        for stored_id, stored_article in self.articles_storage.items():
            if stored_id != article_data.get("id"):  # 同じ記事は除外
                similarity = self.calculate_similarity(target_content, stored_article["content"])
                if similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_article = stored_article
        
        is_duplicate = max_similarity > self.duplicate_threshold
        
        return {
            "is_duplicate": is_duplicate,
            "similarity_score": max_similarity,
            "most_similar_article": most_similar_article["id"] if most_similar_article else None
        }
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """コンテンツ間の類似度を計算"""
        if not content1 or not content2:
            return 0.0
        
        # クリーンアップ
        clean1 = self.clean_content(content1)
        clean2 = self.clean_content(content2)
        
        # 複数の類似度を計算して組み合わせる
        cosine_sim = self.calculate_cosine_similarity(clean1, clean2)
        jaccard_sim = self._calculate_jaccard_similarity(clean1, clean2)
        character_sim = self._calculate_character_similarity(clean1, clean2)
        
        # 重み付け平均（日本語コンテンツに最適化）
        final_similarity = (
            cosine_sim * 0.5 +           # 単語レベルの類似度
            jaccard_sim * 0.3 +          # 集合の類似度
            character_sim * 0.2          # 文字レベルの類似度
        )
        
        return min(final_similarity, 1.0)  # 1.0を超えないように制限
    
    def calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """コサイン類似度を計算"""
        if not text1 or not text2:
            return 0.0
        
        # 同じテキストの場合
        if text1 == text2:
            return 1.0
        
        # テキストを単語に分割
        words1 = self._tokenize(text1)
        words2 = self._tokenize(text2)
        
        if not words1 or not words2:
            return 0.0
        
        # 単語の出現回数をカウント
        counter1 = Counter(words1)
        counter2 = Counter(words2)
        
        # 共通する単語を取得
        common_words = set(counter1.keys()) & set(counter2.keys())
        
        if not common_words:
            return 0.0
        
        # コサイン類似度を計算
        dot_product = sum(counter1[word] * counter2[word] for word in common_words)
        magnitude1 = math.sqrt(sum(count ** 2 for count in counter1.values()))
        magnitude2 = math.sqrt(sum(count ** 2 for count in counter2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _tokenize(self, text: str) -> List[str]:
        """テキストを単語に分割"""
        # 日本語と英語の両方に対応した簡易トークナイザー
        # 英数字、ひらがな、カタカナ、漢字を単語として抽出
        words = re.findall(r'[a-zA-Z0-9]+|[ぁ-んァ-ン一-龯]+', text.lower())
        return [word for word in words if len(word) > 1]  # 1文字の単語は除外
    
    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Jaccard係数を計算"""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _calculate_character_similarity(self, text1: str, text2: str) -> float:
        """文字レベルの類似度を計算（日本語に特化）"""
        if not text1 or not text2:
            return 0.0
        
        # 文字ベースのn-gram（2-gram）を使用
        ngrams1 = self._generate_character_ngrams(text1, n=2)
        ngrams2 = self._generate_character_ngrams(text2, n=2)
        
        if not ngrams1 and not ngrams2:
            return 1.0
        
        common_ngrams = ngrams1 & ngrams2
        total_ngrams = ngrams1 | ngrams2
        
        if not total_ngrams:
            return 0.0
        
        return len(common_ngrams) / len(total_ngrams)
    
    def _generate_character_ngrams(self, text: str, n: int = 2) -> Set[str]:
        """文字のn-gramを生成"""
        # 日本語文字のみを抽出
        japanese_chars = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', text)
        
        if len(japanese_chars) < n:
            return set([japanese_chars]) if japanese_chars else set()
        
        ngrams = set()
        for i in range(len(japanese_chars) - n + 1):
            ngrams.add(japanese_chars[i:i + n])
        
        return ngrams
    
    def set_duplicate_threshold(self, threshold: float) -> None:
        """重複判定の閾値を設定"""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.duplicate_threshold = threshold
    
    def check_duplicate_alert(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """重複アラートをチェック"""
        duplicate_result = self.detect_duplicates(article_data)
        
        alert_triggered = duplicate_result["similarity_score"] > self.duplicate_threshold
        threshold_exceeded = duplicate_result["similarity_score"] > self.duplicate_threshold
        
        similar_articles = []
        if alert_triggered and duplicate_result["most_similar_article"]:
            similar_articles.append({
                "article_id": duplicate_result["most_similar_article"],
                "similarity_score": duplicate_result["similarity_score"]
            })
        
        return {
            "alert_triggered": alert_triggered,
            "threshold_exceeded": threshold_exceeded,
            "similar_articles": similar_articles,
            "threshold": self.duplicate_threshold
        }
    
    def get_article_versions(self, article_id: str) -> List[Dict[str, Any]]:
        """記事のバージョン履歴を取得"""
        if not article_id:
            raise ValueError("Article ID is required")
        
        return self.versions_storage.get(article_id, [])
    
    def get_article(self, article_id: str) -> Dict[str, Any]:
        """記事を取得"""
        if not article_id:
            raise ValueError("Article ID is required")
        
        article = self.articles_storage.get(article_id)
        if not article:
            raise ValueError(f"Article with ID {article_id} not found")
        
        return article
    
    def search_similar_articles(self, query: str, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """類似記事を検索"""
        if not query:
            raise ValueError("Query is required")
        
        similar_articles = []
        
        for article_id, article in self.articles_storage.items():
            similarity = self.calculate_similarity(query, article["content"])
            if similarity >= threshold:
                similar_articles.append({
                    "article_id": article_id,
                    "title": article.get("title", ""),
                    "similarity_score": similarity,
                    "content_preview": article["content"][:100] + "..." if len(article["content"]) > 100 else article["content"]
                })
        
        # 類似度の高い順にソート
        similar_articles.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return similar_articles
    
    def clean_content(self, content: str) -> str:
        """コンテンツをクリーンアップ"""
        if not content:
            return ""
        
        # 余分な空白や改行を除去
        cleaned = re.sub(r'\s+', ' ', content.strip())
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        
        return cleaned
    
    def batch_duplicate_check(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """一括重複チェック"""
        if not articles:
            raise ValueError("Articles list is required")
        
        duplicate_pairs = []
        total_articles = len(articles)
        
        # 全ての記事ペアで類似度をチェック
        for i in range(total_articles):
            for j in range(i + 1, total_articles):
                article1 = articles[i]
                article2 = articles[j]
                
                similarity = self.calculate_similarity(
                    article1.get("content", ""),
                    article2.get("content", "")
                )
                
                if similarity > self.duplicate_threshold:
                    duplicate_pairs.append({
                        "article1_id": article1.get("id", f"index_{i}"),
                        "article2_id": article2.get("id", f"index_{j}"),
                        "similarity_score": similarity
                    })
        
        return {
            "total_articles": total_articles,
            "duplicate_pairs": duplicate_pairs,
            "duplicate_count": len(duplicate_pairs),
            "threshold": self.duplicate_threshold
        }