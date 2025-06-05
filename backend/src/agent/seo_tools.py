"""SEO-specific tools for LangGraph agents."""

from typing import Dict, List, Any, Optional
import json
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

from pydantic import BaseModel


class KeywordData(BaseModel):
    """Schema for keyword data."""
    keyword: str
    search_volume: Optional[int] = None
    competition_score: Optional[float] = None
    cpc: Optional[float] = None
    difficulty: Optional[str] = None
    intent: Optional[str] = None


class CompetitorData(BaseModel):
    """Schema for competitor analysis data."""
    url: str
    title: str
    meta_description: Optional[str] = None
    word_count: int
    headings: List[str]
    keyword_density: Dict[str, float]
    domain_authority: Optional[int] = None
    page_authority: Optional[int] = None


class SEOAnalysis(BaseModel):
    """Schema for SEO analysis results."""
    seo_score: float
    readability_score: float
    keyword_density: Dict[str, float]
    title_analysis: Dict[str, Any]
    meta_analysis: Dict[str, Any]
    content_structure: Dict[str, Any]
    issues: List[str]
    suggestions: List[str]
    strengths: List[str]


def extract_keywords_from_content(content: str, target_keywords: List[str]) -> Dict[str, float]:
    """Extract keyword density from content."""
    if not content:
        return {}
    
    # Clean content
    clean_content = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
    words = re.findall(r'\b\w+\b', clean_content.lower())
    total_words = len(words)
    
    if total_words == 0:
        return {}
    
    keyword_density = {}
    content_lower = clean_content.lower()
    
    for keyword in target_keywords:
        keyword_lower = keyword.lower()
        count = content_lower.count(keyword_lower)
        density = (count / total_words) * 100
        keyword_density[keyword] = round(density, 2)
    
    return keyword_density


def analyze_title_seo(title: str, target_keywords: List[str]) -> Dict[str, Any]:
    """Analyze title for SEO optimization."""
    if not title:
        return {
            "score": 0,
            "length": 0,
            "keyword_included": False,
            "issues": ["Title is empty"],
            "suggestions": ["Add a compelling title with target keywords"]
        }
    
    issues = []
    suggestions = []
    score = 100
    
    # Length analysis
    title_length = len(title)
    if title_length < 30:
        issues.append("Title is too short (< 30 characters)")
        suggestions.append("Expand title to 50-60 characters for better SEO")
        score -= 20
    elif title_length > 60:
        issues.append("Title is too long (> 60 characters)")
        suggestions.append("Shorten title to under 60 characters to avoid truncation")
        score -= 10
    
    # Keyword analysis
    keyword_included = False
    title_lower = title.lower()
    for keyword in target_keywords:
        if keyword.lower() in title_lower:
            keyword_included = True
            break
    
    if not keyword_included:
        issues.append("Target keyword not found in title")
        suggestions.append("Include primary target keyword in the title")
        score -= 30
    
    return {
        "score": max(0, score),
        "length": title_length,
        "keyword_included": keyword_included,
        "issues": issues,
        "suggestions": suggestions
    }


def analyze_meta_description(meta_desc: str, target_keywords: List[str]) -> Dict[str, Any]:
    """Analyze meta description for SEO optimization."""
    if not meta_desc:
        return {
            "score": 0,
            "length": 0,
            "keyword_included": False,
            "issues": ["Meta description is empty"],
            "suggestions": ["Add a compelling meta description with target keywords"]
        }
    
    issues = []
    suggestions = []
    score = 100
    
    # Length analysis
    desc_length = len(meta_desc)
    if desc_length < 120:
        issues.append("Meta description is too short (< 120 characters)")
        suggestions.append("Expand meta description to 150-160 characters")
        score -= 20
    elif desc_length > 160:
        issues.append("Meta description is too long (> 160 characters)")
        suggestions.append("Shorten meta description to under 160 characters")
        score -= 10
    
    # Keyword analysis
    keyword_included = False
    desc_lower = meta_desc.lower()
    for keyword in target_keywords:
        if keyword.lower() in desc_lower:
            keyword_included = True
            break
    
    if not keyword_included:
        issues.append("Target keyword not found in meta description")
        suggestions.append("Include primary target keyword in meta description")
        score -= 30
    
    return {
        "score": max(0, score),
        "length": desc_length,
        "keyword_included": keyword_included,
        "issues": issues,
        "suggestions": suggestions
    }


