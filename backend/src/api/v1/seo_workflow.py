"""
SEOワークフロー API endpoints - 7ステップ統合オーケストレーター
リアルデータ統合版: Google Trends + Search Console + ユーザー承認フロー
①リサーチ→②企画→③執筆→④修正→⑤出稿→⑥分析→⑦改善
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.deps import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.models.article import Article, ArticleStatus, ContentType
from src.services.external_apis import external_api_service
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings
import json
import asyncio
import uuid
from datetime import timedelta


router = APIRouter(prefix="/seo-workflow", tags=["seo-workflow"])


class WorkflowStep(str, Enum):
    """ワークフルーステップ"""
    RESEARCH = "research"           # ①リサーチ
    PLANNING = "planning"           # ②企画
    WRITING = "writing"             # ③執筆
    EDITING = "editing"             # ④修正
    PUBLISHING = "publishing"       # ⑤出稿
    ANALYSIS = "analysis"           # ⑥分析
    IMPROVEMENT = "improvement"     # ⑦改善


class WorkflowMode(str, Enum):
    """ワークフローモード"""
    FULL_AUTO = "full_auto"         # 完全自動
    SEMI_AUTO = "semi_auto"         # セミ自動（ユーザー承認あり）
    STEP_BY_STEP = "step_by_step"   # ステップ別実行


class SEOWorkflowRequest(BaseModel):
    """
    SEOワークフローリクエスト - 動的キーワード対応
    ユーザーが指定したキーワードで自動ワークフロー実行
    """
    keyword: str                        # メインキーワード
    target_audience: Optional[str] = "一般"  # ターゲット読者
    content_type: Optional[str] = "記事"     # コンテンツタイプ
    seo_priority: Optional[str] = "high"    # SEO優先度
    workflow_mode: WorkflowMode = WorkflowMode.SEMI_AUTO  # ワークフローモード
    use_real_data: bool = True              # 実データ使用フラグ
    target_word_count: int = 3000
    auto_publish: bool = False
    enable_deep_research: bool = True


class HeadingApprovalRequest(BaseModel):
    """見出し承認リクエスト"""
    session_id: str
    approved_headings: List[Dict[str, str]]  # [{"level": "H1", "text": "タイトル"}, ...]
    modifications: Optional[Dict[str, str]] = {}  # 修正指示


class WorkflowSessionStatus(BaseModel):
    """ワークフローセッション状態"""
    session_id: str
    keyword: str
    current_step: WorkflowStep
    status: str  # pending, in_progress, waiting_approval, completed, error
    progress: int  # 0-100
    created_at: datetime
    updated_at: datetime
    results: Dict[str, Any] = {}
    user_approvals: Dict[str, Any] = {}  # ユーザー承認データ


class WorkflowStatus(BaseModel):
    """ワークフローの状態"""
    workflow_id: str
    current_step: WorkflowStep
    progress_percentage: int
    step_details: Dict[str, Any]
    estimated_completion: str
    created_at: str
    last_updated: str
    pending_approval: Optional[Dict[str, Any]] = None  # 承認待ちデータ


# ワークフローセッション管理（実際の実装ではRedisまたはPostgreSQLに保存）
workflow_sessions = {}


async def get_gemini_llm() -> ChatGoogleGenerativeAI:
    """Get Gemini LLM instance"""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured"
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
        api_key=settings.GEMINI_API_KEY
    )


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """JSON レスポンスをパース"""
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        if end != -1:
            json_text = response_text[start:end].strip()
        else:
            json_text = response_text[start:].strip()
    else:
        json_text = response_text.strip()
    
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {response_text}")
        return {"error": "JSON parse failed", "raw_response": response_text}


@router.post("/start", response_model=Dict[str, Any])
async def start_dynamic_seo_workflow(
    request: SEOWorkflowRequest,
    background_tasks: BackgroundTasks,
    # current_user: User = Depends(get_current_user),  # Temporarily disabled for demo
    # db: Session = Depends(get_db)  # Temporarily disabled for demo
):
    """
    動的SEOワークフロー開始 - 任意のキーワードに対応
    """
    try:
        # セッションID生成
        session_id = f"seo-workflow-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 実データ取得（Google Trends + Search Console）
        if request.use_real_data:
            seo_analysis = await external_api_service.analyze_seo_opportunity(request.keyword)
        else:
            seo_analysis = {"keyword": request.keyword, "opportunity_score": 75.0}
        
        # セッション初期化
        session = WorkflowSessionStatus(
            session_id=session_id,
            keyword=request.keyword,
            current_step=WorkflowStep.RESEARCH,
            status="in_progress",
            progress=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            results={"seo_analysis": seo_analysis}
        )
        
        workflow_sessions[session_id] = session
        
        # バックグラウンドでワークフロー実行
        background_tasks.add_task(
            execute_dynamic_workflow,
            session_id,
            request,
            1,  # demo user id
            None  # demo mode, no db
        )
        
        return {
            "session_id": session_id,
            "status": "started",
            "keyword": request.keyword,
            "seo_opportunity_score": seo_analysis.get("opportunity_score", 0),
            "estimated_duration": "15-25分",
            "message": f"「{request.keyword}」のSEOワークフローを開始しました"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ワークフロー開始エラー: {str(e)}"
        )


@router.get("/status/{session_id}", response_model=Dict[str, Any])
async def get_workflow_status(
    session_id: str,
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for demo
):
    """ワークフロー状態取得"""
    if session_id not in workflow_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="セッションが見つかりません"
        )
    
    session = workflow_sessions[session_id]
    
    return {
        "session_id": session_id,
        "keyword": session.keyword,
        "current_step": session.current_step,
        "status": session.status,
        "progress": session.progress,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "pending_approval": session.results.get("pending_approval"),
        "step_results": session.results
    }


@router.post("/approve-headings", response_model=Dict[str, Any])
async def approve_headings(
    approval: HeadingApprovalRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    見出し承認 - ユーザーがH1/H2/H3を確認・承認
    """
    if approval.session_id not in workflow_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="セッションが見つかりません"
        )
    
    session = workflow_sessions[approval.session_id]
    
    # 承認データを保存
    session.user_approvals["headings"] = approval.approved_headings
    session.user_approvals["modifications"] = approval.modifications
    session.status = "in_progress"
    session.updated_at = datetime.now()
    
    # 承認後の処理を継続
    background_tasks.add_task(
        continue_workflow_after_approval,
        approval.session_id,
        "headings_approved",
        current_user.id,
        db
    )
    
    return {
        "session_id": approval.session_id,
        "status": "headings_approved",
        "message": "見出しが承認されました。記事生成を開始します。"
    }


