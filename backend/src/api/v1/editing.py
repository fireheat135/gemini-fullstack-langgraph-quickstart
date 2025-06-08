"""
SEO記事編集API endpoints - Notion風コマンドパレット、範囲指定修正
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.deps import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.models.article import Article
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings
import json
import re
import uuid


router = APIRouter(prefix="/editing", tags=["editing"])


class EditingCommand(str, Enum):
    """Notion風編集コマンドタイプ"""
    IMPROVE = "improve"                # 改善する
    SIMPLIFY = "simplify"              # シンプルにする
    EXPAND = "expand"                  # 詳しくする
    SUMMARIZE = "summarize"            # 要約する
    REWRITE = "rewrite"                # 書き直す
    FIX_GRAMMAR = "fix_grammar"        # 文法修正
    ADJUST_TONE = "adjust_tone"        # トーン調整
    ADD_EXAMPLES = "add_examples"      # 例を追加
    OPTIMIZE_SEO = "optimize_seo"      # SEO最適化
    FACT_CHECK = "fact_check"          # ファクトチェック
    TRANSLATE = "translate"            # 翻訳
    CUSTOM = "custom"                  # カスタム指示


class TextRange(BaseModel):
    """テキスト範囲指定"""
    start_index: int
    end_index: int
    selected_text: str
    context_before: Optional[str] = ""
    context_after: Optional[str] = ""


class EditingRequest(BaseModel):
    """Notion風編集リクエスト"""
    article_id: Optional[int] = None
    full_text: str
    text_range: TextRange
    command: EditingCommand
    custom_instruction: Optional[str] = None
    target_keywords: List[str] = []
    writing_style: Optional[Dict[str, str]] = None
    target_language: str = "ja"
    preserve_formatting: bool = True


class EditingSuggestion(BaseModel):
    """AI編集提案"""
    suggestion_id: str
    original_text: str
    suggested_text: str
    explanation: str
    confidence_score: float
    command_used: EditingCommand
    improvement_points: List[str]
    seo_impact: Optional[Dict[str, Any]] = None


class EditingResponse(BaseModel):
    """Notion風編集レスポンス"""
    suggestions: List[EditingSuggestion]
    alternative_options: List[str]
    preview_text: str
    word_count_change: int
    readability_improvement: Optional[float] = None
    seo_score_change: Optional[float] = None
    processing_time: float


# 編集セッションのメモリ管理
editing_sessions = {}


async def get_gemini_llm() -> ChatGoogleGenerativeAI:
    """Get Gemini LLM instance"""
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured"
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3,  # 編集では低めの温度
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
        return {}


def get_command_prompt(command: EditingCommand, custom_instruction: str = None) -> str:
    """AIコマンドに対応するプロンプトを生成"""
    
    command_prompts = {
        EditingCommand.IMPROVE: "選択されたテキストをより明確で読みやすく、情報が豊富な内容に改善してください。",
        EditingCommand.SIMPLIFY: "選択されたテキストをよりシンプルでわかりやすい表現に書き換えてください。専門用語を避け、簡潔な文章にしてください。",
        EditingCommand.EXPAND: "選択されたテキストをより詳細に、具体例や補足説明を加えて充実させてください。情報の深度と価値を向上させてください。",
        EditingCommand.SUMMARIZE: "選択されたテキストの要点をつかんで簡潔にまとめてください。重要な情報を欠かすことなく、コンパクトに伝えてください。",
        EditingCommand.REWRITE: "選択されたテキストを完全に書き直してください。同じ意味を保ちながら、より魅力的でインパクトのある表現に変えてください。",
        EditingCommand.FIX_GRAMMAR: "選択されたテキストの文法、スペル、句読点のエラーを修正してください。日本語として自然で正しい表現にしてください。",
        EditingCommand.ADJUST_TONE: "選択されたテキストのトーンを調整してください。指定されたライティングスタイルに合わせて、読者に適切な印象を与えるように修正してください。",
        EditingCommand.ADD_EXAMPLES: "選択されたテキストに具体例、事例、ケーススタディを追加して、読者の理解を深める内容に変更してください。",
        EditingCommand.OPTIMIZE_SEO: "選択されたテキストをSEOに最適化してください。ターゲットキーワードを自然に組み込み、検索エンジンに優しい文章にしてください。",
        EditingCommand.FACT_CHECK: "選択されたテキストの情報を検証し、不正確または曖昧な部分を修正してください。信頼性と正確性を向上させてください。",
        EditingCommand.TRANSLATE: "選択されたテキストを指定された言語に翻訳してください。ニュアンスやコンテキストを保ちながら、自然な翻訳を行ってください。",
        EditingCommand.CUSTOM: custom_instruction or "指定された指示に従ってテキストを修正してください。"
    }
    
    return command_prompts.get(command, command_prompts[EditingCommand.IMPROVE])


@router.post("/suggest", response_model=EditingResponse)
async def suggest_edits(
    request: EditingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Notion風コマンドパレット: 範囲指定したテキストのAI編集提案"""
    
    start_time = datetime.now()
    
    try:
        llm = await get_gemini_llm()
        
        # コマンドに対応するプロンプトを取得
        command_instruction = get_command_prompt(request.command, request.custom_instruction)
        
        # コンテキストを考慮した編集プロンプト
        editing_prompt = f"""
        以下のテキスト編集タスクを実行してください。
        
        【編集指示】
        {command_instruction}
        
        【選択されたテキスト】
        "{request.text_range.selected_text}"
        
        【コンテキスト情報】
        前後のテキスト：
        前: "{request.text_range.context_before[-200:] if request.text_range.context_before else ''}"
        後: "{request.text_range.context_after[:200] if request.text_range.context_after else ''}"
        
        {f'【ターゲットキーワード】{request.target_keywords}' if request.target_keywords else ''}
        
        {f'【ライティングスタイル】{request.writing_style}' if request.writing_style else ''}
        
        以下の要件で編集提案を作成してください：
        
        1. **メイン提案** - 最適な編集結果
        2. **代替案** - 2-3個の異なるアプローチ
        3. **改善ポイント** - 具体的な改善理由
        4. **影響分析** - 文字数、読みやすさ、SEOへの影響
        
        **出力JSON形式:**
        {{
            "main_suggestion": {{
                "suggested_text": "編集後のテキスト",
                "explanation": "編集理由と改善ポイントの詳細説明",
                "confidence_score": 0.95,
                "improvement_points": [
                    "改善ポイント1: 具体的な改善内容",
                    "改善ポイント2: 具体的な改善内容"
                ],
                "word_count_change": +15,
                "readability_improvement": 0.2,
                "seo_impact": {{
                    "keyword_density_change": 0.5,
                    "semantic_enhancement": true,
                    "user_engagement_potential": "high"
                }}
            }},
            "alternative_options": [
                {{
                    "option_text": "代替案1のテキスト",
                    "approach": "アプローチの説明",
                    "pros_cons": "メリット・デメリット"
                }},
                {{
                    "option_text": "代替案2のテキスト",
                    "approach": "アプローチの説明",
                    "pros_cons": "メリット・デメリット"
                }}
            ],
            "preview_full_text": "編集適用後の全体テキストのプレビュー",
            "analysis": {{
                "original_word_count": {len(request.text_range.selected_text.split())},
                "suggested_word_count": "新しい文字数",
                "readability_score_before": 70,
                "readability_score_after": 85,
                "tone_consistency": "maintained",
                "context_alignment": "improved",
                "seo_optimization_level": "enhanced"
            }},
            "implementation_notes": {{
                "preserve_formatting": {str(request.preserve_formatting).lower()},
                "requires_review": false,
                "additional_research_needed": false,
                "estimated_impact": "positive"
            }}
        }}
        
        **重要な注意事項:**
        - 元の意味やメッセージを保持する
        - コンテキストとの一貫性を維持
        - 読者にとっての価値を向上させる
        - SEO効果と読みやすさのバランスを取る
        - 事実に基づいた正確な情報を提供
        """
        
        # AIによる編集提案生成
        response = llm.invoke(editing_prompt)
        editing_data = parse_json_response(response.content)
        
        if not editing_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="編集提案の生成に失敗しました"
            )
        
        # 処理時間計算
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # EditingSuggestionオブジェクトを作成
        main_suggestion = editing_data.get("main_suggestion", {})
        suggestion = EditingSuggestion(
            suggestion_id=str(uuid.uuid4()),
            original_text=request.text_range.selected_text,
            suggested_text=main_suggestion.get("suggested_text", ""),
            explanation=main_suggestion.get("explanation", ""),
            confidence_score=main_suggestion.get("confidence_score", 0.8),
            command_used=request.command,
            improvement_points=main_suggestion.get("improvement_points", []),
            seo_impact=main_suggestion.get("seo_impact")
        )
        
        # 代替案のテキストを抽出
        alternatives = [
            alt.get("option_text", "") 
            for alt in editing_data.get("alternative_options", [])
        ]
        
        # プレビューテキストを作成
        preview_text = create_preview_text(
            request.full_text,
            request.text_range,
            main_suggestion.get("suggested_text", "")
        )
        
        # 文字数変化を計算
        original_word_count = len(request.text_range.selected_text.split())
        suggested_word_count = len(main_suggestion.get("suggested_text", "").split())
        word_count_change = suggested_word_count - original_word_count
        
        # レスポンス作成
        response_data = EditingResponse(
            suggestions=[suggestion],
            alternative_options=alternatives,
            preview_text=preview_text,
            word_count_change=word_count_change,
            readability_improvement=main_suggestion.get("readability_improvement"),
            seo_score_change=main_suggestion.get("seo_impact", {}).get("keyword_density_change"),
            processing_time=processing_time
        )
        
        # 編集セッションを保存
        session_id = f"edit_{current_user.id}_{int(datetime.now().timestamp())}"
        editing_sessions[session_id] = {
            "user_id": current_user.id,
            "original_request": request.model_dump(),
            "suggestions": editing_data,
            "created_at": datetime.now().isoformat()
        }
        
        print(f"✅ 編集提案生成完了: {request.command.value} (処理時間: {processing_time:.2f}秒)")
        
        return response_data
        
    except Exception as e:
        print(f"❌ 編集提案エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"編集提案中にエラーが発生しました: {str(e)}"
        )


