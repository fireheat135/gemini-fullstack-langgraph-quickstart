"""
SEO Research Graph - Customized LangGraph workflow for SEO keyword research
"""
import os
from typing import Dict, Any, List
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from src.agent.state import OverallState
from src.agent.configuration import Configuration
from src.seo.keyword_analyzer import KeywordAnalyzer
from src.seo.competitor_analyzer import CompetitorAnalyzer

load_dotenv()


class SEOResearchQuery(BaseModel):
    """SEO research query structure"""
    primary_keyword: str = Field(description="Main keyword to research")
    related_queries: List[str] = Field(description="Related search queries for research")
    search_intent: str = Field(description="Search intent: informational, commercial, navigational, transactional")
    target_audience: str = Field(description="Target audience for the content")


class SEOResearchState(BaseModel):
    """State for SEO research workflow"""
    primary_keyword: str
    research_queries: List[str] = []
    keyword_data: Dict[str, Any] = {}
    competitor_data: List[Dict[str, Any]] = []
    content_gaps: List[str] = []
    seo_recommendations: List[str] = []
    search_intent: str = "informational"
    target_audience: str = "一般ユーザー"


def generate_seo_queries(state: dict, config: RunnableConfig) -> dict:
    """Generate SEO-specific research queries"""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=0.7,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    primary_keyword = state.get("primary_keyword", "")
    
    prompt = f"""
    あなたはSEOエキスパートです。以下の主要キーワードに対して、包括的なSEOリサーチを行うための検索クエリを生成してください。

    主要キーワード: {primary_keyword}
    
    以下の観点から検索クエリを5-7個生成してください：
    1. キーワードボリュームと難易度
    2. 関連キーワードと共起語
    3. 検索意図の分析
    4. 競合分析
    5. コンテンツギャップ分析
    6. トレンド分析
    
    各クエリは具体的で検索可能な形にしてください。
    
    例：
    - "{primary_keyword} 検索ボリューム 2024"
    - "{primary_keyword} 関連キーワード"
    - "{primary_keyword} 競合サイト"
    - "{primary_keyword} ユーザー意図"
    
    検索クエリ（改行区切り）:
    """
    
    result = llm.invoke(prompt)
    queries = [q.strip() for q in result.content.split('\n') if q.strip()]
    
    return {"research_queries": queries}


async def analyze_keywords(state: dict, config: RunnableConfig) -> dict:
    """Analyze keywords using the keyword analyzer"""
    analyzer = KeywordAnalyzer()
    primary_keyword = state.get("primary_keyword", "")
    
    try:
        # Primary keyword analysis
        keyword_result = await analyzer.analyze_keyword(
            keyword=primary_keyword,
            include_trends=True,
            include_related=True,
            include_competitors=False
        )
        
        # Get related keywords
        related_keywords = await analyzer.get_related_keywords(primary_keyword)
        
        # Analyze difficulty
        difficulty_data = await analyzer.analyze_difficulty([primary_keyword])
        
        # Get suggestions
        suggestions = await analyzer.suggest_keywords(
            seed_keyword=primary_keyword,
            target_audience=state.get("target_audience", "一般ユーザー"),
            content_type="ブログ記事"
        )
        
        keyword_data = {
            "primary_analysis": keyword_result,
            "related_keywords": related_keywords,
            "difficulty": difficulty_data,
            "suggestions": [s["keyword"] for s in suggestions]
        }
        
        return {"keyword_data": keyword_data}
        
    except Exception as e:
        print(f"Keyword analysis failed: {e}")
        return {"keyword_data": {"error": str(e)}}