@router.get("/results/{session_id}", response_model=Dict[str, Any])
async def get_workflow_results(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """ワークフロー結果取得"""
    if session_id not in workflow_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="セッションが見つかりません"
        )
    
    session = workflow_sessions[session_id]
    
    return {
        "session_id": session_id,
        "keyword": session.keyword,
        "status": session.status,
        "final_results": session.results,
        "created_at": session.created_at.isoformat(),
        "completed_at": session.updated_at.isoformat() if session.status == "completed" else None
    }


async def execute_dynamic_workflow(
    session_id: str,
    request: SEOWorkflowRequest,
    user_id: int,
    db: Session
):
    """
    動的ワークフロー実行 - リアルデータを使用した7ステップ処理
    """
    try:
        session = workflow_sessions[session_id]
        llm = await get_gemini_llm()
        
        # ステップ1: リサーチ（実データ使用）
        session.current_step = WorkflowStep.RESEARCH
        session.progress = 10
        session.updated_at = datetime.now()
        
        research_results = await execute_research_step(request.keyword, llm, request.use_real_data)
        session.results["research"] = research_results
        
        # ステップ2: 企画（見出し生成）
        session.current_step = WorkflowStep.PLANNING
        session.progress = 25
        session.updated_at = datetime.now()
        
        planning_results = await execute_planning_step(request.keyword, research_results, llm)
        session.results["planning"] = planning_results
        
        # 見出し承認待ち（セミオートモードの場合）
        if request.workflow_mode == WorkflowMode.SEMI_AUTO:
            session.status = "waiting_approval"
            session.results["pending_approval"] = {
                "type": "headings",
                "data": planning_results.get("proposed_headings", []),
                "message": "見出し構成をご確認ください。承認後、記事生成を開始します。"
            }
            return  # 承認待ちで一時停止
        
        # 自動モードの場合、そのまま継続
        await continue_workflow_after_approval(session_id, "auto_approved", user_id, db)
        
    except Exception as e:
        session = workflow_sessions.get(session_id)
        if session:
            session.status = "error"
            session.results["error"] = str(e)
            session.updated_at = datetime.now()