def create_preview_text(
    full_text: str,
    text_range: TextRange,
    suggested_text: str
) -> str:
    """編集適用後のプレビューテキストを作成"""
    
    try:
        # 元のテキストを編集範囲で分割
        before_text = full_text[:text_range.start_index]
        after_text = full_text[text_range.end_index:]
        
        # 新しいテキストで結合
        preview = before_text + suggested_text + after_text
        
        return preview
        
    except Exception as e:
        print(f"❌ プレビュー作成エラー: {e}")
        return full_text  # エラー時は元のテキストを返す


@router.post("/apply")
async def apply_editing_suggestion(
    apply_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """編集提案を実際のテキストに適用"""
    
    try:
        suggestion_id = apply_request.get("suggestion_id")
        article_id = apply_request.get("article_id")
        apply_to_full_text = apply_request.get("apply_to_full_text", True)
        
        if article_id:
            # データベースの記事を更新
            article = db.query(Article).filter(
                Article.id == article_id,
                Article.author_id == current_user.id
            ).first()
            
            if not article:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="記事が見つかりません"
                )
            
            # 編集を適用
            if apply_to_full_text and "updated_content" in apply_request:
                article.content = apply_request["updated_content"]
                article.word_count = len(apply_request["updated_content"].split())
                article.updated_at = datetime.utcnow()
                
                db.commit()
                db.refresh(article)
                
                return {
                    "success": True,
                    "message": "編集が正常に適用されました",
                    "article_id": article.id,
                    "new_word_count": article.word_count
                }
        
        # テキストのみの編集の場合
        return {
            "success": True,
            "message": "編集が適用されました",
            "updated_text": apply_request.get("updated_content", "")
        }
        
    except Exception as e:
        if article_id:
            db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"編集適用中にエラーが発生しました: {str(e)}"
        )


