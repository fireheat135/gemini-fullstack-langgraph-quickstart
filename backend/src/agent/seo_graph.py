"""SEO-focused LangGraph workflows."""

import os
import re
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .seo_state import (
    SEOResearchState,
    SEOContentState, 
    SEOAnalysisState,
    KeywordResearchState,
    SEOWorkflowOutput
)
from .seo_tools import (
    extract_keywords_from_content,
    analyze_title_seo,
    analyze_meta_description,
    analyze_content_structure,
    calculate_readability_score,
    fetch_competitor_data,
    generate_content_outline,
    SEOAnalysis
)
from .prompts import get_current_date
from .configuration import Configuration


def keyword_research_node(state: KeywordResearchState, config: RunnableConfig) -> KeywordResearchState:
    """Research keywords for SEO optimization."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=0.3,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    prompt = f"""
    As an SEO expert, research keywords related to "{state['seed_keyword']}" for {state['language']} content in {state['country']}.
    
    Provide a comprehensive keyword analysis including:
    1. Primary keywords (high search volume, medium competition)
    2. Related keywords (semantic variations)
    3. Long-tail keywords (low competition, specific intent)
    4. Keyword clusters (grouped by topic/intent)
    
    Focus on keywords that are:
    - Relevant to the seed keyword
    - Have commercial potential
    - Achievable for ranking
    
    Current date: {get_current_date()}
    """
    
    response = llm.invoke(prompt)
    
    # Parse AI response and extract keyword data
    # This is a simplified version - in production, you'd use structured output
    primary_keywords = [
        {"keyword": f"{state['seed_keyword']} guide", "search_volume": 1000, "competition": 0.6},
        {"keyword": f"best {state['seed_keyword']}", "search_volume": 800, "competition": 0.7},
        {"keyword": f"{state['seed_keyword']} tips", "search_volume": 600, "competition": 0.5},
    ]
    
    related_keywords = [
        {"keyword": f"{state['seed_keyword']} tutorial", "search_volume": 400, "competition": 0.4},
        {"keyword": f"how to {state['seed_keyword']}", "search_volume": 500, "competition": 0.5},
        {"keyword": f"{state['seed_keyword']} examples", "search_volume": 300, "competition": 0.3},
    ]
    
    long_tail_keywords = [
        {"keyword": f"best {state['seed_keyword']} for beginners", "search_volume": 100, "competition": 0.2},
        {"keyword": f"{state['seed_keyword']} step by step guide", "search_volume": 150, "competition": 0.3},
        {"keyword": f"free {state['seed_keyword']} tools", "search_volume": 120, "competition": 0.25},
    ]
    
    return {
        "primary_keywords": primary_keywords,
        "related_keywords": related_keywords,
        "long_tail_keywords": long_tail_keywords,
        "keyword_clusters": [
            {
                "cluster": "educational",
                "keywords": [kw["keyword"] for kw in primary_keywords[:2] + related_keywords[:2]]
            },
            {
                "cluster": "commercial",
                "keywords": [kw["keyword"] for kw in primary_keywords[1:] + long_tail_keywords[:1]]
            }
        ]
    }


def competitor_analysis_node(state: SEOResearchState, config: RunnableConfig) -> SEOResearchState:
    """Analyze competitor content for insights."""
    configurable = Configuration.from_runnable_config(config)
    
    competitor_analysis = []
    
    for url in state["competitor_urls"]:
        competitor_data = fetch_competitor_data(url)
        if competitor_data:
            analysis = {
                "url": url,
                "title": competitor_data.title,
                "word_count": competitor_data.word_count,
                "headings": competitor_data.headings,
                "strengths": [],
                "weaknesses": [],
                "opportunities": []
            }
            
            # Analyze content structure
            if competitor_data.word_count > 1500:
                analysis["strengths"].append("Comprehensive content length")
            else:
                analysis["weaknesses"].append("Content could be more comprehensive")
            
            if len(competitor_data.headings) >= 5:
                analysis["strengths"].append("Well-structured with multiple headings")
            else:
                analysis["opportunities"].append("Better content structure with more headings")
            
            competitor_analysis.append(analysis)
    
    # Identify content gaps
    content_gaps = []
    all_competitor_headings = []
    for analysis in competitor_analysis:
        all_competitor_headings.extend(analysis.get("headings", []))
    
    # Find missing topics that could be opportunities
    common_topics = ["introduction", "benefits", "how to", "best practices", "conclusion"]
    for topic in common_topics:
        topic_coverage = sum(1 for heading in all_competitor_headings 
                           if topic.lower() in heading.lower())
        if topic_coverage < len(competitor_analysis) * 0.5:
            content_gaps.append({
                "topic": topic,
                "opportunity": f"Only {topic_coverage}/{len(competitor_analysis)} competitors cover {topic}",
                "recommendation": f"Include comprehensive {topic} section"
            })
    
    return {
        "competitor_analysis": competitor_analysis,
        "content_gaps": content_gaps
    }


def content_outline_node(state: SEOContentState, config: RunnableConfig) -> SEOContentState:
    """Generate detailed content outline."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=0.4,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    prompt = f"""
    Create a detailed content outline for a {state['content_type']} about "{state['topic']}".
    
    Requirements:
    - Target keywords: {', '.join(state['target_keywords'])}
    - Target length: {state['target_length']} words
    - Tone: {state['tone']}
    - Audience: {state['target_audience']}
    
    The outline should include:
    1. SEO-optimized title
    2. Meta description (150-160 characters)
    3. Detailed section structure with headings
    4. Target keywords distribution
    5. Internal linking opportunities
    6. Call-to-action suggestions
    
    Consider competitor analysis: {state.get('competitor_analysis', 'None available')}
    
    Current date: {get_current_date()}
    """
    
    response = llm.invoke(prompt)
    
    # Generate outline using helper function
    outline = generate_content_outline(
        state['topic'], 
        state['target_keywords'],
        state.get('competitor_analysis')
    )
    
    # Enhanced with AI suggestions
    outline["ai_suggestions"] = response.content
    
    return {"outline": outline}


def content_generation_node(state: SEOContentState, config: RunnableConfig) -> SEOContentState:
    """Generate SEO-optimized content."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatGoogleGenerativeAI(
        model=configurable.reasoning_model,
        temperature=0.6,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    outline = state.get('outline', {})
    
    prompt = f"""
    Write a comprehensive {state['content_type']} about "{state['topic']}" following this outline:
    
    {outline}
    
    Requirements:
    - Include target keywords: {', '.join(state['target_keywords'])}
    - Target length: {state['target_length']} words
    - Tone: {state['tone']}
    - Audience: {state['target_audience']}
    - Use proper HTML structure with headings (H1, H2, H3)
    - Natural keyword integration (avoid keyword stuffing)
    - Include actionable insights and examples
    - Add internal linking suggestions as [INTERNAL LINK: anchor text]
    - Include a compelling introduction and conclusion
    
    Focus on creating valuable, engaging content that serves the user's search intent.
    
    Current date: {get_current_date()}
    """
    
    response = llm.invoke(prompt)
    
    # Generate meta elements
    meta_title = f"{state['topic']} - Complete Guide | Your Site"
    meta_description = f"Discover everything about {state['topic']}. {', '.join(state['target_keywords'][:2])}. Complete guide with expert tips and actionable insights."
    
    # Generate featured image prompt
    featured_image_prompt = f"Professional illustration of {state['topic']}, clean modern design, {state['tone']} style, suitable for blog header"
    
    return {
        "content": response.content,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "featured_image_prompt": featured_image_prompt
    }