def analyze_content_structure(content: str) -> Dict[str, Any]:
    """Analyze content structure for SEO."""
    if not content:
        return {
            "word_count": 0,
            "headings": {},
            "paragraph_count": 0,
            "avg_paragraph_length": 0,
            "issues": ["Content is empty"],
            "suggestions": ["Add substantial content (minimum 300 words)"]
        }
    
    issues = []
    suggestions = []
    
    # Word count
    words = re.findall(r'\b\w+\b', content)
    word_count = len(words)
    
    if word_count < 300:
        issues.append(f"Content is too short ({word_count} words)")
        suggestions.append("Aim for at least 300 words for better SEO")
    
    # Heading analysis
    headings = {
        "h1": len(re.findall(r'<h1[^>]*>', content, re.IGNORECASE)),
        "h2": len(re.findall(r'<h2[^>]*>', content, re.IGNORECASE)),
        "h3": len(re.findall(r'<h3[^>]*>', content, re.IGNORECASE)),
        "h4": len(re.findall(r'<h4[^>]*>', content, re.IGNORECASE)),
        "h5": len(re.findall(r'<h5[^>]*>', content, re.IGNORECASE)),
        "h6": len(re.findall(r'<h6[^>]*>', content, re.IGNORECASE)),
    }
    
    if headings["h1"] == 0:
        issues.append("No H1 heading found")
        suggestions.append("Add an H1 heading for better structure")
    elif headings["h1"] > 1:
        issues.append("Multiple H1 headings found")
        suggestions.append("Use only one H1 heading per page")
    
    if headings["h2"] == 0 and word_count > 500:
        issues.append("No H2 headings found in long content")
        suggestions.append("Break up long content with H2 headings")
    
    # Paragraph analysis
    paragraphs = re.split(r'\n\s*\n|<p[^>]*>|</p>', content)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    paragraph_count = len(paragraphs)
    
    if paragraph_count > 0:
        avg_paragraph_length = word_count / paragraph_count
        if avg_paragraph_length > 150:
            suggestions.append("Consider breaking up long paragraphs for better readability")
    else:
        avg_paragraph_length = 0
    
    return {
        "word_count": word_count,
        "headings": headings,
        "paragraph_count": paragraph_count,
        "avg_paragraph_length": round(avg_paragraph_length, 1),
        "issues": issues,
        "suggestions": suggestions
    }


def calculate_readability_score(content: str) -> float:
    """Calculate readability score (simplified Flesch Reading Ease)."""
    if not content:
        return 0
    
    # Remove HTML tags
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Count sentences
    sentences = re.split(r'[.!?]+', clean_content)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences)
    
    if sentence_count == 0:
        return 0
    
    # Count words
    words = re.findall(r'\b\w+\b', clean_content)
    word_count = len(words)
    
    if word_count == 0:
        return 0
    
    # Count syllables (approximation)
    syllable_count = 0
    for word in words:
        word = word.lower()
        count = 0
        vowels = 'aeiouy'
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index-1] not in vowels:
                count += 1
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count += 1
        syllable_count += count
    
    # Flesch Reading Ease formula
    if sentence_count > 0 and word_count > 0:
        score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
        return max(0, min(100, score))
    
    return 0


def fetch_competitor_data(url: str) -> Optional[CompetitorData]:
    """Fetch and analyze competitor page data."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ""
        
        # Extract meta description
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc_tag.get('content', '').strip() if meta_desc_tag else None
        
        # Extract content
        content = soup.get_text()
        words = re.findall(r'\b\w+\b', content)
        word_count = len(words)
        
        # Extract headings
        headings = []
        for i in range(1, 7):
            heading_tags = soup.find_all(f'h{i}')
            for tag in heading_tags:
                headings.append(tag.get_text().strip())
        
        # Basic keyword density (would need target keywords)
        keyword_density = {}
        
        return CompetitorData(
            url=url,
            title=title,
            meta_description=meta_description,
            word_count=word_count,
            headings=headings,
            keyword_density=keyword_density,
            domain_authority=None,  # Would need external API
            page_authority=None     # Would need external API
        )
        
    except Exception as e:
        print(f"Error fetching competitor data for {url}: {e}")
        return None


def generate_content_outline(
    topic: str, 
    target_keywords: List[str], 
    competitor_analysis: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate a content outline based on topic and research."""
    
    # Basic outline structure
    outline = {
        "title": f"Comprehensive Guide to {topic}",
        "meta_description": f"Learn everything about {topic}. {', '.join(target_keywords[:3])}",
        "sections": [
            {
                "heading": "Introduction",
                "subheadings": [
                    f"What is {topic}?",
                    "Why it matters",
                    "What you'll learn"
                ],
                "target_keywords": target_keywords[:2]
            },
            {
                "heading": f"Understanding {topic}",
                "subheadings": [
                    "Key concepts",
                    "Common misconceptions",
                    "Benefits and challenges"
                ],
                "target_keywords": target_keywords[1:3]
            },
            {
                "heading": f"How to Get Started with {topic}",
                "subheadings": [
                    "Prerequisites",
                    "Step-by-step guide",
                    "Best practices"
                ],
                "target_keywords": target_keywords[2:4]
            },
            {
                "heading": "Advanced Tips and Strategies",
                "subheadings": [
                    "Expert techniques",
                    "Common pitfalls to avoid",
                    "Tools and resources"
                ],
                "target_keywords": target_keywords[3:5]
            },
            {
                "heading": "Conclusion",
                "subheadings": [
                    "Key takeaways",
                    "Next steps",
                    "Additional resources"
                ],
                "target_keywords": target_keywords[:1]
            }
        ],
        "target_length": 2000,
        "internal_links": [],
        "external_links": []
    }
    
    # Enhance with competitor analysis if available
    if competitor_analysis:
        # Add competitor insights to improve outline
        pass
    
    return outline