@router.get("/commands")
async def get_available_commands():
    """利用可能な編集コマンドの一覧を取得"""
    
    commands = [
        {
            "command": EditingCommand.IMPROVE.value,
            "display_name": "改善する",
            "description": "テキストをより明確で読みやすく改善します",
            "icon": "sparkles",
            "category": "quality"
        },
        {
            "command": EditingCommand.SIMPLIFY.value,
            "display_name": "シンプルにする",
            "description": "よりわかりやすい表現に書き換えます",
            "icon": "minimize-2",
            "category": "clarity"
        },
        {
            "command": EditingCommand.EXPAND.value,
            "display_name": "詳しくする",
            "description": "具体例や補足説明を加えて充実させます",
            "icon": "maximize-2",
            "category": "depth"
        },
        {
            "command": EditingCommand.SUMMARIZE.value,
            "display_name": "要約する",
            "description": "要点をつかんで簡潔にまとめます",
            "icon": "list",
            "category": "brevity"
        },
        {
            "command": EditingCommand.REWRITE.value,
            "display_name": "書き直す",
            "description": "完全に書き直してより魅力的にします",
            "icon": "edit-3",
            "category": "creativity"
        },
        {
            "command": EditingCommand.FIX_GRAMMAR.value,
            "display_name": "文法修正",
            "description": "文法、スペル、句読点のエラーを修正します",
            "icon": "check-circle",
            "category": "accuracy"
        },
        {
            "command": EditingCommand.ADJUST_TONE.value,
            "display_name": "トーン調整",
            "description": "文章のトーンやスタイルを調整します",
            "icon": "volume-2",
            "category": "style"
        },
        {
            "command": EditingCommand.ADD_EXAMPLES.value,
            "display_name": "例を追加",
            "description": "具体例や事例を追加して理解しやすくします",
            "icon": "plus-circle",
            "category": "clarity"
        },
        {
            "command": EditingCommand.OPTIMIZE_SEO.value,
            "display_name": "SEO最適化",
            "description": "キーワードを組み込み検索エンジンに最適化します",
            "icon": "trending-up",
            "category": "seo"
        },
        {
            "command": EditingCommand.FACT_CHECK.value,
            "display_name": "ファクトチェック",
            "description": "情報の正確性を検証し、信頼性を向上させます",
            "icon": "shield-check",
            "category": "accuracy"
        },
        {
            "command": EditingCommand.TRANSLATE.value,
            "display_name": "翻訳",
            "description": "指定した言語に自然に翻訳します",
            "icon": "globe",
            "category": "language"
        },
        {
            "command": EditingCommand.CUSTOM.value,
            "display_name": "カスタム指示",
            "description": "独自の指示でカスタマイズした編集を実行します",
            "icon": "settings",
            "category": "custom"
        }
    ]
    
    return {
        "commands": commands,
        "categories": [
            {"id": "quality", "name": "品質改善"},
            {"id": "clarity", "name": "わかりやすさ"},
            {"id": "depth", "name": "内容の深み"},
            {"id": "brevity", "name": "簡潔性"},
            {"id": "creativity", "name": "創造性"},
            {"id": "accuracy", "name": "正確性"},
            {"id": "style", "name": "スタイル"},
            {"id": "seo", "name": "SEO最適化"},
            {"id": "language", "name": "言語"},
            {"id": "custom", "name": "カスタム"}
        ]
    }