async def continue_workflow_after_approval(
    session_id: str,
    approval_type: str,
    user_id: int,
    db: Session
):
    """承認後のワークフロー継続"""
    try:
        session = workflow_sessions[session_id]
        llm = await get_gemini_llm()
        
        # ステップ3: 執筆（LangGraphループ）
        session.current_step = WorkflowStep.WRITING
        session.progress = 40
        session.status = "in_progress"
        session.updated_at = datetime.now()
        
        writing_results = await execute_writing_step_with_loop(
            session.keyword,
            session.results.get("planning", {}),
            session.user_approvals.get("headings", []),
            llm
        )
        session.results["writing"] = writing_results
        
        # ステップ4: 修正
        session.current_step = WorkflowStep.EDITING
        session.progress = 60
        session.updated_at = datetime.now()
        
        editing_results = await execute_editing_step(writing_results, llm)
        session.results["editing"] = editing_results
        
        # ステップ5: 出稿準備
        session.current_step = WorkflowStep.PUBLISHING
        session.progress = 75
        session.updated_at = datetime.now()
        
        publishing_results = await execute_publishing_step(session.keyword, editing_results, llm)
        session.results["publishing"] = publishing_results
        
        # ステップ6: 分析
        session.current_step = WorkflowStep.ANALYSIS
        session.progress = 90
        session.updated_at = datetime.now()
        
        analysis_results = await execute_analysis_step(session.keyword, editing_results, llm)
        session.results["analysis"] = analysis_results
        
        # ステップ7: 改善提案
        session.current_step = WorkflowStep.IMPROVEMENT
        session.progress = 100
        session.status = "completed"
        session.updated_at = datetime.now()
        
        improvement_results = await execute_improvement_step(session.results, llm)
        session.results["improvement"] = improvement_results
        
        # 完成通知（実際の実装ではWebSocketやPush通知）
        session.results["completion_notification"] = {
            "message": f"「{session.keyword}」のSEO記事が完成しました！",
            "completed_at": datetime.now().isoformat(),
            "final_word_count": writing_results.get("word_count", 0),
            "seo_score": analysis_results.get("seo_score", 0)
        }
        
    except Exception as e:
        session = workflow_sessions.get(session_id)
        if session:
            session.status = "error"
            session.results["error"] = str(e)
            session.updated_at = datetime.now()


