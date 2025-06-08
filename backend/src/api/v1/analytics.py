"""Analytics API endpoints."""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, case, text

from src.api.deps import get_db, get_current_user
from src.models.article import Article, ArticleStatus, ContentType
from src.models.user import User
from src.schemas.content import ArticleAnalytics


router = APIRouter()


def calculate_performance_score(article: Article) -> float:
    """Calculate overall performance score for an article."""
    score = 0.0
    
    # Page views (30% weight)
    if article.page_views > 0:
        page_view_score = min(100, (article.page_views / 1000) * 30)
        score += page_view_score
    
    # SEO score (25% weight)
    if article.seo_score:
        score += (article.seo_score / 100) * 25
    
    # Engagement metrics (25% weight)
    engagement_score = 0
    if article.bounce_rate is not None:
        engagement_score += (1 - article.bounce_rate) * 12.5
    if article.average_time_on_page is not None:
        # Good time on page is 2+ minutes
        time_score = min(12.5, (article.average_time_on_page / 120) * 12.5)
        engagement_score += time_score
    score += engagement_score
    
    # Conversion rate (20% weight)
    if article.conversion_rate is not None:
        conversion_score = (article.conversion_rate * 100) * 20
        score += conversion_score
    
    return min(100.0, score)


@router.get("/summary")
async def get_analytics_summary(
    days: Optional[int] = Query(None, description="Number of days to analyze"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics summary."""
    
    # Build date filter
    query = db.query(Article).filter(Article.author_id == current_user.id)
    
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Article.published_at >= cutoff_date)
    elif start_date and end_date:
        query = query.filter(
            and_(
                Article.published_at >= start_date,
                Article.published_at <= end_date
            )
        )
    
    # Get articles
    articles = query.filter(Article.status == ArticleStatus.PUBLISHED).all()
    
    if not articles:
        return {
            "total_articles": 0,
            "total_page_views": 0,
            "total_unique_visitors": 0,
            "average_seo_score": 0,
            "average_bounce_rate": 0,
            "top_performing_articles": [],
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None,
                "days": days
            }
        }
    
    # Calculate summary metrics
    total_page_views = sum(article.page_views for article in articles)
    total_unique_visitors = sum(article.unique_visitors for article in articles)
    
    seo_scores = [article.seo_score for article in articles if article.seo_score is not None]
    avg_seo_score = sum(seo_scores) / len(seo_scores) if seo_scores else 0
    
    bounce_rates = [article.bounce_rate for article in articles if article.bounce_rate is not None]
    avg_bounce_rate = sum(bounce_rates) / len(bounce_rates) if bounce_rates else 0
    
    # Top performing articles
    articles_with_scores = [
        {
            "id": article.id,
            "title": article.title,
            "page_views": article.page_views,
            "seo_score": article.seo_score,
            "performance_score": calculate_performance_score(article)
        }
        for article in articles
    ]
    
    top_articles = sorted(
        articles_with_scores,
        key=lambda x: x["performance_score"],
        reverse=True
    )[:5]
    
    return {
        "total_articles": len(articles),
        "total_page_views": total_page_views,
        "total_unique_visitors": total_unique_visitors,
        "average_seo_score": round(avg_seo_score, 1),
        "average_bounce_rate": round(avg_bounce_rate, 3),
        "top_performing_articles": top_articles,
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None,
            "days": days
        }
    }


@router.post("/compare")
async def compare_articles(
    comparison_request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare performance of multiple articles."""
    
    article_ids = comparison_request.get("article_ids", [])
    
    if not article_ids or len(article_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 article IDs required for comparison"
        )
    
    articles = db.query(Article).filter(
        and_(
            Article.id.in_(article_ids),
            Article.author_id == current_user.id
        )
    ).all()
    
    if len(articles) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough articles found for comparison"
        )
    
    comparison_data = []
    for article in articles:
        performance_metrics = {
            "page_views": article.page_views,
            "unique_visitors": article.unique_visitors,
            "seo_score": article.seo_score,
            "bounce_rate": article.bounce_rate,
            "average_time_on_page": article.average_time_on_page,
            "conversion_rate": article.conversion_rate,
            "performance_score": calculate_performance_score(article)
        }
        
        comparison_data.append({
            "id": article.id,
            "title": article.title,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "performance_metrics": performance_metrics
        })
    
    return {
        "comparison": comparison_data,
        "insights": {
            "best_performing": max(comparison_data, key=lambda x: x["performance_metrics"]["performance_score"]),
            "highest_traffic": max(comparison_data, key=lambda x: x["performance_metrics"]["page_views"]),
            "best_seo": max(comparison_data, key=lambda x: x["performance_metrics"]["seo_score"] or 0)
        }
    }


@router.get("/trends")
async def get_trend_analysis(
    start_date: datetime = Query(..., description="Start date for trend analysis"),
    end_date: datetime = Query(..., description="End date for trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend analysis over time."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.published_at >= start_date,
            Article.published_at <= end_date,
            Article.status == ArticleStatus.PUBLISHED
        )
    ).order_by(Article.published_at).all()
    
    # Group articles by week
    weekly_data = {}
    for article in articles:
        if article.published_at:
            week_start = article.published_at.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = week_start - timedelta(days=week_start.weekday())
            week_key = week_start.isoformat()
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "articles_published": 0,
                    "total_page_views": 0,
                    "total_unique_visitors": 0,
                    "total_conversions": 0,
                    "avg_seo_score": 0,
                    "seo_scores": []
                }
            
            weekly_data[week_key]["articles_published"] += 1
            weekly_data[week_key]["total_page_views"] += article.page_views
            weekly_data[week_key]["total_unique_visitors"] += article.unique_visitors
            
            if article.conversion_rate:
                weekly_data[week_key]["total_conversions"] += article.page_views * article.conversion_rate
            
            if article.seo_score:
                weekly_data[week_key]["seo_scores"].append(article.seo_score)
    
    # Calculate averages
    for week_data in weekly_data.values():
        if week_data["seo_scores"]:
            week_data["avg_seo_score"] = sum(week_data["seo_scores"]) / len(week_data["seo_scores"])
        del week_data["seo_scores"]  # Remove raw scores from output
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "trends": {
            "metrics": weekly_data,
            "summary": {
                "total_weeks": len(weekly_data),
                "avg_articles_per_week": sum(w["articles_published"] for w in weekly_data.values()) / len(weekly_data) if weekly_data else 0,
                "total_page_views": sum(w["total_page_views"] for w in weekly_data.values()),
                "total_unique_visitors": sum(w["total_unique_visitors"] for w in weekly_data.values())
            }
        }
    }


