"""
SEO Research API endpoints - Integrated with LangGraph workflow
"""
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.deps import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.agent.seo_research_graph import run_seo_research


router = APIRouter(prefix="/seo-research", tags=["seo-research"])


class SEOResearchRequest(BaseModel):
    primary_keyword: str
    target_audience: str = "一般ユーザー"
    research_depth: str = "standard"  # light, standard, deep
    include_competitors: bool = True
    include_content_gaps: bool = True


class SEOResearchResponse(BaseModel):
    research_id: str
    status: str
    primary_keyword: str
    target_audience: str
    keyword_data: Optional[Dict[str, Any]] = None
    competitor_data: Optional[list] = None
    content_gaps: Optional[list] = None
    seo_recommendations: Optional[list] = None
    seo_insights: Optional[str] = None
    generated_at: Optional[str] = None
    processing_time: Optional[float] = None


# In-memory storage for demo (replace with Redis/Database in production)
research_sessions = {}


@router.post("/start", response_model=Dict[str, Any])
async def start_seo_research(
    request: SEOResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new SEO research workflow"""
    
    research_id = f"research_{current_user.id}_{int(datetime.now().timestamp())}"
    
    # Initialize research session
    research_sessions[research_id] = {
        "status": "started",
        "primary_keyword": request.primary_keyword,
        "target_audience": request.target_audience,
        "user_id": current_user.id,
        "started_at": datetime.now().isoformat(),
        "progress": 0
    }
    
    # Run research in background
    background_tasks.add_task(
        execute_seo_research,
        research_id,
        request.primary_keyword,
        request.target_audience
    )
    
    return {
        "research_id": research_id,
        "status": "started",
        "message": f"SEOリサーチを開始しました: {request.primary_keyword}",
        "estimated_time": "2-3分程度"
    }


@router.get("/status/{research_id}")
async def get_research_status(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a research session"""
    
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    session = research_sessions[research_id]
    
    # Check if user owns this research
    if session.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return session


@router.get("/results/{research_id}", response_model=SEOResearchResponse)
async def get_research_results(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the complete results of a research session"""
    
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    session = research_sessions[research_id]
    
    # Check if user owns this research
    if session.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if session.get("status") != "completed":
        raise HTTPException(
            status_code=425, 
            detail="Research not completed yet. Check status first."
        )
    
    return SEOResearchResponse(**session)


@router.get("/history")
async def get_research_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get user's research history"""
    
    user_sessions = [
        {
            "research_id": rid,
            "primary_keyword": session["primary_keyword"],
            "status": session["status"],
            "started_at": session["started_at"],
            "target_audience": session.get("target_audience", "")
        }
        for rid, session in research_sessions.items()
        if session.get("user_id") == current_user.id
    ]
    
    # Sort by started_at descending
    user_sessions.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "research_sessions": user_sessions[:limit],
        "total_count": len(user_sessions)
    }


@router.delete("/session/{research_id}")
async def delete_research_session(
    research_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a research session"""
    
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="Research session not found")
    
    session = research_sessions[research_id]
    
    # Check if user owns this research
    if session.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del research_sessions[research_id]
    
    return {"message": "Research session deleted successfully"}


async def execute_seo_research(
    research_id: str, 
    primary_keyword: str, 
    target_audience: str
):
    """Execute the SEO research workflow using LangGraph"""
    
    try:
        # Update status
        research_sessions[research_id]["status"] = "processing"
        research_sessions[research_id]["progress"] = 25
        
        start_time = datetime.now()
        
        # Run the LangGraph SEO research workflow
        result = await run_seo_research(
            primary_keyword=primary_keyword,
            target_audience=target_audience
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Update session with results
        research_sessions[research_id].update({
            "status": "completed",
            "progress": 100,
            "keyword_data": result.get("keyword_data"),
            "competitor_data": result.get("competitor_data", []),
            "content_gaps": result.get("content_gaps", []),
            "seo_recommendations": result.get("seo_recommendations", []),
            "seo_insights": result.get("seo_insights"),
            "generated_at": result.get("generated_at"),
            "processing_time": processing_time,
            "completed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        # Update status to error
        research_sessions[research_id].update({
            "status": "error",
            "error_message": str(e),
            "completed_at": datetime.now().isoformat()
        })
        print(f"SEO research failed for {research_id}: {e}")


@router.post("/quick-analysis")
async def quick_seo_analysis(
    request: SEOResearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Quick SEO analysis without full workflow (for testing)"""
    
    try:
        # Simplified analysis for quick results
        from src.seo.keyword_analyzer import KeywordAnalyzer
        
        analyzer = KeywordAnalyzer()
        
        # Basic keyword analysis
        result = await analyzer.analyze_keyword(request.primary_keyword)
        
        # Get related keywords
        related = await analyzer.get_related_keywords(request.primary_keyword)
        
        return {
            "keyword": request.primary_keyword,
            "analysis": result,
            "related_keywords": related[:10],
            "quick_recommendations": [
                "詳細なコンテンツ計画を作成",
                "競合分析を実施",
                "検索意図に沿ったコンテンツ作成",
                "内部リンク戦略を検討"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        )