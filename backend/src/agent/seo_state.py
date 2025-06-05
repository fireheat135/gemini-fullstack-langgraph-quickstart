"""SEO Agent state definitions for LangGraph workflows."""

from dataclasses import dataclass, field
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated

import operator


class SEOResearchState(TypedDict):
    """State for SEO research workflow."""
    topic: str
    keywords: Annotated[List[str], operator.add]
    competitor_urls: Annotated[List[str], operator.add]
    keyword_analysis: Annotated[List[Dict[str, Any]], operator.add]
    competitor_analysis: Annotated[List[Dict[str, Any]], operator.add]
    content_gaps: Annotated[List[Dict[str, Any]], operator.add]
    target_audience: Optional[str]
    search_intent: Optional[str]
    difficulty_score: Optional[float]
    opportunity_score: Optional[float]


class SEOContentState(TypedDict):
    """State for SEO content generation workflow."""
    topic: str
    target_keywords: List[str]
    content_type: str
    target_length: int
    tone: str
    target_audience: str
    competitor_analysis: Optional[Dict[str, Any]]
    outline: Optional[Dict[str, Any]]
    content: Optional[str]
    seo_analysis: Optional[Dict[str, Any]]
    optimized_content: Optional[str]
    meta_title: Optional[str]
    meta_description: Optional[str]
    featured_image_prompt: Optional[str]


class SEOAnalysisState(TypedDict):
    """State for SEO content analysis workflow."""
    content: str
    target_keywords: List[str]
    url: Optional[str]
    readability_score: Optional[float]
    keyword_density: Optional[Dict[str, float]]
    seo_score: Optional[float]
    issues: Annotated[List[str], operator.add]
    suggestions: Annotated[List[str], operator.add]
    strengths: Annotated[List[str], operator.add]
    title_analysis: Optional[Dict[str, Any]]
    meta_analysis: Optional[Dict[str, Any]]
    content_structure: Optional[Dict[str, Any]]


class KeywordResearchState(TypedDict):
    """State for keyword research workflow."""
    seed_keyword: str
    language: str
    country: str
    primary_keywords: Annotated[List[Dict[str, Any]], operator.add]
    related_keywords: Annotated[List[Dict[str, Any]], operator.add]
    long_tail_keywords: Annotated[List[Dict[str, Any]], operator.add]
    competitor_keywords: Annotated[List[Dict[str, Any]], operator.add]
    keyword_clusters: Annotated[List[Dict[str, Any]], operator.add]
    search_volume_data: Optional[Dict[str, Any]]
    competition_data: Optional[Dict[str, Any]]
    trend_data: Optional[Dict[str, Any]]


class CompetitorAnalysisState(TypedDict):
    """State for competitor analysis workflow."""
    target_keyword: str
    competitor_urls: List[str]
    serp_analysis: Optional[Dict[str, Any]]
    content_analysis: Annotated[List[Dict[str, Any]], operator.add]
    backlink_analysis: Annotated[List[Dict[str, Any]], operator.add]
    gap_analysis: Optional[Dict[str, Any]]
    opportunities: Annotated[List[str], operator.add]
    threats: Annotated[List[str], operator.add]
    recommendations: Annotated[List[str], operator.add]


@dataclass(kw_only=True)
class SEOWorkflowOutput:
    """Output container for SEO workflows."""
    workflow_type: str
    success: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


class ImageGenerationState(TypedDict):
    """State for AI image generation workflow."""
    prompt: str
    style: str
    size: str
    article_context: Optional[str]
    generated_images: Annotated[List[Dict[str, Any]], operator.add]
    selected_image: Optional[Dict[str, Any]]
    alt_text: Optional[str]
    optimization_suggestions: Annotated[List[str], operator.add]