@router.get("/seo-performance")
async def get_seo_performance_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get SEO performance analysis."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED,
            Article.seo_score.isnot(None)
        )
    ).all()
    
    if not articles:
        return {
            "seo_analysis": {
                "average_seo_score": 0,
                "score_distribution": {},
                "improvement_suggestions": []
            }
        }
    
    seo_scores = [article.seo_score for article in articles]
    avg_score = sum(seo_scores) / len(seo_scores)
    
    # Score distribution
    score_ranges = {
        "excellent (90-100)": 0,
        "good (70-89)": 0,
        "fair (50-69)": 0,
        "poor (0-49)": 0
    }
    
    for score in seo_scores:
        if score >= 90:
            score_ranges["excellent (90-100)"] += 1
        elif score >= 70:
            score_ranges["good (70-89)"] += 1
        elif score >= 50:
            score_ranges["fair (50-69)"] += 1
        else:
            score_ranges["poor (0-49)"] += 1
    
    # Generate improvement suggestions
    suggestions = []
    if avg_score < 70:
        suggestions.append("Consider improving meta descriptions and title optimization")
    if avg_score < 80:
        suggestions.append("Focus on increasing content length and keyword density")
    if score_ranges["poor (0-49)"] > 0:
        suggestions.append("Review and optimize poorly performing articles")
    
    return {
        "seo_analysis": {
            "average_seo_score": round(avg_score, 1),
            "score_distribution": score_ranges,
            "improvement_suggestions": suggestions,
            "top_seo_articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "seo_score": article.seo_score
                }
                for article in sorted(articles, key=lambda x: x.seo_score, reverse=True)[:5]
            ]
        }
    }


