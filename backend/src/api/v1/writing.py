"""
SEO記事執筆API endpoints - 構成生成、本文作成、Deep Research連携
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.deps import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.models.article import Article, ArticleStatus, ContentType
from src.services.ai.ai_service_manager import AIServiceManager
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings
import json
import asyncio
import uuid


router = APIRouter(prefix="/writing", tags=["writing"])


class StructureGenerationRequest(BaseModel):
    topic: str
    selected_pattern: Dict[str, Any]
    target_keywords: List[str] = []
    research_data: Optional[Dict[str, Any]] = None
    competitor_analysis: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None


class ContentGenerationRequest(BaseModel):
    topic: str
    article_structure: Dict[str, Any]
    writing_style: Dict[str, Any]
    target_keywords: List[str] = []
    research_data: Optional[Dict[str, Any]] = None
    use_deep_research: bool = True
    target_word_count: int = 3000


class ContentSection(BaseModel):
    heading: str
    level: int  # H2=2, H3=3, etc.
    content: str
    word_count: int
    keywords_used: List[str]
    sources: List[str] = []


class ArticleStructure(BaseModel):
    title: str
    meta_description: str
    introduction: Dict[str, Any]
    sections: List[Dict[str, Any]]
    conclusion: Dict[str, Any]
    estimated_word_count: int
    estimated_reading_time: int
    seo_analysis: Dict[str, Any]


# 進行中の執筆セッション管理
writing_sessions = {}


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
        print(f"JSON パースエラー: {e}")
        print(f"レスポンステキスト: {json_text[:500]}...")
        return {}


@router.post("/generate-structure", response_model=Dict[str, Any])
async def generate_article_structure(
    request: StructureGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """選択された企画パターンに基づいて詳細な記事構成を生成"""
    
    start_time = datetime.now()
    
    try:
        llm = await get_gemini_llm()
        
        # 現在の日付取得
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        structure_prompt = f"""
        「{request.topic}」について、選択された企画パターンに基づいて詳細な記事構成を作成してください。
        
        【選択された企画パターン】
        {request.selected_pattern}
        
        【ターゲットキーワード】
        {request.target_keywords}
        
        {'【リサーチデータ】' + str(request.research_data) if request.research_data else ''}
        
        {'【競合分析】' + str(request.competitor_analysis) if request.competitor_analysis else ''}
        
        以下の要件で詳細な記事構成を作成してください：
        
        **構成要件:**
        1. **タイトル最適化** - SEOとクリック率を考慮した魅力的なタイトル
        2. **メタディスクリプション** - 150-160文字で検索意図を満たす説明
        3. **導入部** - 読者の注意を引き、記事の価値を伝える
        4. **本文構成** - 論理的で読みやすいH2-H3整理
        5. **結論部** - 要点をまとめ、アクションを促す
        6. **SEO最適化** - キーワードの自然な配置と密度計算
        7. **ユーザーエクスペリエンス** - 読みやすさ、エンゲージメントを重視
        
        **出力JSON形式:**
        {{
            "article_structure": {{
                "title": "SEO最適化されたタイトル",
                "meta_title": "HTML titleタグ用（60文字以内）",
                "meta_description": "150-160文字のメタディスクリプション",
                "slug": "url-friendly-slug",
                "introduction": {{
                    "hook": "読者を引きつけるオープニング",
                    "problem_statement": "読者が直面している問題の明確化",
                    "solution_preview": "記事で提供する解決策のプレビュー",
                    "article_value": "記事を読むことで得られる価値",
                    "estimated_words": 200,
                    "keywords_to_include": ["キーワード1", "キーワード2"]
                }},
                "sections": [
                    {{
                        "h2": "H2大見出し",
                        "h2_purpose": "このセクションの目的と読者への価値",
                        "estimated_words": 600,
                        "h3_subsections": [
                            {{
                                "h3": "H3小見出し",
                                "content_outline": "具体的な内容のアウトライン",
                                "estimated_words": 200,
                                "keywords_to_include": ["キーワード"],
                                "content_type": "説明/手順/事例/リストなど",
                                "user_value": "読者がこのセクションから得られる具体的価値"
                            }}
                        ],
                        "section_cta": "セクション末尾のアクション促進（あれば）",
                        "internal_links": ["関連記事リンク1"],
                        "external_references": ["外部参考リンク1"]
                    }}
                ],
                "conclusion": {{
                    "summary": "記事の要点を簡潔にまとめ",
                    "key_takeaways": ["重要ポイント1", "ポイント2"],
                    "call_to_action": "読者に取ってもらいたい具体的アクション",
                    "next_steps": ["次のステップ1", "ステップ2"],
                    "estimated_words": 150
                }},
                "estimated_totals": {{
                    "word_count": 3000,
                    "reading_time": 12,
                    "sections_count": 5,
                    "h2_count": 5,
                    "h3_count": 15
                }}
            }},
            "seo_analysis": {{
                "primary_keyword_placement": {{
                    "title": "メインキーワードをタイトルに含める策略",
                    "headings": "見出しへのキーワード配置計画",
                    "content": "本文内での自然なキーワード使用方法"
                }},
                "keyword_distribution": {{
                    "メインキーワード": {{
                        "target_density": 1.5,
                        "estimated_occurrences": 45,
                        "placement_strategy": "配置戦略の詳細"
                    }}
                }},
                "semantic_keywords": ["関連キーワード1", "関連キーワード2"],
                "content_depth_score": 85,
                "user_intent_match": "検索意図との適合性評価",
                "competitive_advantage": ["競合優位ポイント1", "ポイント2"]
            }},
            "content_guidelines": {{
                "writing_style": {{
                    "tone": "{tone}",
                    "personality": "{personality}",
                    "formality": "{formality}",
                    "specific_instructions": ["文体指示1", "指示2"]
                }},
                "content_requirements": {{
                    "expertise_level": request.selected_pattern.get('required_expertise', '中級'),
                    "evidence_requirements": ["データ裏付け", "事例提示", "専門家の意見"],
                    "visual_elements": ["図解", "グラフ", "スクリーンショット"],
                    "engagement_elements": ["チェックリスト", "コラム", "Q&A"]
                }},
                "quality_checklist": [
                    "情報の正確性と最新性を確認",
                    "読みやすさと論理構成をチェック",
                    "E-A-T(専門性・権威性・信頼性)を強化",
                    "ユーザーの検索意図を完全に満たす",
                    "競合との差別化ポイントを明確化"
                ]
            }},
            "implementation_notes": {{
                "priority_sections": ["優先実装セクション1", "セクション2"],
                "research_requirements": ["追加リサーチが必要な節目1", "節目2"],
                "expert_review_needed": ["専門家レビューが必要な節目1"],
                "estimated_completion_time": "{request.selected_pattern.get('required_time', '8-12時間')}",
                "resource_allocation": {{
                    "writing": "60%",
                    "research": "25%", 
                    "editing": "15%"
                }}
            }}
        }}
        
        **特別考慮事項:**
        - ユーザーの検索意図を満たす包括的な情報提供
        - 競合との差別化を明確にしたユニークな価値提供
        - SEO効果と読みやすさのバランスを取った構成"""
        
        # Extract tone information
        tone_manner = request.selected_pattern.get('tone_manner', {})
        tone = tone_manner.get('voice', '親しみやすい')
        personality = tone_manner.get('personality', '専門家')
        formality = tone_manner.get('style', '丁寧語')
        
        # Format the prompt with extracted values
        writing_prompt = writing_prompt.format(
            tone=tone,
            personality=personality,
            formality=formality
        )
        
        writing_prompt += f"""
        - エンゲージメントとコンバージョンを意識した内容設計
        - 実装可能性を考慮した現実的な計画
        
        現在日付: {datetime.now().strftime('%Y年%m月%d日')}
        対象トピック: {request.topic}
        """
        
        # AI による構成生成
        response = llm.invoke(structure_prompt)
        structure_data = parse_json_response(response.content)
        
        if not structure_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="記事構成の生成に失敗しました"
            )
        
        # 処理時間計算
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # レスポンス構築
        result = {
            "success": True,
            "data": structure_data,
            "metadata": {
                "topic": request.topic,
                "pattern_type": request.selected_pattern.get('type', 'Unknown'),
                "estimated_word_count": structure_data.get('article_structure', {}).get('estimated_totals', {}).get('word_count', 0),
                "estimated_sections": structure_data.get('article_structure', {}).get('estimated_totals', {}).get('sections_count', 0),
                "generated_at": datetime.now().isoformat(),
                "processing_time": processing_time,
                "user_id": current_user.id
            }
        }
        
        sections_count = structure_data.get('article_structure', {}).get('estimated_totals', {}).get('sections_count', 0)
        word_count = structure_data.get('article_structure', {}).get('estimated_totals', {}).get('word_count', 0)
        print(f"✅ 記事構成生成完了: {sections_count}セクション, {word_count:,}文字予定 (処理時間: {processing_time:.2f}秒)")
        
        return result
        
    except Exception as e:
        print(f"❌ 記事構成生成エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"記事構成生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/generate-content", response_model=Dict[str, Any])
async def generate_article_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """記事構成に基づいて完全な記事を生成（Deep Research連携）"""
    
    # 執筆セッションID生成
    session_id = f"writing_{current_user.id}_{int(datetime.now().timestamp())}"
    
    # セッション初期化
    writing_sessions[session_id] = {
        "status": "started",
        "topic": request.topic,
        "target_word_count": request.target_word_count,
        "user_id": current_user.id,
        "started_at": datetime.now().isoformat(),
        "progress": 0,
        "current_step": "初期化中"
    }
    
    # バックグラウンドで執筆実行
    background_tasks.add_task(
        execute_content_generation,
        session_id,
        request
    )
    
    return {
        "session_id": session_id,
        "status": "started",
        "message": f"記事執筆を開始しました: {request.topic}",
        "estimated_time": "15-30分程度",
        "target_word_count": request.target_word_count
    }


async def execute_content_generation(
    session_id: str,
    request: ContentGenerationRequest
):
    """バックグラウンドで記事コンテンツを生成"""
    
    try:
        # 状態更新
        writing_sessions[session_id]["status"] = "processing"
        writing_sessions[session_id]["current_step"] = "Deep Research実行中"
        writing_sessions[session_id]["progress"] = 10
        
        llm = await get_gemini_llm()
        
        # Phase 1: Deep Research実行（競合記事分析）
        if request.use_deep_research:
            writing_sessions[session_id]["current_step"] = "競合記事分析中"
            writing_sessions[session_id]["progress"] = 25
            
            deep_research_data = await perform_deep_research(
                request.topic,
                request.target_keywords,
                llm
            )
        else:
            deep_research_data = {}
        
        # Phase 2: セクション別コンテンツ生成
        writing_sessions[session_id]["current_step"] = "本文執筆中"
        writing_sessions[session_id]["progress"] = 40
        
        article_sections = await generate_article_sections(
            request,
            deep_research_data,
            llm,
            session_id
        )
        
        # Phase 3: 記事統合と最終調整
        writing_sessions[session_id]["current_step"] = "記事統合中"
        writing_sessions[session_id]["progress"] = 80
        
        final_article = await integrate_article_sections(
            request,
            article_sections,
            deep_research_data,
            llm
        )
        
        # Phase 4: SEO最適化とメタデータ生成
        writing_sessions[session_id]["current_step"] = "SEO最適化中"
        writing_sessions[session_id]["progress"] = 90
        
        seo_optimized_article = await optimize_article_seo(
            final_article,
            request.target_keywords,
            llm
        )
        
        # 結果保存
        writing_sessions[session_id].update({
            "status": "completed",
            "progress": 100,
            "current_step": "完了",
            "article_data": seo_optimized_article,
            "deep_research_data": deep_research_data,
            "word_count": len(seo_optimized_article.get('content', '').split()),
            "completed_at": datetime.now().isoformat()
        })
        
        print(f"✅ 記事執筆完了: {session_id}")
        
    except Exception as e:
        # エラー状態更新
        writing_sessions[session_id].update({
            "status": "error",
            "error_message": str(e),
            "completed_at": datetime.now().isoformat()
        })
        print(f"❌ 記事執筆エラー {session_id}: {e}")


async def perform_deep_research(
    topic: str,
    keywords: List[str],
    llm: ChatGoogleGenerativeAI
) -> Dict[str, Any]:
    """競合記事のDeep Researchを実行"""
    
    # 競合記事リサーチプロンプト
    research_prompt = f"""
    「{topic}」に関する上位10サイトの競合記事を分析し、包括的な情報を収集してください。
    
    ターゲットキーワード: {keywords}
    
    以下の情報を収集してください：
    
    1. 競合記事の構成分析
    2. カバーされているトピック
    3. コンテンツギャップの特定
    4. 差別化の機会
    5. 最新情報とトレンド
    
    JSON形式で出力してください。
    """
    
    try:
        response = llm.invoke(research_prompt)
        research_data = parse_json_response(response.content)
        return research_data
    except Exception as e:
        print(f"❌ Deep Researchエラー: {e}")
        return {}


async def generate_article_sections(
    request: ContentGenerationRequest,
    research_data: Dict[str, Any],
    llm: ChatGoogleGenerativeAI,
    session_id: str
) -> List[Dict[str, Any]]:
    """記事の各セクションを個別に生成"""
    
    sections = []
    article_structure = request.article_structure
    
    # 導入部生成
    intro_content = await generate_section_content(
        "introduction",
        article_structure.get("introduction", {}),
        request,
        research_data,
        llm
    )
    sections.append(intro_content)
    
    # メインセクション生成
    main_sections = article_structure.get("sections", [])
    total_sections = len(main_sections)
    
    for idx, section in enumerate(main_sections):
        section_content = await generate_section_content(
            "main_section",
            section,
            request,
            research_data,
            llm
        )
        sections.append(section_content)
        
        # 進行状況更新
        progress = 40 + int((idx + 1) / total_sections * 30)
        writing_sessions[session_id]["progress"] = progress
    
    # 結論部生成
    conclusion_content = await generate_section_content(
        "conclusion",
        article_structure.get("conclusion", {}),
        request,
        research_data,
        llm
    )
    sections.append(conclusion_content)
    
    return sections


async def generate_section_content(
    section_type: str,
    section_structure: Dict[str, Any],
    request: ContentGenerationRequest,
    research_data: Dict[str, Any],
    llm: ChatGoogleGenerativeAI
) -> Dict[str, Any]:
    """個別セクションのコンテンツを生成"""
    
    section_prompt = f"""
    以下のセクションの詳細なコンテンツを作成してください。
    
    セクションタイプ: {section_type}
    セクション構成: {section_structure}
    トピック: {request.topic}
    ターゲットキーワード: {request.target_keywords}
    ライティングスタイル: {request.writing_style}
    
    {'競合記事分析結果:' + str(research_data) if research_data else ''}
    
    以下の要件でコンテンツを作成してください：
    - ユーザーに価値ある情報を提供
    - SEOを意識した自然なキーワード使用
    - 読みやすくエンゲージングな文章
    - 指定されたトーンで執筆
    - 事実に基づいた正確な情報
    
    Markdown形式で出力してください。
    """
    
    try:
        response = llm.invoke(section_prompt)
        content = response.content
        
        return {
            "section_type": section_type,
            "structure": section_structure,
            "content": content,
            "word_count": len(content.split()),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ セクション生成エラー ({section_type}): {e}")
        return {
            "section_type": section_type,
            "structure": section_structure,
            "content": "コンテンツ生成エラー",
            "word_count": 0,
            "error": str(e)
        }


async def integrate_article_sections(
    request: ContentGenerationRequest,
    sections: List[Dict[str, Any]],
    research_data: Dict[str, Any],
    llm: ChatGoogleGenerativeAI
) -> Dict[str, Any]:
    """個別セクションを統合して完整な記事を作成"""
    
    # 各セクションのコンテンツを結合
    full_content = ""
    total_word_count = 0
    
    for section in sections:
        full_content += section.get("content", "") + "\n\n"
        total_word_count += section.get("word_count", 0)
    
    return {
        "title": request.article_structure.get("title", ""),
        "meta_title": request.article_structure.get("meta_title", ""),
        "meta_description": request.article_structure.get("meta_description", ""),
        "content": full_content.strip(),
        "word_count": total_word_count,
        "sections": sections,
        "research_data": research_data,
        "generated_at": datetime.now().isoformat()
    }


async def optimize_article_seo(
    article: Dict[str, Any],
    target_keywords: List[str],
    llm: ChatGoogleGenerativeAI
) -> Dict[str, Any]:
    """記事のSEO最適化を実行"""
    
    seo_prompt = f"""
    以下の記事のSEO最適化を実行し、最終版を作成してください。
    
    記事タイトル: {article.get('title', '')}
    ターゲットキーワード: {target_keywords}
    記事コンテンツ: {article.get('content', '')[:2000]}...
    
    最適化項目：
    1. キーワード密度の調整
    2. 内部リンクの推奨
    3. メタデータの最適化
    4. 構造化データの提案
    5. アイキャッチュ画像の提案
    
    JSON形式で出力してください。
    """
    
    try:
        response = llm.invoke(seo_prompt)
        seo_data = parse_json_response(response.content)
        
        # 元記事にSEO最適化データを追加
        optimized_article = article.copy()
        optimized_article["seo_optimization"] = seo_data
        optimized_article["optimization_completed_at"] = datetime.now().isoformat()
        
        return optimized_article
        
    except Exception as e:
        print(f"❌ SEO最適化エラー: {e}")
        return article


@router.get("/status/{session_id}")
async def get_writing_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """執筆セッションの状態を取得"""
    
    if session_id not in writing_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="執筆セッションが見つかりません"
        )
    
    session = writing_sessions[session_id]
    
    # ユーザーの所有権確認
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセスが拒否されました"
        )
    
    return session


@router.get("/results/{session_id}")
async def get_writing_results(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """執筆セッションの結果を取得"""
    
    if session_id not in writing_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="執筆セッションが見つかりません"
        )
    
    session = writing_sessions[session_id]
    
    # ユーザーの所有権確認
    if session.get("user_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="アクセスが拒否されました"
        )
    
    if session.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="執筆がまだ完了していません。状態を確認してください。"
        )
    
    return {
        "session_info": {
            "session_id": session_id,
            "topic": session.get("topic"),
            "word_count": session.get("word_count"),
            "completed_at": session.get("completed_at")
        },
        "article_data": session.get("article_data", {}),
        "deep_research_data": session.get("deep_research_data", {})
    }


@router.post("/save-article")
async def save_generated_article(
    save_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成された記事をデータベースに保存"""
    
    try:
        article_data = save_request.get("article_data", {})
        
        # Articleモデルに保存
        db_article = Article(
            title=article_data.get("title", ""),
            content=article_data.get("content", ""),
            meta_title=article_data.get("meta_title", ""),
            meta_description=article_data.get("meta_description", ""),
            word_count=article_data.get("word_count", 0),
            status=ArticleStatus.DRAFT,
            content_type=ContentType.BLOG_POST,
            ai_generated=True,
            ai_model_used="gemini-2.0-flash-exp",
            author_id=current_user.id,
            target_keywords=",".join(save_request.get("target_keywords", [])),
            generation_prompt=f"Topic: {save_request.get('topic', '')}"
        )
        
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        
        return {
            "success": True,
            "article_id": db_article.id,
            "message": "記事が正常に保存されました",
            "next_steps": [
                "記事のレビューと編集",
                "SEOスコアの確認",
                "公開スケジュールの設定"
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"記事保存中にエラーが発生しました: {str(e)}"
        )


@router.get("/history")
async def get_writing_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """ユーザーの執筆履歴を取得"""
    
    user_sessions = [
        {
            "session_id": sid,
            "topic": session["topic"],
            "status": session["status"],
            "started_at": session["started_at"],
            "word_count": session.get("word_count", 0)
        }
        for sid, session in writing_sessions.items()
        if session.get("user_id") == current_user.id
    ]
    
    # 開始日時でソート
    user_sessions.sort(key=lambda x: x["started_at"], reverse=True)
    
    return {
        "writing_sessions": user_sessions[:limit],
        "total_count": len(user_sessions)
    }