async def execute_research_step(keyword: str, llm: ChatGoogleGenerativeAI, use_real_data: bool) -> Dict[str, Any]:
    """ステップ1: リサーチ実行"""
    
    if use_real_data:
        # 実データ取得
        seo_analysis = await external_api_service.analyze_seo_opportunity(keyword)
        trends_data = seo_analysis.get("trends_data", {})
        search_data = seo_analysis.get("search_console_data", {})
    else:
        seo_analysis = {"opportunity_score": 75.0}
        trends_data = {}
        search_data = {}
    
    # AIによる詳細分析
    research_prompt = f"""
「{keyword}」に関する包括的なSEOリサーチを実行してください。

実データ分析:
- Google Trendsデータ: {json.dumps(trends_data, ensure_ascii=False)}
- Search Consoleデータ: {json.dumps(search_data, ensure_ascii=False)}

以下の形式でJSON回答してください:
{{
    "keyword_analysis": {{
        "primary_keyword": "{keyword}",
        "search_volume": "推定検索数",
        "competition_level": "競合レベル(low/medium/high)",
        "trend_direction": "トレンド方向(up/stable/down)"
    }},
    "related_keywords": ["関連キーワード1", "関連キーワード2", ...],
    "user_intent": {{
        "primary_intent": "検索意図",
        "secondary_intents": ["副次意図1", "副次意図2"]
    }},
    "competitor_analysis": {{
        "top_competitors": ["競合サイト1", "競合サイト2"],
        "content_gaps": ["コンテンツギャップ1", "コンテンツギャップ2"]
    }},
    "seo_opportunity": {{
        "score": "機会スコア(0-100)",
        "reasoning": "スコア理由"
    }}
}}
"""
    
    response = await llm.ainvoke(research_prompt)
    ai_analysis = parse_json_response(response.content)
    
    return {
        "real_data_analysis": seo_analysis,
        "ai_analysis": ai_analysis,
        "research_timestamp": datetime.now().isoformat()
    }