@router.post("/batch-edit")
async def batch_edit_suggestions(
    batch_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """複数のテキスト範囲に対する一括編集提案"""
    
    try:
        edit_requests = batch_request.get("edit_requests", [])
        if not edit_requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="編集リクエストが指定されていません"
            )
        
        results = []
        
        for idx, edit_req in enumerate(edit_requests):
            try:
                # 個別の編集リクエストを作成
                request = EditingRequest(**edit_req)
                
                # 編集提案を取得
                suggestion_response = await suggest_edits(request, current_user, db)
                
                results.append({
                    "index": idx,
                    "success": True,
                    "suggestion": suggestion_response.model_dump()
                })
                
            except Exception as e:
                results.append({
                    "index": idx,
                    "success": False,
                    "error": str(e)
                })
        
        successful_edits = len([r for r in results if r["success"]])
        
        return {
            "batch_results": results,
            "summary": {
                "total_requests": len(edit_requests),
                "successful_edits": successful_edits,
                "failed_edits": len(edit_requests) - successful_edits
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"一括編集中にエラーが発生しました: {str(e)}"
        )


@router.get("/history")
async def get_editing_history(
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """ユーザーの編集履歴を取得"""
    
    user_sessions = [
        {
            "session_id": sid,
            "command": session["original_request"]["command"],
            "selected_text_preview": session["original_request"]["text_range"]["selected_text"][:100] + "...",
            "created_at": session["created_at"]
        }
        for sid, session in editing_sessions.items()
        if session.get("user_id") == current_user.id
    ]
    
    # 作成日時でソート
    user_sessions.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "editing_history": user_sessions[:limit],
        "total_count": len(user_sessions)
    }
