#!/usr/bin/env python3
"""
誕生花に関するSEOリサーチと記事作成スクリプト
Gemini APIとGoogle Search APIを使用してキーワードリサーチ、競合分析、記事作成を実行
"""

import os
import json
import sys
import requests
from typing import List, Dict, Any
from dataclasses import dataclass
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@dataclass
class KeywordData:
    keyword: str
    search_volume: int
    competition: float
    difficulty: str
    cpc: float = 0.0

@dataclass
class CompetitorData:
    url: str
    title: str
    description: str
    word_count: int
    headings: List[str]
    domain_authority: int

class BirthFlowerSEOResearcher:
    """誕生花SEOリサーチャークラス"""
    
    def __init__(self, gemini_api_key: str, google_api_key: str = None, search_engine_id: str = None):
        self.gemini_api_key = gemini_api_key
        self.google_api_key = google_api_key
        self.search_engine_id = search_engine_id
        
        # Google Gemini API設定
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def research_keywords(self, main_keyword: str = "誕生花") -> List[KeywordData]:
        """キーワードリサーチを実行"""
        print(f"🔍 キーワードリサーチ開始: {main_keyword}")
        
        prompt = f"""
        「{main_keyword}」に関連する検索ボリュームの高いSEOキーワードを30個提案してください。
        各キーワードについて以下の情報を推定してください：
        
        1. 検索ボリューム（月間検索数の推定）
        2. 競合度（0.1-1.0の範囲）
        3. 難易度（Easy/Medium/Hard）
        
        結果をJSON形式で出力してください：
        {{
            "keywords": [
                {{
                    "keyword": "キーワード",
                    "search_volume": 1000,
                    "competition": 0.5,
                    "difficulty": "Medium"
                }}
            ]
        }}
        
        実際の検索トレンドと日本の検索行動を考慮して、現実的な数値を提供してください。
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # JSONパースを試行
            response_text = response.text
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            data = json.loads(json_text)
            
            keywords = []
            for item in data.get("keywords", []):
                keywords.append(KeywordData(
                    keyword=item["keyword"],
                    search_volume=item["search_volume"],
                    competition=item["competition"],
                    difficulty=item["difficulty"]
                ))
            
            print(f"✅ {len(keywords)}個のキーワードを発見")
            return keywords
            
        except Exception as e:
            print(f"❌ キーワードリサーチエラー: {e}")
            # フォールバック用のモックデータ
            return self._get_mock_keyword_data()
    
    def _get_mock_keyword_data(self) -> List[KeywordData]:
        """モックキーワードデータ"""
        return [
            KeywordData("誕生花", 18000, 0.7, "Medium"),
            KeywordData("誕生花 一覧", 8100, 0.6, "Easy"),
            KeywordData("誕生花 花言葉", 6600, 0.5, "Easy"),
            KeywordData("1月 誕生花", 4400, 0.4, "Easy"),
            KeywordData("2月 誕生花", 3600, 0.4, "Easy"),
            KeywordData("誕生花 意味", 2900, 0.5, "Easy"),
            KeywordData("誕生日 花", 2400, 0.6, "Medium"),
            KeywordData("月別 誕生花", 1900, 0.4, "Easy"),
            KeywordData("誕生花 プレゼント", 1600, 0.7, "Medium"),
            KeywordData("誕生花 12月", 1300, 0.3, "Easy"),
        ]
    
    def analyze_competitors(self, keyword: str = "誕生花") -> List[CompetitorData]:
        """競合サイト分析"""
        print(f"📊 競合分析開始: {keyword}")
        
        if self.google_api_key and self.search_engine_id:
            return self._google_search_competitors(keyword)
        else:
            print("⚠️ Google Search API未設定 - モックデータを使用")
            return self._get_mock_competitor_data()
    
    def _google_search_competitors(self, keyword: str) -> List[CompetitorData]:
        """Google Search APIで競合検索"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.search_engine_id,
            'q': keyword,
            'num': 10,
            'lr': 'lang_ja',
            'gl': 'jp'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json()
            
            competitors = []
            for item in results.get('items', []):
                competitors.append(CompetitorData(
                    url=item['link'],
                    title=item['title'],
                    description=item.get('snippet', ''),
                    word_count=len(item.get('snippet', '')) * 10,  # 推定
                    headings=[item['title']],
                    domain_authority=70  # 推定値
                ))
            
            print(f"✅ {len(competitors)}個の競合サイトを分析")
            return competitors
            
        except Exception as e:
            print(f"❌ Google Search API エラー: {e}")
            return self._get_mock_competitor_data()
    
    def _get_mock_competitor_data(self) -> List[CompetitorData]:
        """モック競合データ"""
        return [
            CompetitorData(
                url="https://example1.com/birth-flowers",
                title="誕生花一覧｜365日の誕生日の花と花言葉",
                description="1月から12月まで、365日すべての誕生花を花言葉とともにご紹介。プレゼント選びにも最適な誕生花の完全ガイドです。",
                word_count=3500,
                headings=["誕生花とは", "1月の誕生花", "2月の誕生花", "花言葉の意味"],
                domain_authority=75
            ),
            CompetitorData(
                url="https://example2.com/monthly-flowers",
                title="月別誕生花図鑑 - 花言葉と由来を詳しく解説",
                description="各月の代表的な誕生花について、美しい写真とともに花言葉や歴史的背景を詳しく紹介しています。",
                word_count=4200,
                headings=["月別誕生花カレンダー", "花言葉の歴史", "プレゼントガイド"],
                domain_authority=68
            ),
            CompetitorData(
                url="https://example3.com/flower-meanings",
                title="誕生花の花言葉完全ガイド｜贈り物に込める想い",
                description="誕生花の花言葉を中心に、贈り物としての意味やマナーについて専門家が詳しく解説します。",
                word_count=2800,
                headings=["花言葉とは", "贈り物のマナー", "季節別おすすめ"],
                domain_authority=72
            )
        ]
    
    def create_article_structure(self, keywords: List[KeywordData], competitors: List[CompetitorData]) -> Dict[str, Any]:
        """記事構成を作成"""
        print("📝 記事構成作成中...")
        
        # 上位キーワードを抽出
        top_keywords = [kw.keyword for kw in sorted(keywords, key=lambda x: x.search_volume, reverse=True)[:10]]
        
        # 競合の見出し分析
        competitor_headings = []
        for comp in competitors:
            competitor_headings.extend(comp.headings)
        
        prompt = f"""
        以下の情報を基に、SEO最適化された「誕生花」記事の構成を作成してください：
        
        ターゲットキーワード: {top_keywords}
        競合サイトの見出し: {competitor_headings}
        
        要件：
        1. H1タイトルは魅力的でSEO効果の高いものにする
        2. H2見出しは6-8個程度で構成する
        3. H3見出しも含めた詳細な構成にする
        4. 検索意図を満たす包括的な内容にする
        5. ユーザーが求める情報を網羅する
        
        以下のJSON形式で出力してください：
        {{
            "title": "記事タイトル（H1）",
            "meta_description": "メタディスクリプション（120-160文字）",
            "target_keywords": ["メインキーワード", "サブキーワード"],
            "structure": [
                {{
                    "h2": "大見出し",
                    "h3_items": ["小見出し1", "小見出し2"]
                }}
            ],
            "estimated_word_count": 4000,
            "seo_strategy": "SEO戦略の説明"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            structure = json.loads(json_text)
            print("✅ 記事構成作成完了")
            return structure
            
        except Exception as e:
            print(f"❌ 記事構成作成エラー: {e}")
            return self._get_mock_article_structure()
    
    def _get_mock_article_structure(self) -> Dict[str, Any]:
        """モック記事構成"""
        return {
            "title": "誕生花完全ガイド｜月別一覧と花言葉・プレゼント選びのコツ【2024年版】",
            "meta_description": "誕生花の月別一覧と花言葉を完全解説。1月から12月まで全ての誕生花をご紹介し、プレゼント選びのコツも専門家が詳しく説明します。",
            "target_keywords": ["誕生花", "誕生花 一覧", "誕生花 花言葉", "月別 誕生花"],
            "structure": [
                {
                    "h2": "誕生花とは？基本知識と歴史",
                    "h3_items": ["誕生花の定義と意味", "誕生花文化の歴史", "世界各国の誕生花文化"]
                },
                {
                    "h2": "月別誕生花一覧【1月〜12月完全版】",
                    "h3_items": ["1月〜3月の誕生花", "4月〜6月の誕生花", "7月〜9月の誕生花", "10月〜12月の誕生花"]
                },
                {
                    "h2": "誕生花の花言葉完全ガイド",
                    "h3_items": ["花言葉の由来と意味", "人気の花言葉ランキング", "贈り物に適した花言葉"]
                },
                {
                    "h2": "誕生花をプレゼントに選ぶコツ",
                    "h3_items": ["相手別プレゼント選択法", "季節を考慮した選び方", "予算別おすすめ誕生花"]
                },
                {
                    "h2": "誕生花の育て方・管理方法",
                    "h3_items": ["室内での育て方", "季節別管理のコツ", "長持ちさせる方法"]
                },
                {
                    "h2": "誕生花にまつわるよくある質問",
                    "h3_items": ["複数の誕生花がある理由", "花言葉の信憑性", "海外との違い"]
                }
            ],
            "estimated_word_count": 5000,
            "seo_strategy": "包括的な情報提供でE-A-Tを重視し、ユーザーの検索意図を完全に満たす構成"
        }
    
    def generate_full_article(self, structure: Dict[str, Any]) -> str:
        """完全な記事を生成"""
        print("✍️ 記事執筆中...")
        
        prompt = f"""
        以下の構成に基づいて、SEO最適化された詳細な「誕生花」記事を執筆してください：
        
        タイトル: {structure['title']}
        構成: {json.dumps(structure['structure'], ensure_ascii=False, indent=2)}
        
        要件：
        1. 各セクションは詳細で実用的な情報を含める
        2. 自然なキーワード配置でSEO効果を高める
        3. 読みやすい文章構成にする
        4. 専門性と信頼性を重視する
        5. 目標文字数: {structure.get('estimated_word_count', 4000)}文字程度
        6. Markdown形式で出力する
        
        誕生花の正確な情報、花言葉、歴史的背景を含めた充実した内容にしてください。
        """
        
        try:
            response = self.model.generate_content(prompt)
            article_content = response.text
            
            # Markdownのクリーンアップ
            if "```markdown" in article_content:
                start = article_content.find("```markdown") + 11
                end = article_content.find("```", start)
                if end != -1:
                    article_content = article_content[start:end].strip()
            
            print("✅ 記事執筆完了")
            return article_content
            
        except Exception as e:
            print(f"❌ 記事生成エラー: {e}")
            return self._generate_fallback_article(structure)
    
    def _generate_fallback_article(self, structure: Dict[str, Any]) -> str:
        """フォールバック記事生成"""
        return f"""# {structure['title']}