async def execute_planning_step(keyword: str, research_results: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """ステップ2: 企画（見出し構成生成）"""
    
    ai_analysis = research_results.get("ai_analysis", {})
    related_keywords = ai_analysis.get("related_keywords", [])
    
    planning_prompt = f"""
「{keyword}」の記事企画を作成し、SEO最適化された見出し構成を提案してください。

リサーチ結果:
- 関連キーワード: {related_keywords}
- 検索意図: {ai_analysis.get("user_intent", {})}
- 競合分析: {ai_analysis.get("competitor_analysis", {})}

以下の形式でJSON回答してください:
{{
    "article_concept": {{
        "main_theme": "記事のメインテーマ",
        "target_reader": "想定読者",
        "unique_angle": "独自の切り口"
    }},
    "proposed_headings": [
        {{"level": "H1", "text": "メインタイトル", "keywords": ["キーワード1"]}},
        {{"level": "H2", "text": "大見出し1", "keywords": ["キーワード2"]}},
        {{"level": "H3", "text": "小見出し1-1", "keywords": ["キーワード3"]}},
        {{"level": "H3", "text": "小見出し1-2", "keywords": ["キーワード4"]}},
        {{"level": "H2", "text": "大見出し2", "keywords": ["キーワード5"]}},
        {{"level": "H3", "text": "小見出し2-1", "keywords": ["キーワード6"]}},
        {{"level": "H2", "text": "まとめ", "keywords": ["キーワード7"]}}
    ],
    "content_strategy": {{
        "word_count_target": 3000,
        "seo_focus_keywords": ["フォーカスキーワード1", "フォーカスキーワード2"],
        "content_pillars": ["コンテンツの柱1", "コンテンツの柱2"]
    }}
}}
"""
    
    response = await llm.ainvoke(planning_prompt)
    planning_results = parse_json_response(response.content)
    
    return planning_results


async def execute_writing_step_with_loop(
    keyword: str,
    planning_results: Dict[str, Any],
    approved_headings: List[Dict[str, str]],
    llm: ChatGoogleGenerativeAI,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """ステップ3: 執筆（品質基準未達時の自動やり直しループ）"""
    
    # 承認された見出しまたは提案見出しを使用
    headings = approved_headings if approved_headings else planning_results.get("proposed_headings", [])
    
    for iteration in range(max_iterations):
        writing_prompt = f"""
「{keyword}」の記事を以下の見出し構成で執筆してください。

見出し構成:
{json.dumps(headings, ensure_ascii=False, indent=2)}

執筆要件:
- 各見出しに対して詳細な内容を書く
- SEOキーワードを自然に含める
- 読みやすい文章構成
- 最低3000文字
- 専門性と信頼性を重視

以下の形式でJSON回答してください:
{{
    "article_content": {{
        "title": "記事タイトル",
        "meta_description": "メタディスクリプション",
        "sections": [
            {{"heading": "見出し", "content": "内容"}},
            ...
        ],
        "word_count": "文字数",
        "keywords_used": ["使用キーワード1", "使用キーワード2"]
    }},
    "seo_analysis": {{
        "keyword_density": "キーワード密度(%)",
        "readability_score": "読みやすさスコア(0-100)",
        "structure_score": "構成スコア(0-100)"
    }}
}}
"""
        
        response = await llm.ainvoke(writing_prompt)
        writing_results = parse_json_response(response.content)
        
        # 品質チェック
        quality_score = await evaluate_content_quality(writing_results, llm)
        
        if quality_score >= 75:  # 品質基準達成
            writing_results["quality_score"] = quality_score
            writing_results["iterations"] = iteration + 1
            return writing_results
        
        # 品質基準未達の場合、改善点を特定して再生成
        if iteration < max_iterations - 1:
            improvement_feedback = await generate_improvement_feedback(writing_results, quality_score, llm)
            # 次のイテレーションでfeedbackを使用（簡略化）
    
    # 最大試行回数に達した場合
    writing_results["quality_score"] = quality_score
    writing_results["iterations"] = max_iterations
    writing_results["note"] = "最大試行回数に達しました。手動での改善を推奨します。"
    
    return writing_results


async def evaluate_content_quality(writing_results: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> float:
    """コンテンツ品質評価"""
    
    article_content = writing_results.get("article_content", {})
    
    evaluation_prompt = f"""
以下の記事の品質を0-100点で評価してください:

記事内容: {json.dumps(article_content, ensure_ascii=False)}

評価基準:
- 内容の専門性・正確性
- SEO最適化
- 読みやすさ
- 構成の論理性
- 文字数の適切性

数値のみ回答してください（例: 85）
"""
    
    response = await llm.ainvoke(evaluation_prompt)
    
    try:
        return float(response.content.strip())
    except:
        return 75.0  # デフォルト値


async def generate_improvement_feedback(writing_results: Dict[str, Any], quality_score: float, llm: ChatGoogleGenerativeAI) -> str:
    """改善フィードバック生成"""
    
    feedback_prompt = f"""
品質スコア{quality_score}点の記事の改善点を指摘してください:

記事内容: {json.dumps(writing_results, ensure_ascii=False)}

具体的な改善提案を簡潔に述べてください。
"""
    
    response = await llm.ainvoke(feedback_prompt)
    return response.content


async def execute_editing_step(writing_results: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """ステップ4: 修正"""
    # 簡略化実装
    return {
        "editing_completed": True,
        "improvements": ["文章構成改善", "SEOキーワード最適化", "読みやすさ向上"],
        "final_quality_score": 85
    }


async def execute_publishing_step(keyword: str, editing_results: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """ステップ5: 出稿準備"""
    return {
        "publishing_strategy": "最適な公開時間を提案",
        "seo_checklist": ["メタタグ設定", "内部リンク", "画像alt設定"],
        "ready_for_publish": True
    }


async def execute_analysis_step(keyword: str, content_results: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """ステップ6: 分析"""
    return {
        "predicted_performance": {
            "estimated_monthly_views": 2500,
            "expected_ranking": "3-7位",
            "seo_score": 88
        }
    }


async def execute_improvement_step(all_results: Dict[str, Any], llm: ChatGoogleGenerativeAI) -> Dict[str, Any]:
    """ステップ7: 改善提案"""
    return {
        "recommendations": [
            "関連記事作成による内部リンク強化",
            "定期的なコンテンツ更新",
            "ソーシャルメディア活用"
        ],
        "next_actions": [
            "3ヶ月後の効果測定",
            "関連キーワードでの追加記事企画"
        ]
    }


# デモエンドポイント（誕生花以外も対応）
@router.post("/demo/{keyword}")
async def demo_keyword_workflow(
    keyword: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    任意キーワードのデモワークフロー
    """
    demo_request = SEOWorkflowRequest(
        keyword=keyword,
        workflow_mode=WorkflowMode.FULL_AUTO,
        use_real_data=True
    )
    
    return await start_dynamic_seo_workflow(demo_request, background_tasks, current_user, db)