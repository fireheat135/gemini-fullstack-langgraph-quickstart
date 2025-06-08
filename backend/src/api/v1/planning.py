"""
SEO記事企画API endpoints - 4パターンのコンセプト・トンマナ生成
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.db.deps import get_db
from src.api.deps import get_current_user
from src.models.user import User
from src.services.ai.ai_service_manager import AIServiceManager
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.config import settings
import json


router = APIRouter(prefix="/planning", tags=["planning"])


class PlanningRequest(BaseModel):
    topic: str
    target_keywords: List[str] = []
    research_data: Optional[Dict[str, Any]] = None
    target_audience: str = "一般ユーザー"
    content_type: str = "ブログ記事"
    business_goals: List[str] = ["SEO向上", "ブランド認知"]


class PlanningPattern(BaseModel):
    type: str
    target_persona: str
    title: str
    meta_description: str
    structure: List[Dict[str, Any]]
    estimated_word_count: int
    expected_pv: int
    expected_cvr: float
    required_time: str
    required_expertise: str
    tone_manner: Dict[str, str]
    differentiation: List[str]


class PlanningResponse(BaseModel):
    planning_patterns: List[PlanningPattern]
    recommendation: Dict[str, Any]
    analysis_summary: Dict[str, Any]
    generated_at: str
    processing_time: float


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
    # JSONブロックを抽出
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


@router.post("/generate-patterns", response_model=Dict[str, Any])
async def generate_planning_patterns(
    request: PlanningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """4パターンの記事企画案を生成"""
    
    start_time = datetime.now()
    
    try:
        llm = await get_gemini_llm()
        
        # 現在の日付取得
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        planning_prompt = f"""
        「{request.topic}」について、戦略的なSEO記事企画を4パターン作成してください。
        
        【基本情報】
        - トピック: {request.topic}
        - ターゲットキーワード: {request.target_keywords}
        - ターゲットオーディエンス: {request.target_audience}
        - コンテンツタイプ: {request.content_type}
        - ビジネス目標: {request.business_goals}
        - 現在日付: {current_date}
        
        {'【リサーチデータ】' + str(request.research_data) if request.research_data else ''}
        
        以下の4つの企画パターンで記事案を作成してください：
        
        1. **初心者向け解説型** - 基礎知識や入門情報を丁寧に解説
        2. **専門家向け詳細型** - 深い洞察や高度なテクニックを提供
        3. **実践・How-to型** - 具体的な手順やステップバイステップガイド
        4. **比較・まとめ型** - 複数選択肢の比較や包括的なまとめ
        
        各企画案について以下を含めてください：
        
        **必須要素:**
        - ターゲットペルソナ（年齢、職業、知識レベル、課題）
        - SEO最適化されたタイトル（H1）
        - 魅力的なメタディスクリプション（150-160文字）
        - 詳細な記事構成（H2-H3レベルの見出し構造）
        - 推定文字数（根拠含む）
        - 現実的なPV・CVR予測
        - 必要な制作時間と専門性レベル
        - 具体的なトンマナ設定（文体、語調、キャラクター）
        - 競合との差別化ポイント
        
        **出力JSON形式:**
        {{
            "planning_patterns": [
                {{
                    "type": "初心者向け解説型",
                    "target_persona": {{
                        "age_range": "年齢層",
                        "occupation": "職業",
                        "knowledge_level": "知識レベル",
                        "pain_points": ["課題1", "課題2"],
                        "goals": ["目標1", "目標2"]
                    }},
                    "title": "SEO最適化されたタイトル",
                    "meta_description": "150-160文字のメタディスクリプション",
                    "structure": [
                        {{
                            "h2": "大見出し1",
                            "h3_items": ["小見出し1-1", "小見出し1-2"],
                            "estimated_words": 500,
                            "purpose": "セクションの目的"
                        }}
                    ],
                    "estimated_word_count": 3000,
                    "word_count_rationale": "文字数の根拠",
                    "expected_pv": 5000,
                    "expected_cvr": 0.03,
                    "pv_cvr_rationale": "予測の根拠",
                    "required_time": "8-12時間",
                    "required_expertise": "中級レベル",
                    "tone_manner": {{
                        "style": "です・ます調",
                        "voice": "親しみやすい",
                        "personality": "専門知識を持つ友人",
                        "specific_examples": ["語尾の特徴", "使用する敬語レベル"]
                    }},
                    "differentiation": ["差別化ポイント1", "差別化ポイント2"],
                    "seo_strategy": {{
                        "primary_keyword_placement": "キーワード配置戦略",
                        "secondary_keywords": ["サブキーワード1", "サブキーワード2"],
                        "content_depth": "コンテンツの深さレベル"
                    }},
                    "engagement_strategy": {{
                        "hook": "読者を引きつける要素",
                        "retention_tactics": ["読み続けさせる工夫1", "工夫2"],
                        "call_to_action": "具体的なCTA"
                    }}
                }}
            ],
            "recommendation": {{
                "best_pattern": "推奨パターン名",
                "reason": "詳細な推奨理由（SEO効果、リソース効率、競合優位性を含む）",
                "success_probability": 85,
                "risk_factors": ["リスク要因1", "リスク要因2"],
                "mitigation_strategies": ["リスク軽減策1", "軽減策2"]
            }},
            "analysis_summary": {{
                "market_opportunity": "市場機会の分析",
                "competitive_landscape": "競合状況の分析", 
                "user_demand_analysis": "ユーザーニーズの分析",
                "content_gap_identification": ["コンテンツギャップ1", "ギャップ2"],
                "optimal_timing": "最適な公開タイミング",
                "resource_allocation": "推奨リソース配分"
            }},
            "implementation_guidance": {{
                "priority_order": ["実装優先順位1", "優先順位2"],
                "quality_checkpoints": ["品質チェックポイント1", "ポイント2"],
                "success_metrics": {{
                    "short_term": ["短期指標1", "指標2"],
                    "long_term": ["長期指標1", "指標2"]
                }}
            }}
        }}
        
        **重要な考慮事項:**
        - 各パターンは明確に差別化され、異なるユーザーニーズに対応
        - SEO効果と読者価値のバランスを重視
        - 現実的で実装可能な企画案
        - 競合分析に基づく戦略的差別化
        - 測定可能な成功指標の設定
        """
        
        # AI による企画生成
        response = llm.invoke(planning_prompt)
        planning_data = parse_json_response(response.content)
        
        if not planning_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER,
                detail="企画データの生成に失敗しました"
            )
        
        # 処理時間計算
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # レスポンス構築
        result = {
            "success": True,
            "data": planning_data,
            "metadata": {
                "topic": request.topic,
                "target_keywords": request.target_keywords,
                "target_audience": request.target_audience,
                "generated_at": datetime.now().isoformat(),
                "processing_time": processing_time,
                "user_id": current_user.id
            }
        }
        
        patterns_count = len(planning_data.get("planning_patterns", []))
        print(f"✅ 企画生成完了: {patterns_count}パターン生成 (処理時間: {processing_time:.2f}秒)")
        
        return result
        
    except Exception as e:
        print(f"❌ 企画生成エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"企画生成中にエラーが発生しました: {str(e)}"
        )


@router.post("/select-pattern")
async def select_planning_pattern(
    pattern_selection: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """選択された企画パターンを確定し、次のステップへ進む"""
    
    required_fields = ["selected_pattern", "planning_id", "customizations"]
    for field in required_fields:
        if field not in pattern_selection:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"必須フィールドが不足しています: {field}"
            )
    
    try:
        # 選択された企画パターンの保存・処理ロジック
        # （実際の実装では、データベースに保存やセッション管理を行う）
        
        result = {
            "success": True,
            "message": "企画パターンが選択されました",
            "selected_pattern": pattern_selection["selected_pattern"],
            "next_step": "writing",
            "next_step_url": "/api/v1/writing/generate-structure",
            "estimated_completion_time": "30-60分"
        }
        
        return result
        
    except Exception as e:
        print(f"❌ パターン選択エラー: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"パターン選択中にエラーが発生しました: {str(e)}"
        )


@router.get("/patterns/history")
async def get_planning_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """ユーザーの企画履歴を取得"""
    
    # 実装例（実際はデータベースから取得）
    mock_history = [
        {
            "id": "planning_123",
            "topic": "誕生花",
            "created_at": "2024-01-15T10:00:00Z",
            "status": "completed",
            "selected_pattern": "初心者向け解説型",
            "estimated_pv": 5000
        }
    ]
    
    return {
        "planning_history": mock_history,
        "total_count": len(mock_history)
    }


@router.post("/customize-pattern")
async def customize_planning_pattern(
    customization_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """選択した企画パターンをカスタマイズ"""
    
    try:
        llm = await get_gemini_llm()
        
        customization_prompt = f"""
        以下の企画パターンをユーザーの要求に基づいてカスタマイズしてください。
        
        【元の企画パターン】
        {customization_request.get('original_pattern', {})}
        
        【カスタマイズ要求】
        {customization_request.get('customization_requests', [])}
        
        【制約条件】
        - SEO効果を維持すること
        - 実装可能性を考慮すること  
        - ブランドトーンとの整合性を保つこと
        
        カスタマイズされた企画パターンを元の形式で出力してください。
        """
        
        response = llm.invoke(customization_prompt)
        customized_data = parse_json_response(response.content)
        
        return {
            "success": True,
            "customized_pattern": customized_data,
            "changes_summary": customization_request.get('customization_requests', []),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"カスタマイズ中にエラーが発生しました: {str(e)}"
        )


@router.post("/validate-pattern")
async def validate_planning_pattern(
    validation_request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """企画パターンの妥当性を検証"""
    
    try:
        pattern = validation_request.get('pattern', {})
        
        # 基本的な検証ロジック
        validation_results = {
            "seo_score": 0,
            "feasibility_score": 0,
            "market_potential_score": 0,
            "issues": [],
            "recommendations": []
        }
        
        # タイトル検証
        title = pattern.get('title', '')
        if len(title) < 30 or len(title) > 60:
            validation_results["issues"].append("タイトル長が最適範囲外です（30-60文字推奨）")
            validation_results["seo_score"] -= 10
        else:
            validation_results["seo_score"] += 20
        
        # メタディスクリプション検証
        meta_desc = pattern.get('meta_description', '')
        if len(meta_desc) < 150 or len(meta_desc) > 160:
            validation_results["issues"].append("メタディスクリプション長が最適範囲外です（150-160文字推奨）")
            validation_results["seo_score"] -= 10
        else:
            validation_results["seo_score"] += 20
        
        # 文字数検証
        word_count = pattern.get('estimated_word_count', 0)
        if word_count < 1000:
            validation_results["issues"].append("推定文字数が少なすぎます（1000文字以上推奨）")
            validation_results["feasibility_score"] -= 15
        elif word_count > 8000:
            validation_results["issues"].append("推定文字数が多すぎます（リソース不足の可能性）")
            validation_results["feasibility_score"] -= 10
        else:
            validation_results["feasibility_score"] += 20
        
        # 市場ポテンシャル評価
        expected_pv = pattern.get('expected_pv', 0)
        if expected_pv > 1000:
            validation_results["market_potential_score"] += 25
        
        # 総合スコア計算
        total_score = max(0, min(100, 
            validation_results["seo_score"] + 
            validation_results["feasibility_score"] + 
            validation_results["market_potential_score"]
        ))
        
        # 推奨事項生成
        if total_score < 70:
            validation_results["recommendations"].append("企画の見直しを推奨します")
        if validation_results["seo_score"] < 30:
            validation_results["recommendations"].append("SEO要素の強化が必要です")
        if validation_results["feasibility_score"] < 30:
            validation_results["recommendations"].append("実装難易度を下げることを検討してください")
        
        return {
            "validation_score": total_score,
            "detailed_scores": validation_results,
            "is_recommended": total_score >= 70,
            "validation_summary": f"総合スコア: {total_score}/100 ({'推奨' if total_score >= 70 else '要改善'})"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"検証中にエラーが発生しました: {str(e)}"
        )
