"""Anthropic Claude API service integration."""

import asyncio
from typing import Any, Dict, List, Optional

import anthropic
from anthropic import AsyncAnthropic

from src.core.config import settings
from src.models.api_key import APIKey


class AnthropicService:
    """Service for Anthropic Claude API integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic service with API key."""
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = AsyncAnthropic(api_key=self.api_key) if self.api_key else None
    
    @property
    def default_model(self) -> str:
        """Default Claude model to use."""
        return "claude-opus-4-20250514"
    
    @property
    def available_models(self) -> List[str]:
        """List of available Claude models."""
        return [
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
        ]
    
    def configure_with_api_key(self, api_key_obj: APIKey) -> None:
        """Configure service with encrypted API key object."""
        from src.core.encryption import decrypt_api_key
        
        decrypted_key = decrypt_api_key(api_key_obj.encrypted_api_key)
        self.api_key = decrypted_key
        self.client = AsyncAnthropic(api_key=self.api_key)
    
    async def generate_text(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Claude API."""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "Anthropic client not configured"
                }
            
            model_name = model_name or self.default_model
            
            # Prepare message
            message_params = {
                "model": model_name,
                "max_tokens": max_tokens or 8192,
                "temperature": temperature or 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Add system message if provided
            if system_message:
                message_params["system"] = system_message
            
            # Generate content
            response = await self.client.messages.create(**message_params, **kwargs)
            
            return {
                "success": True,
                "content": response.content[0].text,
                "model": model_name,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name or self.default_model,
            }
    
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "seo",
        **kwargs
    ) -> Dict[str, Any]:
        """Analyze content for SEO, readability, etc."""
        
        system_messages = {
            "seo": """
            あなたはSEOとコンテンツマーケティングの専門家です。
            コンテンツを多角的に分析し、実用的で具体的な改善提案を行ってください。
            技術的な正確性と実践的な価値を重視してください。
            """,
            
            "readability": """
            あなたは文章の可読性とユーザビリティの専門家です。
            日本語の特性を考慮して、読みやすさと理解しやすさを詳細に分析してください。
            多様な読者層を想定した改善提案を行ってください。
            """,
            
            "keyword_optimization": """
            あなたはSEOキーワード戦略の専門家です。
            検索エンジンの最新アルゴリズムとユーザーの検索行動を考慮して、
            キーワード最適化の詳細な分析と提案を行ってください。
            """
        }
        
        analysis_prompts = {
            "seo": f"""
            以下のコンテンツをSEOの観点から包括的に分析し、詳細なJSON形式で回答してください：

            === コンテンツ ===
            {content}

            === 分析項目 ===
            以下のJSON構造で詳細に分析してください：

            {{
                "overall_seo_score": {{
                    "score": 0-100の数値,
                    "grade": "A+/A/B+/B/C+/C/D",
                    "summary": "総合評価の説明"
                }},
                "technical_seo": {{
                    "title_optimization": {{
                        "score": 0-100,
                        "current_length": タイトル文字数,
                        "optimal_length": "推奨文字数範囲",
                        "keyword_inclusion": "キーワード含有状況",
                        "suggestions": ["改善提案1", "改善提案2"]
                    }},
                    "meta_description": {{
                        "exists": true/false,
                        "length": 文字数,
                        "optimization_score": 0-100,
                        "suggestion": "推奨メタディスクリプション"
                    }},
                    "heading_structure": {{
                        "score": 0-100,
                        "h1_count": 数値,
                        "h2_count": 数値,
                        "h3_count": 数値,
                        "hierarchy_issues": ["問題点"],
                        "suggestions": ["改善提案"]
                    }}
                }},
                "content_quality": {{
                    "readability_score": 0-100,
                    "expertise_score": 0-100,
                    "authority_indicators": ["権威性の要素"],
                    "trustworthiness_score": 0-100,
                    "user_intent_match": 0-100,
                    "content_depth": "shallow/moderate/comprehensive",
                    "unique_value": ["独自の価値提案"]
                }},
                "keyword_analysis": {{
                    "primary_keywords": ["特定されたメインキーワード"],
                    "keyword_density": {{"キーワード": 密度パーセンテージ}},
                    "keyword_distribution": "even/front-loaded/back-loaded/uneven",
                    "lsi_keywords_present": ["発見された関連キーワード"],
                    "missing_keywords": ["追加すべきキーワード"],
                    "over_optimization_risk": 0-100
                }},
                "recommendations": {{
                    "high_priority": ["最優先の改善項目"],
                    "medium_priority": ["中優先度の改善項目"],
                    "low_priority": ["低優先度の改善項目"],
                    "content_additions": ["追加すべきコンテンツ"],
                    "structural_improvements": ["構造的改善"],
                    "estimated_impact": "改善による予想される効果"
                }}
            }}
            """,
            
            "readability": f"""
            以下のコンテンツの可読性を詳細に分析し、JSON形式で回答してください：

            === コンテンツ ===
            {content}

            === 分析項目 ===
            {{
                "overall_readability": {{
                    "score": 0-100の数値,
                    "grade": "非常に読みやすい/読みやすい/普通/やや難しい/難しい",
                    "target_audience": "想定読者層"
                }},
                "linguistic_analysis": {{
                    "average_sentence_length": 平均文字数,
                    "sentence_variation": "文の長さのバリエーション評価",
                    "vocabulary_complexity": {{
                        "difficult_words_ratio": 難しい語彙の割合,
                        "technical_terms_count": 専門用語数,
                        "jargon_usage": "専門用語の使用状況"
                    }},
                    "grammatical_complexity": "文法的複雑さの評価"
                }},
                "structure_analysis": {{
                    "paragraph_count": 段落数,
                    "average_paragraph_length": 平均段落文字数,
                    "paragraph_coherence": "段落の一貫性評価",
                    "logical_flow": "論理的な流れの評価",
                    "transition_quality": "文章のつながりの評価"
                }},
                "visual_readability": {{
                    "white_space_usage": "余白の使用状況",
                    "list_usage": "リスト構造の活用度",
                    "emphasis_usage": "強調の使用状況",
                    "scanability": "流し読みのしやすさ"
                }},
                "engagement_factors": {{
                    "opening_effectiveness": "導入部の効果",
                    "curiosity_maintenance": "興味の維持度",
                    "call_to_action_clarity": "行動喚起の明確さ",
                    "emotional_connection": "感情的な繋がり"
                }},
                "improvements": {{
                    "sentence_improvements": ["文章改善提案"],
                    "vocabulary_suggestions": ["語彙改善提案"],
                    "structure_enhancements": ["構造改善提案"],
                    "engagement_boosters": ["エンゲージメント向上提案"]
                }}
            }}
            """,
            
            "keyword_optimization": f"""
            以下のコンテンツのキーワード最適化を戦略的に分析し、JSON形式で回答してください：

            === コンテンツ ===
            {content}

            === 分析項目 ===
            {{
                "keyword_discovery": {{
                    "primary_keywords": ["特定された主要キーワード"],
                    "secondary_keywords": ["セカンダリキーワード"],
                    "long_tail_keywords": ["ロングテールキーワード"],
                    "brand_keywords": ["ブランド関連キーワード"],
                    "competitor_keywords": ["競合も狙っていそうなキーワード"]
                }},
                "keyword_metrics": {{
                    "keyword_frequency": {{"キーワード": 出現回数}},
                    "keyword_density": {{"キーワード": "密度パーセンテージ"}},
                    "keyword_prominence": {{"キーワード": "重要な位置での出現状況"}},
                    "keyword_distribution_score": 0-100
                }},
                "semantic_analysis": {{
                    "topic_clustering": ["関連トピッククラスター"],
                    "semantic_keywords": ["意味的に関連するキーワード"],
                    "entity_recognition": ["特定されたエンティティ"],
                    "context_relevance": 0-100
                }},
                "search_intent_analysis": {{
                    "informational_intent": 0-100,
                    "commercial_intent": 0-100,
                    "navigational_intent": 0-100,
                    "transactional_intent": 0-100,
                    "dominant_intent": "特定された主要検索意図"
                }},
                "optimization_opportunities": {{
                    "underused_keywords": ["活用不足のキーワード"],
                    "keyword_gaps": ["キーワードギャップ"],
                    "cannibalization_risks": ["キーワードカニバリゼーションのリスク"],
                    "expansion_opportunities": ["拡張機会"],
                    "featured_snippet_potential": ["強調スニペット獲得の可能性"]
                }},
                "strategic_recommendations": {{
                    "immediate_actions": ["即座に実行すべき施策"],
                    "content_expansion": ["コンテンツ拡張の提案"],
                    "internal_linking": ["内部リンク戦略"],
                    "cluster_development": ["トピッククラスター開発"],
                    "competitive_advantages": ["競合優位性の構築方法"]
                }}
            }}
            """
        }
        
        system_message = system_messages.get(analysis_type, system_messages["seo"])
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["seo"])
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                temperature=0.2,  # Low temperature for consistent analysis
                **kwargs
            )
            
            if result["success"]:
                # Try to parse JSON response
                import json
                try:
                    analysis_data = json.loads(result["content"])
                    result["analysis"] = analysis_data
                except json.JSONDecodeError:
                    result["analysis"] = {"raw_response": result["content"]}
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type,
            }
    
    async def generate_seo_content(
        self,
        topic: str,
        keywords: List[str],
        content_type: str = "blog_post",
        target_length: int = 2000,
        tone: str = "professional",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate SEO-optimized content with Claude's advanced reasoning."""
        
        keywords_str = "、".join(keywords)
        
        system_message = """
        あなたは経験豊富なSEOコンテンツストラテジストです。
        最新のSEOベストプラクティス、ユーザーエクスペリエンス、
        そして検索意図を深く理解したコンテンツを作成してください。
        
        E-A-T（専門性、権威性、信頼性）を重視し、
        読者に真の価値を提供するコンテンツを心がけてください。
        """
        
        prompt = f"""
        以下の詳細な条件に基づいて、戦略的にSEO最適化されたコンテンツを作成してください：

        === プロジェクト仕様 ===
        **メインテーマ:** {topic}
        **ターゲットキーワード:** {keywords_str}
        **コンテンツ形式:** {content_type}
        **目標文字数:** {target_length}文字
        **トーン:** {tone}

        === コンテンツ要件 ===
        
        **1. SEO最適化要素:**
        - メインキーワードの戦略的配置（密度1-3%）
        - 関連キーワード・LSIキーワードの自然な統合
        - 検索意図に完全に対応した内容
        - 構造化データに適した見出し階層

        **2. コンテンツ構成:**
        ```
        1. SEO最適化タイトル（32文字以内、魅力的で検索向け）
        2. メタディスクリプション（120-160文字、CTR最適化）
        3. 導入部（フック、問題提起、記事の価値提案）
        4. 主要セクション（H2使用、各セクション300-500文字）
        5. 詳細サブセクション（H3使用、具体例・データ含む）
        6. 実践的な情報（ステップ、チェックリスト、ツール等）
        7. 結論・まとめ（行動喚起含む）
        8. FAQ（最低5項目、関連キーワード含む）
        ```

        **3. 品質基準:**
        - E-A-T原則の徹底（専門性、権威性、信頼性）
        - 事実確認可能な情報・統計の使用
        - 読者の課題解決に直結する実用的価値
        - 競合差別化要素の明確化
        - ユーザーエンゲージメントを促進する要素

        **4. 技術的SEO要素:**
        - 適切なキーワード配置（タイトル、H2、導入部、結論）
        - 内部リンク機会の示唆
        - 関連トピックへの言及
        - ローカルSEO要素（該当する場合）

        **5. ユーザーエクスペリエンス:**
        - スキャン可能な構造（箇条書き、番号リスト活用）
        - 論理的で直感的な情報の流れ
        - 視覚的な区切りと強調
        - 行動喚起の戦略的配置

        === 出力形式 ===
        完成したコンテンツを、上記の構成に従って作成してください。
        各セクションを明確に区別し、SEO要素を効果的に統合してください。

        コンテンツを作成してください：
        """
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                max_tokens=target_length * 3,  # Allow for comprehensive generation
                temperature=0.7,
                **kwargs
            )
            
            if result["success"]:
                content = result["content"]
                
                # Analyze the generated content structure
                result["structured_content"] = {
                    "full_content": content,
                    "topic": topic,
                    "keywords": keywords,
                    "estimated_length": len(content),
                    "content_type": content_type,
                    "tone": tone,
                    "word_count": len(content.split()),
                    "character_count": len(content),
                }
                
                # Extract sections if possible
                sections = content.split('\n\n')
                result["structured_content"]["section_count"] = len(sections)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "keywords": keywords,
            }
    
    async def test_connection(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Test the API connection and return status."""
        try:
            test_key = api_key or self.api_key
            if not test_key:
                return {
                    "success": False,
                    "error": "API key not provided"
                }
            
            # Create temporary client for testing
            test_client = AsyncAnthropic(api_key=test_key)
            
            # Test with a simple prompt
            response = await test_client.messages.create(
                model="claude-3-5-haiku-20241022",  # Use cheaper model for testing
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, please respond with 'Connection successful' if you can read this."
                    }
                ]
            )
            
            return {
                "success": True,
                "message": "Anthropic Claude API connection successful",
                "model": "claude-3-5-haiku-20241022",
                "response": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Anthropic Claude API test failed: {str(e)}"
            }