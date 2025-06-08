"""
Test configuration and fixtures for SEO Agent platform tests.
"""
import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# FastAPIのインポート
from fastapi.testclient import TestClient
from src.main import app
from src.models.base import Base
from src.core.config import settings
from src.db.session import get_db

# テスト用データベースURL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"

# 環境変数の設定
os.environ["GEMINI_API_KEY"] = "AIzaSyDA5R1ewUtKeO7SE72Ybh5Nn0r11KZ3B74"
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_SYNC_DATABASE_URL, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
async def async_test_db_engine():
    """Create an async test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield engine
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
async def async_test_db_session(
    async_test_db_engine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create an async test database session."""
    SessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_test_db_engine,
        class_=AsyncSession,
    )
    async with SessionLocal() as session:
        yield session


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client."""
    mock = Mock()
    mock.generate_content = AsyncMock(
        return_value=Mock(
            text="# 誕生花テスト記事\n\nこれはテスト用の記事です。"
        )
    )
    return mock


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI API client."""
    mock = Mock()
    mock.chat.completions.create = AsyncMock(
        return_value=Mock(
            choices=[
                Mock(message=Mock(content="テスト画像生成プロンプト"))
            ]
        )
    )
    mock.images.generate = AsyncMock(
        return_value=Mock(
            data=[Mock(url="https://example.com/test-image.png")]
        )
    )
    return mock


@pytest.fixture
def client(test_db_session: Session) -> TestClient:
    """Create a test client for FastAPI app."""
    # Override the database dependency
    def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_api_key():
    """Test API key."""
    return "test-api-key-12345"


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123",
    }


@pytest.fixture
def test_article_data():
    """Test article data for 誕生花."""
    return {
        "title": "誕生花で贈る感動を！月別一覧、意味、プレゼント選びの完全ガイド",
        "keywords": ["誕生花", "誕生花 一覧", "誕生花 意味", "誕生花 ギフト"],
        "target_audience": "誕生日プレゼントを探している人",
        "tone": "friendly",
        "length": 3000,
    }


@pytest.fixture
def mock_langchain_agent():
    """Mock LangChain agent for testing."""
    mock = Mock()
    mock.invoke = AsyncMock(
        return_value={
            "messages": [
                {
                    "role": "assistant",
                    "content": "誕生花の記事を生成しました。",
                }
            ],
            "article": {
                "title": "誕生花で贈る感動を！",
                "content": "誕生花の素晴らしさについて...",
                "meta_description": "誕生花の意味と選び方",
            },
        }
    )
    return mock


# TDD原則: テストヘルパー関数
async def create_test_user(session: AsyncSession, user_data: dict):
    """Create a test user in the database."""
    # User モデルの実装後に有効化
    pass


async def create_test_article(session: AsyncSession, article_data: dict):
    """Create a test article in the database."""
    # Article モデルの実装後に有効化
    pass


class TestDataGenerator:
    """Test data generator for TDD."""
    
    @staticmethod
    def generate_seo_article_data(scenario="normal"):
        """Generate test data for SEO articles based on scenario."""
        if scenario == "normal":
            return {
                "title": "誕生花で贈る感動を！月別一覧",
                "keywords": ["誕生花", "誕生花 一覧"],
                "content_length": 2000,
                "tone": "friendly",
            }
        elif scenario == "edge_case":
            return {
                "title": "あ" * 100,  # 最大長テスト
                "keywords": ["🌸", "花-2024", "テスト_123"],
                "content_length": 10000,  # 大容量
                "tone": "professional",
            }
        elif scenario == "birth_flower_specific":
            return {
                "title": "1月の誕生花スイートピーの魅力",
                "keywords": ["1月 誕生花", "スイートピー", "花言葉"],
                "content_length": 3000,
                "tone": "informative",
                "specific_flowers": ["スイートピー", "カーネーション"],
            }