def seo_analysis_node(state: SEOAnalysisState, config: RunnableConfig) -> SEOAnalysisState:
    """Analyze content for SEO optimization."""
    content = state['content']
    target_keywords = state['target_keywords']
    
    # Perform various SEO analyses
    keyword_density = extract_keywords_from_content(content, target_keywords)
    readability_score = calculate_readability_score(content)
    
    # Extract title and meta description from content if available
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    title = title_match.group(1) if title_match else ""
    
    meta_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    meta_description = meta_match.group(1) if meta_match else ""
    
    title_analysis = analyze_title_seo(title, target_keywords)
    meta_analysis = analyze_meta_description(meta_description, target_keywords)
    content_structure = analyze_content_structure(content)
    
    # Calculate overall SEO score
    seo_score = (
        title_analysis['score'] * 0.3 +
        meta_analysis['score'] * 0.2 + 
        min(100, readability_score) * 0.2 +
        (100 - min(100, sum(keyword_density.values()) * 10)) * 0.3  # Penalize keyword stuffing
    )
    
    # Collect issues and suggestions
    issues = []
    suggestions = []
    strengths = []
    
    issues.extend(title_analysis.get('issues', []))
    issues.extend(meta_analysis.get('issues', []))
    issues.extend(content_structure.get('issues', []))
    
    suggestions.extend(title_analysis.get('suggestions', []))
    suggestions.extend(meta_analysis.get('suggestions', []))
    suggestions.extend(content_structure.get('suggestions', []))
    
    # Identify strengths
    if readability_score > 60:
        strengths.append("Good readability score")
    if content_structure['word_count'] > 500:
        strengths.append("Comprehensive content length")
    if any(density > 0.5 and density < 3 for density in keyword_density.values()):
        strengths.append("Appropriate keyword density")
    
    return {
        "seo_score": round(seo_score, 1),
        "readability_score": round(readability_score, 1),
        "keyword_density": keyword_density,
        "title_analysis": title_analysis,
        "meta_analysis": meta_analysis,
        "content_structure": content_structure,
        "issues": issues,
        "suggestions": suggestions,
        "strengths": strengths
    }


