"""
Keyword Research API endpoints
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.deps import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.models.api_key import APIKey, APIProvider
from src.services.ai.ai_service_manager import AIServiceManager
from src.seo.keyword_analyzer import KeywordAnalyzer
from src.seo.competitor_analyzer import CompetitorAnalyzer
from src.seo.trend_analyzer import TrendAnalyzer
from src.core.rate_limiter import RateLimiter


router = APIRouter(prefix="/keywords", tags=["keywords"])
rate_limiter = RateLimiter(max_calls=10, time_window=60)  # 10 calls per minute


class KeywordAnalysisRequest(BaseModel):
    keyword: str
    include_trends: bool = True
    include_related: bool = True
    include_competitors: bool = False


class BulkKeywordRequest(BaseModel):
    keywords: List[str]


class CompetitorAnalysisRequest(BaseModel):
    keyword: str
    top_n: int = 10


class KeywordClusterRequest(BaseModel):
    keywords: List[str]


class TrendAnalysisRequest(BaseModel):
    keyword: str
    timeframe: str = "12_months"  # 3_months, 6_months, 12_months, 5_years


class KeywordSuggestionRequest(BaseModel):
    seed_keyword: str
    target_audience: str
    content_type: str
    suggestion_count: int = 10


class KeywordDifficultyRequest(BaseModel):
    keyword: str
    include_breakdown: bool = False


async def get_ai_service(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AIServiceManager:
    """Get AI service manager for current user"""
    # Check if user has API key configured
    api_key = db.query(APIKey).filter(
        APIKey.user_id == current_user.id,
        APIKey.provider == APIProvider.GOOGLE_GEMINI,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="API key not configured. Please add your Google Gemini API key."
        )
    
    return AIServiceManager(db, current_user.id)


@router.post("/analyze")
async def analyze_keyword(
    request: KeywordAnalysisRequest,
    x_client_id: Optional[str] = Header(None),
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a single keyword for SEO metrics"""
    # Rate limiting
    client_id = x_client_id or str(current_user.id)
    if not rate_limiter.check_rate_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_limiter.max_calls),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(rate_limiter.get_reset_time(client_id).timestamp()))
            }
        )
    
    # Initialize analyzer
    analyzer = KeywordAnalyzer(ai_service)
    
    # Perform analysis
    result = await analyzer.analyze_keyword(
        keyword=request.keyword,
        include_trends=request.include_trends,
        include_related=request.include_related,
        include_competitors=request.include_competitors
    )
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining_calls(client_id)
    reset_time = rate_limiter.get_reset_time(client_id)
    
    return {
        **result,
        "_rate_limit": {
            "limit": rate_limiter.max_calls,
            "remaining": remaining,
            "reset": int(reset_time.timestamp())
        }
    }


@router.post("/analyze/bulk")
async def analyze_keywords_bulk(
    request: BulkKeywordRequest,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze multiple keywords in bulk"""
    analyzer = KeywordAnalyzer(ai_service)
    
    results = []
    for keyword in request.keywords:
        try:
            result = await analyzer.analyze_keyword(
                keyword=keyword,
                include_trends=False,
                include_related=False,
                include_competitors=False
            )
            results.append(result)
        except Exception as e:
            results.append({
                "keyword": keyword,
                "error": str(e)
            })
    
    return {"results": results}


@router.post("/competitors")
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze top competitors for a keyword"""
    analyzer = CompetitorAnalyzer(ai_service)
    
    competitors = await analyzer.analyze_competitors(
        keyword=request.keyword,
        top_n=request.top_n
    )
    
    return {
        "keyword": request.keyword,
        "competitors": competitors
    }


@router.post("/cluster")
async def cluster_keywords(
    request: KeywordClusterRequest,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cluster keywords into related groups"""
    analyzer = KeywordAnalyzer(ai_service)
    
    clusters = await analyzer.cluster_keywords(request.keywords)
    
    return {"clusters": clusters}


@router.post("/trends")
async def analyze_trends(
    request: TrendAnalysisRequest,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze search trends for a keyword"""
    analyzer = TrendAnalyzer(ai_service)
    
    trend_data = await analyzer.analyze_trend(
        keyword=request.keyword,
        timeframe=request.timeframe
    )
    
    return {
        "keyword": request.keyword,
        "trend_data": trend_data
    }


@router.post("/import/csv")
async def import_keywords_csv(
    file: UploadFile = File(...),
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import keywords from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")
    
    contents = await file.read()
    csv_data = csv.DictReader(io.StringIO(contents.decode('utf-8')))
    
    keywords = []
    for row in csv_data:
        keywords.append({
            "keyword": row.get("keyword", ""),
            "search_volume": int(row.get("search_volume", 0)),
            "cpc": float(row.get("cpc", 0))
        })
    
    return {
        "imported_count": len(keywords),
        "keywords": keywords
    }


@router.post("/suggest")
async def suggest_keywords(
    request: KeywordSuggestionRequest,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered keyword suggestions"""
    analyzer = KeywordAnalyzer(ai_service)
    
    suggestions = await analyzer.suggest_keywords(
        seed_keyword=request.seed_keyword,
        target_audience=request.target_audience,
        content_type=request.content_type,
        count=request.suggestion_count
    )
    
    return {"suggestions": suggestions}


@router.get("/{keyword}/history")
async def get_keyword_history(
    keyword: str,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical search volume data for a keyword"""
    analyzer = KeywordAnalyzer(ai_service)
    
    history = await analyzer.get_search_volume_history(keyword)
    
    return {
        "keyword": keyword,
        "history": history
    }


@router.post("/difficulty")
async def calculate_keyword_difficulty(
    request: KeywordDifficultyRequest,
    ai_service: AIServiceManager = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate keyword difficulty score"""
    analyzer = KeywordAnalyzer(ai_service)
    
    difficulty_data = await analyzer.calculate_difficulty(
        keyword=request.keyword,
        include_breakdown=request.include_breakdown
    )
    
    return difficulty_data