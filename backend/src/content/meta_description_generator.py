"""
Meta Description Generator
メタディスクリプション生成機能

SEO最適化されたメタディスクリプションを生成する機能
- 160文字以下制限チェック
- キーワード含有率チェック  
- 感情訴求要素の統合
- AIサービス連携による高品質生成
"""
import asyncio
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetaDescriptionResult:
    """メタディスクリプション生成結果"""
    meta_description: str
    seo_score: float
    keyword_analysis: Dict[str, Any]
    length_analysis: Dict[str, Any]
    recommendations: List[str]


class MetaDescriptionGenerator:
    """メタディスクリプション生成器
    
    SEO最適化されたメタディスクリプションを生成するクラス
    - 文字数制限の厳密な管理
    - キーワード密度の最適化
    - 感情訴求要素の統合
    - 複数バリエーションの生成
    """
    
    def __init__(self):
        self.max_length = 160
        self.min_length = 120
        self.target_keyword_density = 0.02
        
        # 誕生花記事特有のテンプレート
        self.birth_flower_templates = {
            "informational": "{month}月の誕生花{flower}の{emotion_word}を{action_word}。{detail_element}まで、{guide_word}します。初心者にも分かりやすく豊富な写真と共にお届けします。",
            "problem_solving": "{month}月生まれの方への{flower}プレゼント選び完全ガイド。{solution_element}で失敗しない{action_word}を、実例を交えながら詳しくご紹介します。",
            "comparative": "{month}月の誕生花{flower}vs他の花の{comparison_element}。{benefit_word}な選び方を{expert_word}が、豊富な経験を基に分かりやすく解説します。",
            "emotional": "あなたの{month}月誕生花{flower}が持つ{emotion_word}とは？{special_element}で{feeling_word}を発見しませんか。心に響く花の物語をお届けします。"
        }
        
        # 感情訴求語彙
        self.emotional_words = [
            "魅力", "美しさ", "特別", "完全", "徹底", "詳しく", "おすすめ", 
            "人気", "厳選", "充実", "豊富", "素敵", "感動", "驚き"
        ]
        
        # アクション語彙
        self.action_words = [
            "解説", "紹介", "ガイド", "説明", "案内", "提案", "比較", 
            "選び方", "使い方", "楽しみ方", "活用法", "攻略法"
        ]
        
        # 誕生花特有の要素
        self.birth_flower_elements = {
            "detail_elements": ["花言葉", "由来", "歴史", "特徴", "種類", "贈り方"],
            "emotional_elements": ["意味", "想い", "気持ち", "愛情", "感謝", "祝福"],
            "practical_elements": ["プレゼント", "ギフト", "贈り物", "記念", "お祝い", "サプライズ"]
        }

    def generate_meta_description(self, article_context: Dict[str, Any]) -> str:
        """基本的なメタディスクリプション生成"""
        self._validate_input(article_context)
        
        title = article_context["title"]
        primary_keyword = article_context["primary_keyword"]
        secondary_keywords = article_context.get("secondary_keywords", [])
        content_summary = article_context.get("content_summary", "")
        
        # 基本テンプレートを使用して生成
        template_result = self._generate_from_basic_template(
            title, primary_keyword, secondary_keywords, content_summary
        )
        
        # 文字数制限内に調整
        adjusted_result = self._adjust_length(template_result)
        
        return adjusted_result

    def generate_meta_description_with_analysis(self, article_context: Dict[str, Any]) -> Dict[str, Any]:
        """分析付きメタディスクリプション生成"""
        meta_description = self.generate_meta_description(article_context)
        
        keyword_analysis = self._analyze_keywords(meta_description, article_context)
        length_analysis = self._analyze_length(meta_description)
        emotional_analysis = self._analyze_emotional_appeal(meta_description)
        
        return {
            "meta_description": meta_description,
            "keyword_analysis": keyword_analysis,
            "length_analysis": length_analysis,
            "emotional_analysis": emotional_analysis
        }

    async def generate_ai_enhanced_meta_description(self, article_context: Dict[str, Any]) -> str:
        """AI強化メタディスクリプション生成"""
        try:
            # AI生成用のプロンプトを構築
            prompt = self._build_ai_prompt(article_context)
            
            # AIサービスを呼び出し
            ai_result = await self._call_ai_service(prompt)
            
            # 結果を制限内に調整
            adjusted_result = self._adjust_length(ai_result)
            
            return adjusted_result
            
        except Exception as e:
            logger.warning(f"AI generation failed, falling back to template: {e}")
            return self.generate_meta_description(article_context)

    def generate_multiple_variations(self, article_context: Dict[str, Any], count: int = 3) -> List[str]:
        """複数バリエーション生成"""
        variations = []
        
        # 異なるテンプレートで生成
        template_types = ["informational", "problem_solving", "comparative", "emotional"]
        
        for i in range(count):
            template_type = template_types[i % len(template_types)]
            variation = self.generate_from_template(article_context, template_type)
            variations.append(variation)
        
        # ユニークなバリエーションを確保
        unique_variations = []
        for variation in variations:
            if variation not in unique_variations:
                unique_variations.append(variation)
        
        # 足りない分は微調整で生成
        while len(unique_variations) < count:
            base_variation = unique_variations[0]
            adjusted = self._create_variation(base_variation, article_context)
            if adjusted not in unique_variations:
                unique_variations.append(adjusted)
        
        return unique_variations[:count]

    def analyze_seo_optimization(self, article_context: Dict[str, Any]) -> Dict[str, Any]:
        """SEO最適化分析"""
        meta_description = self.generate_meta_description(article_context)
        
        keyword_analysis = self._analyze_keywords(meta_description, article_context)
        length_analysis = self._analyze_length(meta_description)
        emotional_analysis = self._analyze_emotional_appeal(meta_description)
        
        # SEOスコア計算
        seo_score = self._calculate_seo_score(
            keyword_analysis, length_analysis, emotional_analysis
        )
        
        # 推奨事項生成
        recommendations = self._generate_seo_recommendations(
            keyword_analysis, length_analysis, emotional_analysis
        )
        
        return {
            "seo_score": seo_score,
            "recommendations": recommendations,
            "keyword_analysis": keyword_analysis,
            "length_analysis": length_analysis,
            "emotional_analysis": emotional_analysis
        }

    def generate_from_template(self, article_context: Dict[str, Any], template_type: str) -> str:
        """テンプレートベース生成"""
        self._validate_input(article_context)
        
        if template_type not in self.birth_flower_templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        template = self.birth_flower_templates[template_type]
        
        # テンプレート変数を抽出・置換
        filled_template = self._fill_template_variables(template, article_context)
        
        # 文字数調整
        adjusted_result = self._adjust_length(filled_template)
        
        return adjusted_result

    def generate_birth_flower_optimized(self, article_context: Dict[str, Any]) -> Dict[str, Any]:
        """誕生花記事特化最適化"""
        # 誕生花特有の要素を抽出
        birth_flower_elements = self._extract_birth_flower_elements(article_context)
        
        # 特化テンプレートで生成
        optimized_description = self._generate_birth_flower_specific(
            article_context, birth_flower_elements
        )
        
        return {
            "meta_description": optimized_description,
            "birth_flower_elements": birth_flower_elements,
            "optimization_applied": [
                "誕生花特有の感情表現",
                "月指定の最適化",
                "花言葉要素の統合",
                "プレゼント文脈の強化"
            ]
        }

    def _validate_input(self, article_context: Dict[str, Any]) -> None:
        """入力バリデーション"""
        if not article_context:
            raise ValueError("Article context is required")
        
        if "title" not in article_context:
            raise ValueError("Title is required")
        
        if "primary_keyword" not in article_context:
            raise ValueError("Primary keyword is required")

    def _generate_from_basic_template(
        self, title: str, primary_keyword: str, secondary_keywords: List[str], summary: str
    ) -> str:
        """基本テンプレートから生成"""
        # キーワードを自然に統合
        integrated_keywords = self._integrate_keywords_naturally(
            primary_keyword, secondary_keywords
        )
        
        # 感情訴求語を選択
        emotion_word = self._select_emotional_word(title, summary)
        action_word = self._select_action_word(title, summary)
        
        # 基本構造を構築（キーワードは最初に1回だけ使用）
        base_structure = f"{integrated_keywords}の{emotion_word}を{action_word}。"
        
        # 詳細要素を追加（セカンダリキーワードを自然に含める）
        if summary:
            detail_element = self._extract_detail_element(summary)
            base_structure += f"{detail_element}や基本情報"
            
            # セカンダリキーワードを自然に追加（密度を考慮）
            if secondary_keywords and len(secondary_keywords) > 0:
                # 最初のセカンダリキーワードを自然に含める
                first_secondary = secondary_keywords[0]
                if "プレゼント" in summary or "ギフト" in summary:
                    base_structure += f"、{first_secondary}の贈り方"
                elif "花言葉" in summary:
                    base_structure += f"、{first_secondary}の由来"
                else:
                    base_structure += f"、{first_secondary}について"
            else:
                base_structure += "、詳細情報"
                
            base_structure += "まで、専門家が詳しく分かりやすくご紹介します。"
        else:
            base_structure += "基本情報から活用方法、選び方のコツまで専門家が詳しく解説します。"
            
        # 追加要素で文字数を調整
        if len(base_structure) < 120:
            additional_elements = [
                "初心者でも分かりやすい内容で",
                "豊富な写真と共に",
                "実用的な情報満載で",
                "最新情報を交えて"
            ]
            for element in additional_elements:
                if len(base_structure) < 120:
                    base_structure = base_structure[:-1]  # 句点を一旦削除
                    base_structure += f"、{element}お届けします。"
                else:
                    break
        
        return base_structure

    def _adjust_length(self, text: str) -> str:
        """文字数調整"""
        # 短すぎる場合は追加要素を加える
        if len(text) < self.min_length:
            additional_phrases = [
                "詳細は記事でご確認ください",
                "専門家監修の信頼できる情報です",
                "初心者にも分かりやすい内容です",
                "最新情報を交えてお届けします"
            ]
            for phrase in additional_phrases:
                if len(text) < self.min_length:
                    text = text.rstrip('。') + f"。{phrase}。"
                else:
                    break
        
        # 長すぎる場合は短縮
        if len(text) <= self.max_length:
            return text
        
        # 160文字以内に短縮
        truncated = text[:self.max_length]
        
        # 文の境界で切る
        last_period = truncated.rfind('。')
        if last_period > self.min_length:
            return truncated[:last_period + 1]
        
        # 句読点で切る
        last_comma = truncated.rfind('、')
        if last_comma > self.min_length:
            return truncated[:last_comma] + '。'
        
        # 最後の手段：文字数で切って「...」を追加
        return truncated[:self.max_length - 3] + '...'

    def _analyze_keywords(self, meta_description: str, article_context: Dict[str, Any]) -> Dict[str, Any]:
        """キーワード分析"""
        primary_keyword = article_context["primary_keyword"]
        secondary_keywords = article_context.get("secondary_keywords", [])
        
        # キーワード出現回数をカウント
        primary_count = meta_description.count(primary_keyword)
        secondary_counts = {kw: meta_description.count(kw) for kw in secondary_keywords}
        
        # 総キーワード出現数
        total_keyword_chars = len(primary_keyword) * primary_count
        for kw, count in secondary_counts.items():
            total_keyword_chars += len(kw) * count
        
        # キーワード密度計算
        density = total_keyword_chars / len(meta_description) if len(meta_description) > 0 else 0
        
        # 含まれているキーワード
        included_keywords = [primary_keyword] if primary_count > 0 else []
        included_keywords.extend([kw for kw, count in secondary_counts.items() if count > 0])
        
        return {
            "density": density,
            "primary_keyword_count": primary_count,
            "secondary_keyword_counts": secondary_counts,
            "included_keywords": included_keywords,
            "total_keywords": len(included_keywords)
        }

    def _analyze_length(self, meta_description: str) -> Dict[str, Any]:
        """長さ分析"""
        length = len(meta_description)
        
        return {
            "character_count": length,
            "within_limit": length <= self.max_length,
            "above_minimum": length >= self.min_length,
            "optimal_range": self.min_length <= length <= self.max_length,
            "utilization_rate": length / self.max_length
        }

    def _analyze_emotional_appeal(self, meta_description: str) -> Dict[str, Any]:
        """感情訴求分析"""
        found_emotional_words = [word for word in self.emotional_words if word in meta_description]
        found_action_words = [word for word in self.action_words if word in meta_description]
        
        # 感情スコア計算
        emotion_score = len(found_emotional_words) * 20 + len(found_action_words) * 15
        emotion_score = min(emotion_score, 100)
        
        return {
            "emotional_words_found": found_emotional_words,
            "action_words_found": found_action_words,
            "emotion_score": emotion_score,
            "has_emotional_appeal": len(found_emotional_words) > 0,
            "has_action_appeal": len(found_action_words) > 0
        }

    def _calculate_seo_score(
        self, keyword_analysis: Dict[str, Any], 
        length_analysis: Dict[str, Any], 
        emotional_analysis: Dict[str, Any]
    ) -> float:
        """SEOスコア計算"""
        score = 0
        
        # 長さスコア (30点満点)
        if length_analysis["optimal_range"]:
            score += 30
        elif length_analysis["within_limit"]:
            score += 20
        elif length_analysis["above_minimum"]:
            score += 15
        
        # キーワードスコア (40点満点)
        if keyword_analysis["primary_keyword_count"] > 0:
            score += 20
        
        density = keyword_analysis["density"]
        if 0.01 <= density <= 0.05:
            score += 20
        elif 0.005 <= density <= 0.08:
            score += 10
        
        # 感情訴求スコア (30点満点)
        emotion_score = emotional_analysis["emotion_score"]
        score += min(emotion_score * 0.3, 30)
        
        return min(score, 100)

    def _generate_seo_recommendations(
        self, keyword_analysis: Dict[str, Any], 
        length_analysis: Dict[str, Any], 
        emotional_analysis: Dict[str, Any]
    ) -> List[str]:
        """SEO推奨事項生成"""
        recommendations = []
        
        # 長さ関連
        if not length_analysis["within_limit"]:
            recommendations.append("メタディスクリプションが160文字を超過しています。短縮してください。")
        elif not length_analysis["above_minimum"]:
            recommendations.append("メタディスクリプションが短すぎます。120文字以上にしてください。")
        
        # キーワード関連
        if keyword_analysis["primary_keyword_count"] == 0:
            recommendations.append("プライマリキーワードが含まれていません。追加してください。")
        
        density = keyword_analysis["density"]
        if density < 0.01:
            recommendations.append("キーワード密度が低すぎます。関連キーワードを追加してください。")
        elif density > 0.05:
            recommendations.append("キーワード密度が高すぎます。自然な文章に調整してください。")
        
        # 感情訴求関連
        if not emotional_analysis["has_emotional_appeal"]:
            recommendations.append("感情に訴える表現を追加してユーザーの関心を引きましょう。")
        
        if not emotional_analysis["has_action_appeal"]:
            recommendations.append("行動を促す表現を追加してクリック率を向上させましょう。")
        
        return recommendations

    def _integrate_keywords_naturally(self, primary_keyword: str, secondary_keywords: List[str]) -> str:
        """キーワードの自然な統合"""
        # プライマリキーワードのみを使用（密度を抑えるため）
        # セカンダリキーワードは文章の中で自然に使用する
        return primary_keyword

    def _select_emotional_word(self, title: str, summary: str) -> str:
        """感情訴求語選択"""
        text = f"{title} {summary}".lower()
        
        # 文脈に適した感情語を選択
        if any(word in text for word in ["解説", "説明", "紹介"]):
            return "魅力"
        elif any(word in text for word in ["選び方", "比較", "ガイド"]):
            return "完全"
        elif any(word in text for word in ["プレゼント", "ギフト"]):
            return "特別"
        else:
            return "美しさ"

    def _select_action_word(self, title: str, summary: str) -> str:
        """アクション語選択"""
        text = f"{title} {summary}".lower()
        
        if any(word in text for word in ["解説", "説明"]):
            return "解説"
        elif any(word in text for word in ["紹介", "案内"]):
            return "紹介"
        elif any(word in text for word in ["ガイド", "選び方"]):
            return "ガイド"
        elif any(word in text for word in ["比較", "検討"]):
            return "比較"
        else:
            return "解説"

    def _extract_detail_element(self, summary: str) -> str:
        """詳細要素抽出"""
        detail_patterns = {
            "花言葉": ["花言葉", "意味"],
            "プレゼント": ["プレゼント", "ギフト", "贈り物"],
            "種類": ["種類", "品種", "バリエーション"],
            "由来": ["由来", "歴史", "起源"],
            "特徴": ["特徴", "魅力", "ポイント"]
        }
        
        for element, patterns in detail_patterns.items():
            if any(pattern in summary for pattern in patterns):
                return element
        
        return "基本情報"

    def _fill_template_variables(self, template: str, article_context: Dict[str, Any]) -> str:
        """テンプレート変数埋め込み"""
        # 月の抽出
        title = article_context["title"]
        month_match = re.search(r'(\d+)月', title)
        month = month_match.group(1) if month_match else "誕生"
        
        # 花の名前抽出
        flower_names = ["チューリップ", "バラ", "カーネーション", "スズラン", "ユリ", "ヒマワリ"]
        flower = "誕生花"
        for flower_name in flower_names:
            if flower_name in title:
                flower = flower_name
                break
        
        # コンテンツサマリーから詳細要素を抽出
        summary = article_context.get("content_summary", "")
        detail_element = self._extract_detail_element(summary)
        
        # 変数置換
        filled = template.format(
            month=month,
            flower=flower,
            emotion_word=self._select_emotional_word(title, summary),
            action_word=self._select_action_word(title, summary),
            detail_element=f"{detail_element}・由来・歴史",
            guide_word="詳しくご紹介",
            solution_element="失敗しない選び方とポイント",
            comparison_element="魅力と特徴の詳細比較",
            benefit_word="最適で素敵",
            expert_word="花の専門家",
            special_element="特別な意味と深い想い",
            feeling_word="新しい発見と感動"
        )
        
        # 文字数が不足している場合は追加要素を加える
        if len(filled) < 120:
            additional_phrases = [
                "初心者にも分かりやすく",
                "豊富な写真付きで",
                "最新情報を交えて",
                "実用的なアドバイスと共に"
            ]
            for phrase in additional_phrases:
                if len(filled) < 120:
                    filled = filled.rstrip('。') + f"、{phrase}お届けします。"
                else:
                    break
        
        return filled

    def _extract_birth_flower_elements(self, article_context: Dict[str, Any]) -> Dict[str, List[str]]:
        """誕生花特有要素抽出"""
        title = article_context["title"]
        summary = article_context.get("content_summary", "")
        text = f"{title} {summary}".lower()
        
        extracted = {
            "detail_elements": [],
            "emotional_elements": [],
            "practical_elements": []
        }
        
        for category, elements in self.birth_flower_elements.items():
            for element in elements:
                if element in text:
                    extracted[category].append(element)
        
        return extracted

    def _generate_birth_flower_specific(
        self, article_context: Dict[str, Any], elements: Dict[str, List[str]]
    ) -> str:
        """誕生花特化生成"""
        title = article_context["title"]
        primary_keyword = article_context["primary_keyword"]
        
        # 月と花を抽出
        month_match = re.search(r'(\d+)月', title)
        month = month_match.group(1) if month_match else "誕生"
        
        flower_names = ["チューリップ", "バラ", "カーネーション", "スズラン", "ユリ", "ヒマワリ"]
        flower = "誕生花"
        for flower_name in flower_names:
            if flower_name in title:
                flower = flower_name
                break
        
        # 要素に基づいて構造を構築
        if elements["detail_elements"]:
            detail = elements["detail_elements"][0]
            base = f"{month}月の誕生花{flower}の美しい{detail}を徹底解説。"
        else:
            base = f"{month}月の誕生花{flower}の特別な魅力を徹底解説。"
        
        if elements["practical_elements"]:
            practical = elements["practical_elements"][0]
            base += f"{practical}選びに役立つ詳細情報や選び方のポイント"
        else:
            base += "基本情報から歴史、育て方のコツ"
        
        if elements["emotional_elements"]:
            emotional = elements["emotional_elements"][0]
            base += f"、{emotional}に込められた深い意味"
        else:
            base += "、花言葉に込められた想い"
            
        # 追加要素で文字数を確保
        additional_info = [
            "季節の楽しみ方",
            "人気の品種紹介",
            "贈り方のマナー",
            "アレンジメントのアイデア"
        ]
        
        for info in additional_info:
            if len(base) < 100:
                base += f"、{info}"
        
        base += "まで、専門家が豊富な写真と共に分かりやすくご紹介します。"
        
        return self._adjust_length(base)

    def _create_variation(self, base_text: str, article_context: Dict[str, Any]) -> str:
        """バリエーション作成"""
        # 感情語やアクション語を変更してバリエーションを作成
        variations_map = {
            "魅力": "美しさ",
            "徹底": "詳しく",
            "解説": "紹介",
            "ご紹介": "ガイド",
            "詳しく": "完全に"
        }
        
        varied_text = base_text
        for original, replacement in variations_map.items():
            if original in varied_text:
                varied_text = varied_text.replace(original, replacement, 1)
                break
        
        return self._adjust_length(varied_text)

    async def _call_ai_service(self, prompt: str) -> str:
        """AIサービス呼び出し（モック実装）"""
        # 実際の実装では、Gemini/OpenAI/Anthropic APIを呼び出す
        # ここではテスト用の固定レスポンスを返す
        return "3月の誕生花チューリップの美しい花言葉と魅力を徹底解説。プレゼント選びに役立つ詳細情報とおすすめの贈り方まで、専門家が丁寧に紹介します。"

    def _build_ai_prompt(self, article_context: Dict[str, Any]) -> str:
        """AI用プロンプト構築"""
        title = article_context["title"]
        primary_keyword = article_context["primary_keyword"]
        secondary_keywords = article_context.get("secondary_keywords", [])
        
        prompt = f"""
        以下の記事のメタディスクリプションを生成してください：

        タイトル: {title}
        メインキーワード: {primary_keyword}
        サブキーワード: {', '.join(secondary_keywords)}

        要件:
        - 160文字以内
        - キーワードを自然に含める
        - 感情に訴える表現を使用
        - 行動を促す要素を含める
        - 誕生花記事として魅力的に
        """
        
        return prompt