@router.get("/content-performance")
async def get_content_performance_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get content performance analysis by type and characteristics."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED
        )
    ).all()
    
    # Performance by content type
    by_content_type = {}
    for article in articles:
        content_type = article.content_type.value
        if content_type not in by_content_type:
            by_content_type[content_type] = {
                "count": 0,
                "total_page_views": 0,
                "avg_seo_score": 0,
                "seo_scores": []
            }
        
        by_content_type[content_type]["count"] += 1
        by_content_type[content_type]["total_page_views"] += article.page_views
        if article.seo_score:
            by_content_type[content_type]["seo_scores"].append(article.seo_score)
    
    # Calculate averages
    for type_data in by_content_type.values():
        if type_data["seo_scores"]:
            type_data["avg_seo_score"] = sum(type_data["seo_scores"]) / len(type_data["seo_scores"])
        del type_data["seo_scores"]
    
    # Performance by word count range
    by_word_count = {
        "short (0-500)": {"count": 0, "total_page_views": 0, "avg_performance": 0, "scores": []},
        "medium (501-1500)": {"count": 0, "total_page_views": 0, "avg_performance": 0, "scores": []},
        "long (1501+)": {"count": 0, "total_page_views": 0, "avg_performance": 0, "scores": []}
    }
    
    for article in articles:
        if article.word_count <= 500:
            category = "short (0-500)"
        elif article.word_count <= 1500:
            category = "medium (501-1500)"
        else:
            category = "long (1501+)"
        
        by_word_count[category]["count"] += 1
        by_word_count[category]["total_page_views"] += article.page_views
        performance_score = calculate_performance_score(article)
        by_word_count[category]["scores"].append(performance_score)
    
    # Calculate averages for word count ranges
    for category_data in by_word_count.values():
        if category_data["scores"]:
            category_data["avg_performance"] = sum(category_data["scores"]) / len(category_data["scores"])
        del category_data["scores"]
    
    return {
        "content_performance": {
            "by_content_type": by_content_type,
            "by_word_count_range": by_word_count
        }
    }


@router.get("/engagement")
async def get_user_engagement_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user engagement metrics."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED
        )
    ).all()
    
    # Calculate engagement metrics
    time_on_page_values = [a.average_time_on_page for a in articles if a.average_time_on_page is not None]
    bounce_rate_values = [a.bounce_rate for a in articles if a.bounce_rate is not None]
    
    avg_time_on_page = sum(time_on_page_values) / len(time_on_page_values) if time_on_page_values else 0
    avg_bounce_rate = sum(bounce_rate_values) / len(bounce_rate_values) if bounce_rate_values else 0
    
    # Page depth analysis (based on content length and engagement)
    page_depth_score = 0
    if articles:
        total_words = sum(a.word_count for a in articles)
        avg_words = total_words / len(articles)
        
        # Higher word count generally indicates deeper content
        if avg_words > 1000:
            page_depth_score = 3  # Deep
        elif avg_words > 500:
            page_depth_score = 2  # Medium
        else:
            page_depth_score = 1  # Shallow
    
    return {
        "engagement_metrics": {
            "average_time_on_page": round(avg_time_on_page, 1),
            "bounce_rate": round(avg_bounce_rate, 3),
            "page_depth": {
                "score": page_depth_score,
                "average_word_count": round(sum(a.word_count for a in articles) / len(articles) if articles else 0)
            },
            "engagement_quality": "high" if avg_time_on_page > 120 and avg_bounce_rate < 0.4 else "medium" if avg_time_on_page > 60 else "low"
        }
    }


@router.get("/conversions")
async def get_conversion_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversion analysis."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED
        )
    ).all()
    
    # Calculate conversion metrics
    total_conversions = 0
    total_page_views = sum(a.page_views for a in articles)
    
    converting_articles = []
    for article in articles:
        if article.conversion_rate and article.conversion_rate > 0:
            conversions = article.page_views * article.conversion_rate
            total_conversions += conversions
            converting_articles.append({
                "id": article.id,
                "title": article.title,
                "page_views": article.page_views,
                "conversion_rate": article.conversion_rate,
                "conversions": round(conversions, 2)
            })
    
    overall_conversion_rate = total_conversions / total_page_views if total_page_views > 0 else 0
    
    # Top converting articles
    top_converting = sorted(
        converting_articles,
        key=lambda x: x["conversions"],
        reverse=True
    )[:5]
    
    return {
        "conversion_analysis": {
            "total_conversions": round(total_conversions, 2),
            "conversion_rate": round(overall_conversion_rate, 4),
            "converting_articles_count": len(converting_articles),
            "top_converting_articles": top_converting
        }
    }