def content_optimization_node(state: SEOContentState, config: RunnableConfig) -> SEOContentState:
    """Optimize content based on SEO analysis."""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatGoogleGenerativeAI(
        model=configurable.reasoning_model,
        temperature=0.3,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    seo_analysis = state.get('seo_analysis', {})
    original_content = state.get('content', '')
    
    if not seo_analysis or not original_content:
        return state
    
    prompt = f"""
    Optimize the following content based on SEO analysis results:
    
    Original Content:
    {original_content}
    
    SEO Analysis Results:
    - SEO Score: {seo_analysis.get('seo_score', 0)}/100
    - Issues: {', '.join(seo_analysis.get('issues', []))}
    - Suggestions: {', '.join(seo_analysis.get('suggestions', []))}
    
    Target Keywords: {', '.join(state['target_keywords'])}
    
    Please improve the content by:
    1. Addressing all identified issues
    2. Implementing the suggestions
    3. Maintaining natural, readable flow
    4. Preserving the original meaning and value
    5. Optimizing for target keywords without overstuffing
    
    Return the optimized content with the same HTML structure.
    """
    
    response = llm.invoke(prompt)
    
    return {"optimized_content": response.content}


# Create SEO Research Workflow
def create_seo_research_graph() -> StateGraph:
    """Create SEO research workflow graph."""
    builder = StateGraph(SEOResearchState)
    
    # Add nodes  
    builder.add_node("keyword_research", keyword_research_node)
    builder.add_node("analyze_competitors", competitor_analysis_node)
    
    # Define workflow
    builder.add_edge(START, "keyword_research")
    builder.add_edge("keyword_research", "analyze_competitors")
    builder.add_edge("analyze_competitors", END)
    
    return builder.compile(name="seo-research-agent")


# Create SEO Content Generation Workflow
def create_seo_content_graph() -> StateGraph:
    """Create SEO content generation workflow graph."""
    builder = StateGraph(SEOContentState)
    
    # Add nodes
    builder.add_node("content_outline", content_outline_node)
    builder.add_node("content_generation", content_generation_node)
    builder.add_node("content_optimization", content_optimization_node)
    
    # Define workflow
    builder.add_edge(START, "content_outline")
    builder.add_edge("content_outline", "content_generation")
    builder.add_edge("content_generation", "content_optimization")
    builder.add_edge("content_optimization", END)
    
    return builder.compile(name="seo-content-agent")


# Create SEO Analysis Workflow
def create_seo_analysis_graph() -> StateGraph:
    """Create SEO analysis workflow graph."""
    builder = StateGraph(SEOAnalysisState)
    
    # Add nodes
    builder.add_node("seo_analysis", seo_analysis_node)
    
    # Define workflow
    builder.add_edge(START, "seo_analysis")
    builder.add_edge("seo_analysis", END)
    
    return builder.compile(name="seo-analysis-agent")