誕生花は、それぞれの月や日に対応した特別な花々で、古くから世界中で愛され続けています。この記事では、誕生花の基本知識から月別の一覧、花言葉、プレゼント選びのコツまで、誕生花に関する情報を包括的にご紹介します。

## 誕生花とは？基本知識と歴史

### 誕生花の定義と意味
誕生花とは、生まれた月や日に対応して定められた花のことです。それぞれの花には特別な意味や花言葉が込められており、その人の性格や運勢を表すとされています。

### 誕生花文化の歴史
誕生花の概念は古代ローマ時代にまで遡り、花々に神々が宿ると信じられていました。この伝統が現代まで受け継がれ、世界各地で独自の誕生花文化が発達しました。

## 月別誕生花一覧【1月〜12月完全版】

### 1月〜3月の誕生花
- **1月**: 水仙（スイセン）- 花言葉「自己愛」「神秘」
- **2月**: 梅（ウメ）- 花言葉「忠実」「独立」  
- **3月**: 桜（サクラ）- 花言葉「精神の美」「優雅な女性」

### 4月〜6月の誕生花
- **4月**: 花水木（ハナミズキ）- 花言葉「永続性」「返礼」
- **5月**: 鈴蘭（スズラン）- 花言葉「再び幸せが訪れる」「純潔」
- **6月**: 薔薇（バラ）- 花言葉「愛」「美」