@router.get("/keywords")
async def get_keyword_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get keyword performance analysis."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED,
            Article.target_keywords.isnot(None)
        )
    ).all()
    
    # Aggregate keyword data
    keyword_performance = {}
    
    for article in articles:
        if article.target_keywords:
            keywords = [kw.strip() for kw in article.target_keywords.split(',')]
            for keyword in keywords:
                if keyword not in keyword_performance:
                    keyword_performance[keyword] = {
                        "articles_count": 0,
                        "total_page_views": 0,
                        "avg_seo_score": 0,
                        "seo_scores": []
                    }
                
                keyword_performance[keyword]["articles_count"] += 1
                keyword_performance[keyword]["total_page_views"] += article.page_views
                if article.seo_score:
                    keyword_performance[keyword]["seo_scores"].append(article.seo_score)
    
    # Calculate averages and sort
    top_keywords = []
    for keyword, data in keyword_performance.items():
        if data["seo_scores"]:
            data["avg_seo_score"] = sum(data["seo_scores"]) / len(data["seo_scores"])
        
        top_keywords.append({
            "keyword": keyword,
            "articles_count": data["articles_count"],
            "total_page_views": data["total_page_views"],
            "avg_seo_score": round(data["avg_seo_score"], 1)
        })
    
    # Sort by page views
    top_keywords.sort(key=lambda x: x["total_page_views"], reverse=True)
    
    return {
        "keyword_analysis": {
            "total_keywords": len(keyword_performance),
            "top_keywords": top_keywords[:10],
            "keyword_trends": {
                "most_used": max(keyword_performance.items(), key=lambda x: x[1]["articles_count"])[0] if keyword_performance else None,
                "highest_traffic": max(keyword_performance.items(), key=lambda x: x[1]["total_page_views"])[0] if keyword_performance else None
            }
        }
    }


@router.get("/competitive")
async def get_competitive_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get competitive analysis."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED
        )
    ).all()
    
    if not articles:
        return {
            "competitive_analysis": {
                "market_position": "unknown",
                "opportunities": []
            }
        }
    
    # Simple competitive analysis based on internal metrics
    avg_seo_score = sum(a.seo_score for a in articles if a.seo_score) / len([a for a in articles if a.seo_score])
    avg_page_views = sum(a.page_views for a in articles) / len(articles)
    avg_bounce_rate = sum(a.bounce_rate for a in articles if a.bounce_rate) / len([a for a in articles if a.bounce_rate])
    
    # Determine market position based on metrics
    if avg_seo_score > 80 and avg_page_views > 2000:
        market_position = "strong"
    elif avg_seo_score > 60 and avg_page_views > 1000:
        market_position = "competitive"
    else:
        market_position = "developing"
    
    # Generate opportunities
    opportunities = []
    if avg_seo_score < 70:
        opportunities.append("Improve SEO optimization across all content")
    if avg_page_views < 1000:
        opportunities.append("Focus on traffic generation and promotion")
    if avg_bounce_rate > 0.6:
        opportunities.append("Enhance content engagement and user experience")
    
    return {
        "competitive_analysis": {
            "market_position": market_position,
            "performance_metrics": {
                "avg_seo_score": round(avg_seo_score, 1),
                "avg_page_views": round(avg_page_views),
                "avg_bounce_rate": round(avg_bounce_rate, 3)
            },
            "opportunities": opportunities
        }
    }


@router.get("/export")
async def export_analytics_report(
    format: str = Query("json", description="Export format (json, csv)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export comprehensive analytics report."""
    
    articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED
        )
    ).all()
    
    # Generate comprehensive report
    report_data = {
        "summary": {
            "total_articles": len(articles),
            "total_page_views": sum(a.page_views for a in articles),
            "total_unique_visitors": sum(a.unique_visitors for a in articles),
            "avg_seo_score": sum(a.seo_score for a in articles if a.seo_score) / len([a for a in articles if a.seo_score]) if articles else 0
        },
        "detailed_metrics": [
            {
                "id": article.id,
                "title": article.title,
                "page_views": article.page_views,
                "unique_visitors": article.unique_visitors,
                "seo_score": article.seo_score,
                "bounce_rate": article.bounce_rate,
                "conversion_rate": article.conversion_rate,
                "performance_score": calculate_performance_score(article),
                "published_at": article.published_at.isoformat() if article.published_at else None
            }
            for article in articles
        ]
    }
    
    return {
        "report": report_data,
        "generated_at": datetime.utcnow().isoformat(),
        "format": format,
        "user_id": current_user.id
    }


@router.get("/real-time")
async def get_real_time_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time metrics (simulated for demo)."""
    
    # In a real implementation, this would connect to real-time analytics
    recent_articles = db.query(Article).filter(
        and_(
            Article.author_id == current_user.id,
            Article.status == ArticleStatus.PUBLISHED,
            Article.published_at >= datetime.utcnow() - timedelta(days=7)
        )
    ).order_by(desc(Article.page_views)).limit(5).all()
    
    return {
        "real_time_metrics": {
            "active_users": 42,  # Simulated
            "current_page_views": sum(a.page_views for a in recent_articles),
            "trending_articles": [
                {
                    "id": article.id,
                    "title": article.title,
                    "current_views": article.page_views
                }
                for article in recent_articles
            ]
        }
    }