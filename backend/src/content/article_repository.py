"""
Article Repository
記事リポジトリ - データベース永続化層

TDD Green Phase: テストを通す最小限の実装
SQLAlchemy ArticleモデルとのCRUD操作を提供
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# ArticleモデルとEnumsをインポート
from ..models.article import Article, ArticleStatus, ContentType

logger = logging.getLogger(__name__)


class ArticleRepository:
    """
    記事リポジトリクラス
    
    SQLAlchemy Articleモデルを使用したデータベース永続化層
    単一責任原則: データアクセスのみに特化
    """
    
    def __init__(self, db_session: Session):
        """
        リポジトリの初期化
        
        Args:
            db_session: SQLAlchemyのデータベースセッション
        """
        self.db = db_session
    
    def save(self, article_data: Dict[str, Any]) -> Article:
        """
        記事をデータベースに保存
        
        Args:
            article_data: 記事データ辞書
            
        Returns:
            Article: 保存された記事オブジェクト
            
        Raises:
            ValueError: 必須フィールドが不足している場合
            SQLAlchemyError: データベースエラー
        """
        try:
            # バリデーションとArticle作成を分離（単一責任原則）
            self._validate_article_data(article_data)
            article = self._create_article_from_data(article_data)
            
            # データベースに保存
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            
            logger.info(f"Article saved successfully: ID={article.id}, Title='{article.title}'")
            return article
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while saving article: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error while saving article: {e}")
            raise
    
    def _validate_article_data(self, article_data: Dict[str, Any]) -> None:
        """
        記事データのバリデーション（防御的プログラミング）
        
        Args:
            article_data: 検証する記事データ
            
        Raises:
            ValueError: バリデーションエラー
        """
        required_fields = ["title", "author_id"]
        
        for field in required_fields:
            if not article_data.get(field):
                raise ValueError(f"{field} is required")
    
    def _create_article_from_data(self, article_data: Dict[str, Any]) -> Article:
        """
        記事データからArticleオブジェクトを作成
        
        Args:
            article_data: 記事データ辞書
            
        Returns:
            Article: 作成されたArticleオブジェクト
        """
        return Article(
            title=article_data["title"],
            slug=article_data.get("slug"),
            content=article_data.get("content"),
            excerpt=article_data.get("excerpt"),
            meta_title=article_data.get("meta_title"),
            meta_description=article_data.get("meta_description"),
            meta_keywords=article_data.get("meta_keywords"),
            content_type=ContentType(article_data.get("content_type", "BLOG_POST")),
            status=ArticleStatus(article_data.get("status", "DRAFT")),
            target_keywords=article_data.get("target_keywords"),
            ai_generated=article_data.get("ai_generated", False),
            ai_model_used=article_data.get("ai_model_used"),
            author_id=article_data["author_id"],
            project_id=article_data.get("project_id"),
            word_count=self._calculate_word_count(article_data.get("content", ""))
        )
    
    def _calculate_word_count(self, content: str) -> int:
        """
        コンテンツの単語数を計算
        
        Args:
            content: 計算対象のコンテンツ
            
        Returns:
            int: 単語数
        """
        return len(content.split()) if content else 0
    
    def find_by_id(self, article_id: int) -> Optional[Article]:
        """
        IDによる記事検索
        
        Args:
            article_id: 記事ID
            
        Returns:
            Optional[Article]: 見つかった記事、または None
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()
            return article
        except SQLAlchemyError as e:
            logger.error(f"Database error while finding article by ID {article_id}: {e}")
            return None
    
    def find_by_title(self, title: str) -> List[Article]:
        """
        タイトルによる記事検索（部分一致）
        
        Args:
            title: 検索タイトル
            
        Returns:
            List[Article]: 見つかった記事のリスト
        """
        try:
            articles = self.db.query(Article).filter(
                Article.title.ilike(f"%{title}%")
            ).all()
            return articles
        except SQLAlchemyError as e:
            logger.error(f"Database error while finding articles by title '{title}': {e}")
            return []
    
    def find_all(self) -> List[Article]:
        """
        全記事取得
        
        Returns:
            List[Article]: 全記事のリスト
        """
        try:
            articles = self.db.query(Article).all()
            return articles
        except SQLAlchemyError as e:
            logger.error(f"Database error while finding all articles: {e}")
            return []
    
    def update(self, article_id: int, update_data: Dict[str, Any]) -> Optional[Article]:
        """
        記事更新
        
        Args:
            article_id: 更新対象の記事ID
            update_data: 更新データ辞書
            
        Returns:
            Optional[Article]: 更新された記事、または None
        """
        try:
            article = self.find_by_id(article_id)
            if not article:
                return None
            
            # 更新処理をヘルパーメソッドに抽出（単一責任原則）
            self._update_article_fields(article, update_data)
            
            # 更新日時を設定
            article.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(article)
            
            logger.info(f"Article updated successfully: ID={article.id}")
            return article
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while updating article {article_id}: {e}")
            return None
    
    def _update_article_fields(self, article: Article, update_data: Dict[str, Any]) -> None:
        """
        記事フィールドの更新（プライベートヘルパーメソッド）
        
        Args:
            article: 更新対象の記事オブジェクト
            update_data: 更新データ辞書
        """
        # 更新可能なフィールドのマッピング
        updatable_fields = {
            'title', 'slug', 'content', 'excerpt', 'meta_title', 
            'meta_description', 'meta_keywords', 'target_keywords', 'word_count'
        }
        
        enum_fields = {
            'content_type': ContentType,
            'status': ArticleStatus
        }
        
        # 通常フィールドの更新
        for field in updatable_fields:
            if field in update_data:
                setattr(article, field, update_data[field])
        
        # Enumフィールドの更新
        for field, enum_class in enum_fields.items():
            if field in update_data:
                setattr(article, field, enum_class(update_data[field]))
    
    def delete(self, article_id: int) -> bool:
        """
        記事削除
        
        Args:
            article_id: 削除対象の記事ID
            
        Returns:
            bool: 削除成功時 True、失敗時 False
        """
        try:
            article = self.find_by_id(article_id)
            if not article:
                return False
            
            self.db.delete(article)
            self.db.commit()
            
            logger.info(f"Article deleted successfully: ID={article_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error while deleting article {article_id}: {e}")
            return False
    
    def search_by_content(self, query: str) -> List[Article]:
        """
        コンテンツ全文検索
        
        Args:
            query: 検索クエリ
            
        Returns:
            List[Article]: 見つかった記事のリスト
        """
        try:
            articles = self.db.query(Article).filter(
                Article.content.ilike(f"%{query}%")
            ).all()
            return articles
        except SQLAlchemyError as e:
            logger.error(f"Database error while searching content for '{query}': {e}")
            return []
    
    def find_by_status(self, status: Union[str, ArticleStatus]) -> List[Article]:
        """
        ステータス別記事取得
        
        Args:
            status: 記事ステータス
            
        Returns:
            List[Article]: 指定ステータスの記事リスト
        """
        try:
            if isinstance(status, str):
                status = ArticleStatus(status)
            
            articles = self.db.query(Article).filter(
                Article.status == status
            ).all()
            return articles
        except SQLAlchemyError as e:
            logger.error(f"Database error while finding articles by status '{status}': {e}")
            return []
    
    def find_by_author(self, author_id: int) -> List[Article]:
        """
        著者別記事取得
        
        Args:
            author_id: 著者ID
            
        Returns:
            List[Article]: 指定著者の記事リスト
        """
        try:
            articles = self.db.query(Article).filter(
                Article.author_id == author_id
            ).all()
            return articles
        except SQLAlchemyError as e:
            logger.error(f"Database error while finding articles by author {author_id}: {e}")
            return []
    
    def bulk_save(self, articles_data: List[Dict[str, Any]]) -> List[Article]:
        """
        一括記事保存
        
        Args:
            articles_data: 記事データのリスト
            
        Returns:
            List[Article]: 保存された記事のリスト
        """
        saved_articles = []
        try:
            for article_data in articles_data:
                article = self.save(article_data)
                saved_articles.append(article)
            
            logger.info(f"Bulk save completed: {len(saved_articles)} articles saved")
            return saved_articles
            
        except Exception as e:
            # 部分的な失敗の場合もロールバック
            self.db.rollback()
            logger.error(f"Bulk save failed: {e}")
            raise
    
    def create_version(self, article_id: int, updated_content: str) -> Dict[str, Any]:
        """
        記事のバージョン作成
        
        Args:
            article_id: 元記事のID
            updated_content: 更新されたコンテンツ
            
        Returns:
            Dict[str, Any]: バージョン情報
        """
        try:
            parent_article = self.find_by_id(article_id)
            if not parent_article:
                raise ValueError(f"Parent article with ID {article_id} not found")
            
            # 新バージョンとして新しい記事を作成
            version_data = {
                "title": parent_article.title,
                "content": updated_content,
                "author_id": parent_article.author_id,
                "project_id": parent_article.project_id,
                "status": "DRAFT"  # バージョンは常にドラフトとして作成
            }
            
            new_version = self.save(version_data)
            
            # 親記事との関連を設定
            new_version.parent_id = article_id
            new_version.version = parent_article.version + 1
            self.db.commit()
            
            return {
                "version": new_version.version,
                "parent_id": article_id,
                "new_article_id": new_version.id
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating version for article {article_id}: {e}")
            raise


class ArticleRepositoryError(Exception):
    """ArticleRepository専用例外クラス"""
    pass