async def analyze_competitors(state: dict, config: RunnableConfig) -> dict:
    """Analyze competitors for the keyword"""
    analyzer = CompetitorAnalyzer()
    primary_keyword = state.get("primary_keyword", "")
    
    try:
        competitors = await analyzer.analyze_competitors(
            keyword=primary_keyword,
            top_n=10
        )
        
        # Extract content gaps
        content_gaps = []
        seo_recommendations = []
        
        if competitors:
            # Analyze common patterns
            avg_word_count = sum(c.get("word_count", 0) for c in competitors) / len(competitors)
            common_headings = []
            
            for competitor in competitors:
                if competitor.get("headings"):
                    common_headings.extend(competitor["headings"])
            
            # Generate recommendations based on analysis
            seo_recommendations = [
                f"推奨文字数: {int(avg_word_count)}文字程度",
                f"競合分析結果: 上位{len(competitors)}サイトを分析",
                "見出し構造の最適化が重要",
                "ユーザー意図に基づいたコンテンツ作成"
            ]
            
            content_gaps = [
                "より詳細な解説コンテンツ",
                "実用的な事例・ケーススタディ",
                "最新のトレンド情報",
                "ユーザーのよくある質問への回答"
            ]
        
        return {
            "competitor_data": competitors,
            "content_gaps": content_gaps,
            "seo_recommendations": seo_recommendations
        }
        
    except Exception as e:
        print(f"Competitor analysis failed: {e}")
        return {
            "competitor_data": [],
            "content_gaps": [],
            "seo_recommendations": [f"分析エラー: {str(e)}"]
        }


def generate_seo_insights(state: dict, config: RunnableConfig) -> dict:
    """Generate comprehensive SEO insights and recommendations"""
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatGoogleGenerativeAI(
        model=configurable.answer_model,
        temperature=0.3,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    primary_keyword = state.get("primary_keyword", "")
    keyword_data = state.get("keyword_data", {})
    competitor_data = state.get("competitor_data", [])
    content_gaps = state.get("content_gaps", [])
    
    prompt = f"""
    SEOエキスパートとして、以下のリサーチデータを基に包括的なSEO戦略レポートを作成してください。

    【主要キーワード】: {primary_keyword}
    
    【キーワードデータ】:
    {keyword_data}
    
    【競合データ】:
    競合サイト数: {len(competitor_data)}
    
    【コンテンツギャップ】:
    {content_gaps}
    
    以下の形式でレポートを作成してください：

    ## SEO戦略レポート

    ### 1. キーワード分析サマリー
    - 検索ボリューム評価
    - 競合難易度評価
    - 機会評価

    ### 2. コンテンツ戦略
    - 推奨コンテンツタイプ
    - ターゲット文字数
    - 見出し構造提案

    ### 3. 競合分析インサイト
    - 競合の強み・弱み
    - 差別化ポイント

    ### 4. 実行可能なアクションプラン
    - 優先順位付きタスク
    - 成功指標（KPI）

    レポート:
    """
    
    result = llm.invoke(prompt)
    
    return {
        "seo_insights": result.content,
        "status": "completed",
        "generated_at": datetime.now().isoformat()
    }


# Build the SEO Research Graph
def create_seo_research_graph():
    """Create the SEO research workflow graph"""
    
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("generate_queries", generate_seo_queries)
    workflow.add_node("analyze_keywords", analyze_keywords)
    workflow.add_node("analyze_competitors", analyze_competitors)
    workflow.add_node("generate_insights", generate_seo_insights)
    
    # Add edges
    workflow.add_edge(START, "generate_queries")
    workflow.add_edge("generate_queries", "analyze_keywords")
    workflow.add_edge("analyze_keywords", "analyze_competitors")
    workflow.add_edge("analyze_competitors", "generate_insights")
    workflow.add_edge("generate_insights", END)
    
    return workflow.compile()


# Create the compiled graph
seo_research_graph = create_seo_research_graph()


async def run_seo_research(primary_keyword: str, target_audience: str = "一般ユーザー") -> dict:
    """Run the complete SEO research workflow"""
    
    initial_state = {
        "primary_keyword": primary_keyword,
        "target_audience": target_audience,
        "search_intent": "informational"
    }
    
    config = {"configurable": {"thread_id": f"seo_research_{primary_keyword}"}}
    
    result = await seo_research_graph.ainvoke(initial_state, config)
    
    return result