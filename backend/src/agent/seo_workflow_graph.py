#!/usr/bin/env python3
"""
SEO記事作成7ステップワークフロー
リサーチ→企画→執筆→修正→出稿→分析→改善の完全自動化システム
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from .state import OverallState
from .configuration import Configuration
from .utils import get_research_topic
from .prompts import get_current_date


class WorkflowStep(Enum):
    """ワークフロー段階"""
    RESEARCH = "research"           # リサーチ
    PLANNING = "planning"           # 企画  
    WRITING = "writing"            # 執筆
    EDITING = "editing"            # 修正
    PUBLISHING = "publishing"      # 出稿
    ANALYSIS = "analysis"          # 分析
    IMPROVEMENT = "improvement"    # 改善


@dataclass
class SEOWorkflowState:
    """SEOワークフロー状態"""
    current_step: WorkflowStep
    topic: str
    target_keywords: List[str] = None
    research_data: Dict[str, Any] = None
    planning_data: Dict[str, Any] = None
    article_content: str = None
    article_metadata: Dict[str, Any] = None
    performance_data: Dict[str, Any] = None
    improvement_suggestions: List[str] = None
    workflow_id: str = None
    created_at: datetime = None
    updated_at: datetime = None


class SEOWorkflowOrchestrator:
    """SEO記事作成ワークフロー統合管理"""
    
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            api_key=gemini_api_key
        )
    
    # ============================================================
    # Step 1: リサーチ (Research)
    # ============================================================
    
    def step_1_research(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 1: リサーチ段階
        - キーワード分析 (Hrefs/ラッコキーワード風)
        - 競合記事分析 (Deep Research活用)
        - ユーザーニーズ分析
        - トレンド分析
        """
        print("🔍 Step 1: リサーチ開始")
        
        research_prompt = f"""
        「{state.topic}」について包括的なSEOリサーチを実行してください。
        
        以下の項目を調査し、JSON形式で結果を出力してください：
        
        1. キーワード分析
           - メインキーワードの検索ボリューム推定
           - 関連キーワード30個（ロングテール含む）
           - 競合性評価（Easy/Medium/Hard）
           - 検索意図分類（情報収集/購買/ナビゲーション）
        
        2. 競合記事分析
           - 上位10サイトの想定タイトル・構成
           - 平均文字数
           - 差別化ポイント
        
        3. ユーザーニーズ分析
           - ターゲットペルソナ3パターン
           - 各ペルソナの検索意図
           - 解決すべき課題・悩み
        
        4. トレンド分析
           - 季節性・時期性
           - 関連トピックのトレンド
           - 急上昇キーワード
        
        出力形式：
        {{
            "keywords": {{
                "main": "{state.topic}",
                "related": ["関連キーワード1", ...],
                "long_tail": ["ロングテール1", ...],
                "search_volumes": {{"キーワード": 推定月間検索数}},
                "competition": {{"キーワード": "Easy/Medium/Hard"}},
                "search_intent": {{"キーワード": "情報収集/購買/ナビゲーション"}}
            }},
            "competitors": [
                {{
                    "title": "想定タイトル",
                    "structure": ["H2見出し1", "H2見出し2", ...],
                    "word_count": 推定文字数,
                    "strength": "強み",
                    "weakness": "弱み"
                }}
            ],
            "user_personas": [
                {{
                    "name": "ペルソナ名",
                    "demographics": "属性",
                    "search_intent": "検索意図",
                    "pain_points": ["課題1", "課題2", ...],
                    "goals": ["目標1", "目標2", ...]
                }}
            ],
            "trends": {{
                "seasonality": "季節性の説明",
                "related_topics": ["関連トピック1", ...],
                "trending_keywords": ["急上昇キーワード1", ...]
            }}
        }}
        
        現在の日付: {get_current_date()}
        リサーチ対象: {state.topic}
        """
        
        try:
            response = self.llm.invoke(research_prompt)
            research_data = self._parse_json_response(response.content)
            
            state.research_data = research_data
            state.target_keywords = research_data.get("keywords", {}).get("related", [])[:10]
            state.current_step = WorkflowStep.PLANNING
            
            print(f"✅ リサーチ完了: {len(state.target_keywords)}個のキーワード発見")
            return {"research_data": research_data, "step": "planning"}
            
        except Exception as e:
            print(f"❌ リサーチエラー: {e}")
            return {"error": str(e), "step": "research"}
    
    # ============================================================
    # Step 2: 企画 (Planning)
    # ============================================================
    
    def step_2_planning(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 2: 企画段階
        - 4パターンの記事企画案生成
        - トンマナ設計
        - 記事構成設計
        - 成果予測
        """
        print("📋 Step 2: 企画開始")
        
        planning_prompt = f"""
        リサーチ結果を基に、「{state.topic}」の記事企画を4パターン作成してください。
        
        リサーチデータ:
        {state.research_data}
        
        以下の4つの企画パターンで記事案を作成してください：
        
        1. 初心者向け解説型
        2. 専門家向け詳細型  
        3. 実践・How-to型
        4. 比較・まとめ型
        
        各企画案について以下を含めてください：
        
        - ターゲットペルソナ
        - 記事タイトル（H1）
        - メタディスクリプション
        - 記事構成（H2-H3レベル）
        - 推定文字数
        - 予想PV・CVR
        - 必要リソース（時間・専門性）
        - トンマナ設定
        - 差別化ポイント
        
        出力形式：
        {{
            "planning_patterns": [
                {{
                    "type": "初心者向け解説型",
                    "target_persona": "ペルソナ説明",
                    "title": "記事タイトル",
                    "meta_description": "メタディスクリプション",
                    "structure": [
                        {{
                            "h2": "大見出し",
                            "h3_items": ["小見出し1", "小見出し2", ...]
                        }}
                    ],
                    "estimated_word_count": 数値,
                    "expected_pv": 数値,
                    "expected_cvr": 数値,
                    "required_time": "時間",
                    "required_expertise": "必要専門性",
                    "tone_manner": {{
                        "style": "文体",
                        "voice": "語調", 
                        "personality": "キャラクター"
                    }},
                    "differentiation": ["差別化ポイント1", ...]
                }}
            ],
            "recommendation": {{
                "best_pattern": "推奨パターン",
                "reason": "推奨理由",
                "success_probability": 数値
            }}
        }}
        """
        
        try:
            response = self.llm.invoke(planning_prompt)
            planning_data = self._parse_json_response(response.content)
            
            state.planning_data = planning_data
            state.current_step = WorkflowStep.WRITING
            
            patterns_count = len(planning_data.get("planning_patterns", []))
            print(f"✅ 企画完了: {patterns_count}パターン生成")
            return {"planning_data": planning_data, "step": "writing"}
            
        except Exception as e:
            print(f"❌ 企画エラー: {e}")
            return {"error": str(e), "step": "planning"}
    
    # ============================================================
    # Step 3: 執筆 (Writing)
    # ============================================================
    
    def step_3_writing(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 3: 執筆段階
        - 推奨企画案の記事執筆
        - SEO最適化
        - メタ情報生成
        - サムネイル生成指示
        """
        print("✍️ Step 3: 執筆開始")
        
        # 推奨企画案を選択
        recommended_pattern = None
        if state.planning_data and "recommendation" in state.planning_data:
            best_pattern_name = state.planning_data["recommendation"]["best_pattern"]
            for pattern in state.planning_data.get("planning_patterns", []):
                if pattern["type"] == best_pattern_name:
                    recommended_pattern = pattern
                    break
        
        if not recommended_pattern:
            return {"error": "推奨企画案が見つかりません", "step": "planning"}
        
        writing_prompt = f"""
        以下の企画案に基づいて、完全なSEO記事を執筆してください。
        
        企画案:
        {recommended_pattern}
        
        キーワード情報:
        {state.target_keywords}
        
        執筆要件:
        1. 指定された構成に従って詳細な記事を作成
        2. 自然なキーワード配置でSEO効果を最大化
        3. ユーザーの検索意図を完全に満たす内容
        4. 専門性・権威性・信頼性(E-A-T)を重視
        5. 読みやすく魅力的な文章
        6. 目標文字数: {recommended_pattern.get('estimated_word_count', 4000)}文字
        
        出力形式：
        {{
            "article": {{
                "title": "記事タイトル",
                "meta_description": "メタディスクリプション", 
                "content": "Markdown形式の記事本文",
                "word_count": 実際の文字数,
                "keywords_used": ["使用キーワード1", ...],
                "internal_links": ["内部リンク候補1", ...],
                "external_links": ["外部リンク候補1", ...]
            }},
            "seo_optimization": {{
                "title_seo_score": 数値,
                "keyword_density": 数値,
                "readability_score": 数値,
                "meta_optimized": true/false
            }},
            "thumbnail_prompt": "サムネイル生成用のプロンプト",
            "social_media": {{
                "twitter_summary": "Twitter用要約",
                "facebook_description": "Facebook用説明",
                "linkedin_summary": "LinkedIn用要約"
            }}
        }}
        """
        
        try:
            response = self.llm.invoke(writing_prompt)
            writing_data = self._parse_json_response(response.content)
            
            state.article_content = writing_data.get("article", {}).get("content", "")
            state.article_metadata = {
                "title": writing_data.get("article", {}).get("title", ""),
                "meta_description": writing_data.get("article", {}).get("meta_description", ""),
                "word_count": writing_data.get("article", {}).get("word_count", 0),
                "seo_score": writing_data.get("seo_optimization", {}),
                "thumbnail_prompt": writing_data.get("thumbnail_prompt", ""),
                "social_media": writing_data.get("social_media", {})
            }
            state.current_step = WorkflowStep.EDITING
            
            word_count = state.article_metadata.get("word_count", 0)
            print(f"✅ 執筆完了: {word_count:,}文字の記事生成")
            return {"article_data": writing_data, "step": "editing"}
            
        except Exception as e:
            print(f"❌ 執筆エラー: {e}")
            return {"error": str(e), "step": "writing"}
    
    # ============================================================
    # Step 4: 修正 (Editing) 
    # ============================================================
    
    def step_4_editing(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 4: 修正段階
        - AIによる記事品質チェック
        - SEO最適化提案
        - 改善案生成
        - Notion風編集候補生成
        """
        print("🔧 Step 4: 修正・編集開始")
        
        editing_prompt = f"""
        作成された記事を詳細に分析し、改善提案を行ってください。
        
        記事タイトル: {state.article_metadata.get('title', '')}
        記事内容: {state.article_content[:2000]}...
        
        以下の観点で分析・改善提案してください：
        
        1. SEO最適化
           - タイトルの改善案
           - メタディスクリプションの改善案  
           - キーワード配置の最適化
           - 見出し構成の改善
        
        2. コンテンツ品質
           - 情報の正確性・網羅性
           - 論理構成の改善
           - 読みやすさの向上
           - E-A-T強化案
        
        3. ユーザーエクスペリエンス
           - 導入部の魅力向上
           - 中間部の engagement維持
           - 結論部の action促進
           - 視覚的要素の提案
        
        4. Notion風編集コマンド
           - 具体的な編集指示
           - 置換すべき文章と改善案
           - 追加すべき情報
           - 削除すべき箇所
        
        出力形式:
        {{
            "seo_improvements": {{
                "title_suggestions": ["改善タイトル案1", ...],
                "meta_suggestions": ["改善メタ案1", ...], 
                "keyword_optimization": ["最適化提案1", ...],
                "structure_improvements": ["構成改善案1", ...]
            }},
            "content_improvements": {{
                "accuracy_fixes": ["正確性改善1", ...],
                "logic_improvements": ["論理改善1", ...],
                "readability_fixes": ["読みやすさ改善1", ...],
                "eat_enhancements": ["E-A-T強化案1", ...]
            }},
            "ux_improvements": {{
                "intro_enhancements": ["導入改善1", ...],
                "engagement_tips": ["engagement改善1", ...],
                "cta_improvements": ["CTA改善1", ...],
                "visual_suggestions": ["視覚的改善1", ...]
            }},
            "editing_commands": [
                {{
                    "type": "replace",
                    "target": "置換対象文章",
                    "replacement": "改善文章", 
                    "reason": "改善理由"
                }},
                {{
                    "type": "add",
                    "position": "追加位置",
                    "content": "追加内容",
                    "reason": "追加理由"
                }},
                {{
                    "type": "delete", 
                    "target": "削除対象",
                    "reason": "削除理由"
                }}
            ],
            "overall_score": {{
                "seo_score": 数値,
                "content_score": 数値,
                "ux_score": 数値,
                "overall_score": 数値
            }}
        }}
        """
        
        try:
            response = self.llm.invoke(editing_prompt)
            editing_data = self._parse_json_response(response.content)
            
            state.current_step = WorkflowStep.PUBLISHING
            
            commands_count = len(editing_data.get("editing_commands", []))
            overall_score = editing_data.get("overall_score", {}).get("overall_score", 0)
            print(f"✅ 編集分析完了: {commands_count}個の改善提案 (スコア: {overall_score})")
            return {"editing_data": editing_data, "step": "publishing"}
            
        except Exception as e:
            print(f"❌ 編集エラー: {e}")
            return {"error": str(e), "step": "editing"}
    
    # ============================================================
    # Step 5: 出稿 (Publishing)
    # ============================================================
    
    def step_5_publishing(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 5: 出稿段階
        - 公開スケジュール最適化
        - CMS連携準備
        - SNS投稿準備
        - パフォーマンス追跡設定
        """
        print("📤 Step 5: 出稿準備開始")
        
        publishing_prompt = f"""
        記事の出稿戦略を策定してください。
        
        記事情報:
        - タイトル: {state.article_metadata.get('title', '')}
        - 文字数: {state.article_metadata.get('word_count', 0)}
        - ターゲットキーワード: {state.target_keywords[:5]}
        
        以下の出稿戦略を立案してください：
        
        1. 公開タイミング最適化
           - 最適な公開日時
           - 曜日・時間帯の根拠
           - 季節性・トレンドを考慮
        
        2. CMS設定
           - カテゴリ・タグ設定
           - URL構造提案
           - 内部リンク戦略
           - 関連記事設定
        
        3. SNS戦略
           - Twitter投稿文案
           - Facebook投稿文案
           - LinkedIn投稿文案
           - Instagram投稿アイデア
        
        4. パフォーマンス追跡
           - 追跡すべきKPI
           - 分析期間設定
           - 比較対象記事
           - 成功指標定義
        
        出力形式:
        {{
            "publishing_schedule": {{
                "optimal_datetime": "YYYY-MM-DD HH:MM",
                "dayofweek_reason": "曜日選択理由",
                "time_reason": "時間選択理由",
                "seasonal_consideration": "季節性考慮"
            }},
            "cms_settings": {{
                "categories": ["カテゴリ1", ...],
                "tags": ["タグ1", ...],
                "url_slug": "url-slug",
                "internal_links": ["内部リンクURL1", ...],
                "related_articles": ["関連記事1", ...]
            }},
            "social_media_strategy": {{
                "twitter": {{
                    "posts": ["投稿文1", "投稿文2", ...],
                    "hashtags": ["#ハッシュタグ1", ...],
                    "timing": ["投稿タイミング1", ...]
                }},
                "facebook": {{
                    "post": "Facebook投稿文",
                    "image_suggestion": "画像提案"
                }},
                "linkedin": {{
                    "post": "LinkedIn投稿文", 
                    "professional_angle": "専門性アピール"
                }}
            }},
            "performance_tracking": {{
                "kpis": ["KPI1", "KPI2", ...],
                "tracking_period": "追跡期間",
                "comparison_articles": ["比較記事1", ...],
                "success_criteria": {{
                    "pv_target": 数値,
                    "engagement_target": 数値,
                    "conversion_target": 数値
                }}
            }}
        }}
        """
        
        try:
            response = self.llm.invoke(publishing_prompt)
            publishing_data = self._parse_json_response(response.content)
            
            state.current_step = WorkflowStep.ANALYSIS
            
            optimal_time = publishing_data.get("publishing_schedule", {}).get("optimal_datetime", "")
            print(f"✅ 出稿戦略完了: 最適公開時刻 {optimal_time}")
            return {"publishing_data": publishing_data, "step": "analysis"}
            
        except Exception as e:
            print(f"❌ 出稿戦略エラー: {e}")
            return {"error": str(e), "step": "publishing"}
    
    # ============================================================
    # Step 6: 分析 (Analysis)
    # ============================================================
    
    def step_6_analysis(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 6: 分析段階
        - パフォーマンス予測
        - タギング戦略
        - 分析フレームワーク設定
        - ベンチマーク設定
        """
        print("📊 Step 6: 分析フレームワーク設定開始")
        
        analysis_prompt = f"""
        記事のパフォーマンス分析フレームワークを設計してください。
        
        記事情報:
        - タイトル: {state.article_metadata.get('title', '')}
        - ターゲットキーワード: {state.target_keywords}
        - 推定文字数: {state.article_metadata.get('word_count', 0)}
        
        以下の分析フレームワークを設計してください：
        
        1. 記事タギング戦略
           - パフォーマンス追跡用タグ
           - コンテンツ特性タグ  
           - SEO属性タグ
           - 実験変数タグ
        
        2. パフォーマンス予測
           - PV予測（1週間、1ヶ月、3ヶ月）
           - 検索順位予測
           - エンゲージメント予測
           - コンバージョン予測
        
        3. 統計分析設計
           - A/Bテスト設計
           - 因果推論アプローチ
           - 比較対照群設定
           - 交絡要因の特定
        
        4. 成功指標・KPI
           - 短期指標（1-4週間）
           - 中期指標（1-3ヶ月）
           - 長期指標（3-12ヶ月）
           - 相対指標・絶対指標
        
        出力形式:
        {{
            "article_tags": {{
                "performance_tags": ["tag1", "tag2", ...],
                "content_tags": ["content_tag1", ...],
                "seo_tags": ["seo_tag1", ...],
                "experiment_tags": ["exp_tag1", ...]
            }},
            "performance_predictions": {{
                "pv_predictions": {{
                    "week_1": 数値,
                    "month_1": 数値,
                    "month_3": 数値
                }},
                "ranking_predictions": {{
                    "main_keyword": 数値,
                    "related_keywords": {{"keyword": 予測順位}}
                }},
                "engagement_predictions": {{
                    "bounce_rate": 数値,
                    "time_on_page": 数値,
                    "social_shares": 数値
                }},
                "conversion_predictions": {{
                    "email_signups": 数値,
                    "contact_forms": 数値,
                    "sales": 数値
                }}
            }},
            "statistical_analysis": {{
                "ab_test_design": {{
                    "test_variables": ["変数1", ...],
                    "control_group": "対照群設定",
                    "sample_size": 数値,
                    "test_duration": "期間"
                }},
                "causal_inference": {{
                    "method": "手法名",
                    "control_variables": ["統制変数1", ...],
                    "confounding_factors": ["交絡要因1", ...]
                }},
                "comparison_framework": {{
                    "similar_articles": ["類似記事1", ...],
                    "benchmark_metrics": ["ベンチマーク指標1", ...],
                    "comparison_period": "比較期間"
                }}
            }},
            "success_metrics": {{
                "short_term": {{
                    "metrics": ["指標1", ...],
                    "targets": {{"指標1": 目標値}},
                    "period": "1-4 weeks"
                }},
                "medium_term": {{
                    "metrics": ["指標1", ...],
                    "targets": {{"指標1": 目標値}},
                    "period": "1-3 months"  
                }},
                "long_term": {{
                    "metrics": ["指標1", ...],
                    "targets": {{"指標1": 目標値}},
                    "period": "3-12 months"
                }}
            }}
        }}
        """
        
        try:
            response = self.llm.invoke(analysis_prompt)
            analysis_data = self._parse_json_response(response.content)
            
            state.performance_data = analysis_data
            state.current_step = WorkflowStep.IMPROVEMENT
            
            predictions = analysis_data.get("performance_predictions", {})
            month1_pv = predictions.get("pv_predictions", {}).get("month_1", 0)
            print(f"✅ 分析設計完了: 1ヶ月PV予測 {month1_pv:,}")
            return {"analysis_data": analysis_data, "step": "improvement"}
            
        except Exception as e:
            print(f"❌ 分析設計エラー: {e}")
            return {"error": str(e), "step": "analysis"}
    
    # ============================================================
    # Step 7: 改善 (Improvement)
    # ============================================================
    
    def step_7_improvement(self, state: SEOWorkflowState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Step 7: 改善段階
        - 継続的改善計画
        - 学習ループ設計
        - 次回記事への提言
        - 全体最適化戦略
        """
        print("🔄 Step 7: 改善・最適化計画策定開始")
        
        improvement_prompt = f"""
        記事作成プロセス全体を振り返り、継続的改善計画を策定してください。
        
        ワークフロー実行結果:
        - リサーチ結果: {state.research_data}
        - 企画結果: {state.planning_data}  
        - 記事品質: {state.article_metadata}
        - 分析設計: {state.performance_data}
        
        以下の改善計画を策定してください：
        
        1. プロセス改善
           - 各ステップの最適化案
           - 効率化・自動化提案
           - 品質向上施策
           - リソース最適化
        
        2. 学習ループ設計
           - パフォーマンスフィードバック活用
           - 失敗・成功パターン学習
           - A/Bテスト結果反映
           - ベストプラクティス更新
        
        3. 次回記事への提言
           - トピック選定改善
           - キーワード戦略調整
           - コンテンツ品質向上
           - プロモーション最適化
        
        4. 全体戦略最適化
           - ポートフォリオ最適化
           - リソース配分調整
           - ROI最大化戦略
           - 長期成長計画
        
        出力形式:
        {{
            "process_improvements": {{
                "research_optimization": ["改善案1", ...],
                "planning_optimization": ["改善案1", ...],
                "writing_optimization": ["改善案1", ...],
                "editing_optimization": ["改善案1", ...],
                "publishing_optimization": ["改善案1", ...],
                "analysis_optimization": ["改善案1", ...],
                "automation_opportunities": ["自動化案1", ...]
            }},
            "learning_loop": {{
                "feedback_mechanisms": ["フィードバック手法1", ...],
                "pattern_recognition": ["パターン認識手法1", ...],
                "ab_test_integration": ["A/Bテスト統合方法1", ...],
                "best_practice_updates": ["ベストプラクティス更新方法1", ...]
            }},
            "next_article_recommendations": {{
                "topic_selection": ["トピック選定改善1", ...],
                "keyword_strategy": ["キーワード戦略改善1", ...],
                "content_quality": ["コンテンツ品質改善1", ...],
                "promotion_strategy": ["プロモーション改善1", ...]
            }},
            "strategic_optimization": {{
                "portfolio_optimization": ["ポートフォリオ最適化1", ...],
                "resource_allocation": ["リソース配分最適化1", ...],
                "roi_maximization": ["ROI最大化戦略1", ...],
                "growth_strategy": ["成長戦略1", ...],
                "competitive_advantage": ["競争優位戦略1", ...]
            }},
            "implementation_plan": {{
                "priority_improvements": ["優先改善項目1", ...],
                "timeline": {{"改善項目1": "実装期間"}},
                "resources_needed": {{"改善項目1": "必要リソース"}},
                "success_metrics": {{"改善項目1": "成功指標"}}
            }}
        }}
        """
        
        try:
            response = self.llm.invoke(improvement_prompt)
            improvement_data = self._parse_json_response(response.content)
            
            state.improvement_suggestions = improvement_data.get("priority_improvements", [])
            state.updated_at = datetime.now()
            
            priority_count = len(state.improvement_suggestions)
            print(f"✅ 改善計画完了: {priority_count}個の優先改善項目")
            
            # ワークフロー完了
            return {
                "improvement_data": improvement_data,
                "workflow_complete": True,
                "final_state": state
            }
            
        except Exception as e:
            print(f"❌ 改善計画エラー: {e}")
            return {"error": str(e), "step": "improvement"}
    
    # ============================================================
    # ユーティリティメソッド
    # ============================================================
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """JSON レスポンスをパース"""
        import json
        
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
    
    def execute_full_workflow(self, topic: str) -> SEOWorkflowState:
        """完全なSEOワークフローを実行"""
        print(f"🚀 SEO記事作成ワークフロー開始: {topic}")
        print("=" * 60)
        
        # 初期状態作成
        state = SEOWorkflowState(
            current_step=WorkflowStep.RESEARCH,
            topic=topic,
            workflow_id=f"seo_{int(datetime.now().timestamp())}",
            created_at=datetime.now()
        )
        
        config = RunnableConfig()
        
        # 7ステップを順次実行
        steps = [
            ("Step 1: リサーチ", self.step_1_research),
            ("Step 2: 企画", self.step_2_planning),
            ("Step 3: 執筆", self.step_3_writing),
            ("Step 4: 修正", self.step_4_editing),
            ("Step 5: 出稿", self.step_5_publishing),
            ("Step 6: 分析", self.step_6_analysis),
            ("Step 7: 改善", self.step_7_improvement)
        ]
        
        results = {}
        
        for step_name, step_func in steps:
            print(f"\n{step_name}")
            print("-" * 40)
            
            try:
                result = step_func(state, config)
                results[step_name] = result
                
                if "error" in result:
                    print(f"❌ {step_name} でエラーが発生しました: {result['error']}")
                    break
                    
            except Exception as e:
                print(f"❌ {step_name} で予期しないエラー: {e}")
                break
        
        print("\n" + "=" * 60)
        print("🎉 SEO記事作成ワークフロー完了")
        print(f"最終ステップ: {state.current_step.value}")
        print(f"記事タイトル: {state.article_metadata.get('title', 'N/A') if state.article_metadata else 'N/A'}")
        print(f"文字数: {state.article_metadata.get('word_count', 0) if state.article_metadata else 0:,}")
        print(f"改善提案数: {len(state.improvement_suggestions) if state.improvement_suggestions else 0}")
        
        return state


# ============================================================
# LangGraphワークフロー統合
# ============================================================

def create_seo_workflow_graph(gemini_api_key: str) -> StateGraph:
    """SEO記事作成LangGraphワークフローを作成"""
    
    orchestrator = SEOWorkflowOrchestrator(gemini_api_key)
    
    def research_node(state: OverallState, config: RunnableConfig):
        topic = get_research_topic(state["messages"])
        workflow_state = SEOWorkflowState(
            current_step=WorkflowStep.RESEARCH,
            topic=topic
        )
        result = orchestrator.step_1_research(workflow_state, config)
        return {"research_result": result}
    
    def planning_node(state: OverallState, config: RunnableConfig):
        # 前ステップの結果を取得して企画実行
        # (実装詳細は省略)
        pass
    
    # グラフ構築
    builder = StateGraph(OverallState, config_schema=Configuration)
    
    # ノード追加
    builder.add_node("seo_research", research_node)
    builder.add_node("seo_planning", planning_node)
    # 他のノードも同様に追加...
    
    # エッジ追加
    builder.add_edge(START, "seo_research")
    builder.add_edge("seo_research", "seo_planning")
    # 他のエッジも同様に追加...
    
    return builder.compile(name="seo-workflow-graph")


# ============================================================
# メイン実行部分
# ============================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY が設定されていません")
        exit(1)
    
    # テスト実行
    orchestrator = SEOWorkflowOrchestrator(gemini_api_key)
    final_state = orchestrator.execute_full_workflow("誕生花")
    
    print(f"\n📋 最終結果:")
    print(f"ワークフローID: {final_state.workflow_id}")
    print(f"トピック: {final_state.topic}")
    print(f"最終ステップ: {final_state.current_step.value}")
    print(f"処理時間: {final_state.updated_at - final_state.created_at if final_state.updated_at else 'N/A'}")