### 7月〜9月の誕生花
- **7月**: 百合（ユリ）- 花言葉「純粋」「無垢」
- **8月**: 向日葵（ヒマワリ）- 花言葉「憧れ」「熱愛」
- **9月**: 桔梗（キキョウ）- 花言葉「永遠の愛」「誠実」

### 10月〜12月の誕生花
- **10月**: コスモス - 花言葉「乙女の真心」「調和」
- **11月**: 菊（キク）- 花言葉「高貴」「高尚」
- **12月**: ポインセチア - 花言葉「祝福」「幸運を祈る」

## 誕生花の花言葉完全ガイド

花言葉は、言葉では表現しきれない感情を花に込めて伝える美しい文化です。各花の花言葉を理解することで、より意味のある贈り物ができるでしょう。

## 誕生花をプレゼントに選ぶコツ

誕生花をプレゼントとして選ぶ際は、相手の好みや季節性、花言葉の意味などを総合的に考慮することが大切です。

## まとめ

誕生花は単なる装飾品ではなく、深い歴史と意味を持つ文化的な遺産です。この知識を活用して、大切な人への心のこもった贈り物を選んでみてください。
"""

def main():
    """メイン実行関数"""
    print("🌸 誕生花SEOリサーチ＆記事作成ツール 🌸")
    print("="*50)
    
    # APIキー確認
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY が設定されていません")
        return
    
    # 研究者インスタンス作成
    researcher = BirthFlowerSEOResearcher(
        gemini_api_key=gemini_api_key,
        google_api_key=google_api_key,
        search_engine_id=search_engine_id
    )
    
    # 1. キーワードリサーチ
    keywords = researcher.research_keywords("誕生花")
    
    # 2. 競合分析
    competitors = researcher.analyze_competitors("誕生花")
    
    # 3. 記事構成作成
    structure = researcher.create_article_structure(keywords, competitors)
    
    # 4. 記事生成
    article = researcher.generate_full_article(structure)
    
    # 5. 結果出力
    print("\n" + "="*50)
    print("📊 リサーチ結果サマリー")
    print("="*50)
    
    print(f"\n🔍 発見キーワード数: {len(keywords)}")
    for kw in keywords[:5]:
        print(f"  • {kw.keyword}: {kw.search_volume:,}回/月 (競合度: {kw.competition})")
    
    print(f"\n📊 分析競合サイト数: {len(competitors)}")
    for comp in competitors[:3]:
        print(f"  • {comp.title[:50]}... (DA: {comp.domain_authority})")
    
    print(f"\n📝 記事情報:")
    print(f"  • タイトル: {structure['title']}")
    print(f"  • 推定文字数: {structure['estimated_word_count']:,}文字")
    print(f"  • セクション数: {len(structure['structure'])}")
    
    # 6. MDファイル出力
    output_file = "birth_flowers_seo_article.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"<!-- SEO記事: {structure['title']} -->\n")
        f.write(f"<!-- 作成日時: {time.strftime('%Y-%m-%d %H:%M:%S')} -->\n")
        f.write(f"<!-- メタディスクリプション: {structure['meta_description']} -->\n")
        f.write(f"<!-- ターゲットキーワード: {', '.join(structure['target_keywords'])} -->\n\n")
        f.write(article)
    
    print(f"\n✅ 記事を {output_file} に保存しました")
    print("\n🎉 SEOリサーチ＆記事作成完了！")

if __name__ == "__main__":
    main()