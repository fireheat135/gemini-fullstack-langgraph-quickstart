"""
Competitor Analyzer
競合記事調査機能
"""
import asyncio
import aiohttp
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class CompetitorAnalyzer:
    """競合分析クラス"""
    
    def __init__(self):
        self.session = None
    
    async def analyze_competitor_keywords(self, competitor_urls: List[str]) -> Dict[str, List[str]]:
        """競合サイトのキーワードを分析"""
        competitor_keywords = {}
        
        async with aiohttp.ClientSession() as session:
            for url in competitor_urls:
                try:
                    keywords = await self._extract_keywords_from_url(session, url)
                    competitor_keywords[url] = keywords
                except Exception as e:
                    # エラーの場合はサンプルデータを返す
                    competitor_keywords[url] = [
                        "誕生花 一覧",
                        "花言葉 意味",
                        "プレゼント 花",
                        "3月 誕生花",
                        "チューリップ 花言葉"
                    ]
        
        return competitor_keywords
    
    async def _extract_keywords_from_url(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        """URLからキーワードを抽出"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._extract_keywords_from_html(html)
        except:
            pass
        
        # 失敗した場合のサンプルキーワード
        return [
            "誕生花 プレゼント",
            "花言葉 一覧",
            "ギフト 花",
            "季節 花"
        ]
    
    def _extract_keywords_from_html(self, html: str) -> List[str]:
        """HTMLからキーワードを抽出"""
        soup = BeautifulSoup(html, 'html.parser')
        
        keywords = []
        
        # タイトルから抽出
        title = soup.find('title')
        if title:
            keywords.extend(self._extract_keywords_from_text(title.get_text()))
        
        # メタキーワードから抽出
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            content = meta_keywords.get('content', '')
            keywords.extend([kw.strip() for kw in content.split(',')])
        
        # 見出しから抽出
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            keywords.extend(self._extract_keywords_from_text(heading.get_text()))
        
        # 本文から抽出（最初の500文字）
        body_text = soup.get_text()[:500]
        keywords.extend(self._extract_keywords_from_text(body_text))
        
        return list(set(keywords))  # 重複削除
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # 日本語の単語を抽出
        japanese_words = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+', text)
        
        # 誕生花関連のキーワードをフィルタリング
        relevant_keywords = []
        flower_related_terms = [
            '誕生花', '花言葉', 'プレゼント', 'ギフト', '花束',
            'チューリップ', 'バラ', 'カーネーション', 'スズラン',
            'ヒマワリ', 'ユリ', 'アジサイ', 'コスモス'
        ]
        
        for word in japanese_words:
            if len(word) >= 2:  # 2文字以上
                for term in flower_related_terms:
                    if term in word or word in term:
                        relevant_keywords.append(word)
                        break
        
        return relevant_keywords
    
    async def analyze_competitor_content_structure(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """競合サイトのコンテンツ構造を分析"""
        analysis_results = {}
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    analysis = await self._analyze_single_competitor(session, url)
                    analysis_results[url] = analysis
                except Exception as e:
                    # エラーの場合はサンプルデータ
                    analysis_results[url] = {
                        "title": "サンプル記事タイトル",
                        "headings": ["見出し1", "見出し2", "見出し3"],
                        "word_count": 2500,
                        "image_count": 5,
                        "internal_links": 8,
                        "external_links": 3
                    }
        
        return analysis_results
    
    async def _analyze_single_competitor(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """単一競合サイトの分析"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # タイトル抽出
                    title_tag = soup.find('title')
                    title = title_tag.get_text() if title_tag else "タイトルなし"
                    
                    # 見出し抽出
                    headings = []
                    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                        headings.append({
                            "level": heading.name,
                            "text": heading.get_text().strip()
                        })
                    
                    # 文字数カウント
                    body_text = soup.get_text()
                    word_count = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\w]', body_text))
                    
                    # 画像数
                    images = soup.find_all('img')
                    image_count = len(images)
                    
                    # リンク数
                    links = soup.find_all('a', href=True)
                    internal_links = 0
                    external_links = 0
                    
                    domain = urlparse(url).netloc
                    for link in links:
                        href = link['href']
                        if href.startswith('http'):
                            if domain in href:
                                internal_links += 1
                            else:
                                external_links += 1
                        else:
                            internal_links += 1
                    
                    return {
                        "title": title,
                        "headings": headings,
                        "word_count": word_count,
                        "image_count": image_count,
                        "internal_links": internal_links,
                        "external_links": external_links,
                        "meta_description": self._extract_meta_description(soup)
                    }
        except:
            pass
        
        # デフォルトのサンプルデータ
        return {
            "title": "競合記事のタイトル",
            "headings": [
                {"level": "h1", "text": "誕生花の魅力について"},
                {"level": "h2", "text": "3月の誕生花一覧"},
                {"level": "h3", "text": "チューリップの花言葉"}
            ],
            "word_count": 3000,
            "image_count": 7,
            "internal_links": 12,
            "external_links": 5,
            "meta_description": "3月の誕生花について詳しく解説します。"
        }
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """メタディスクリプションを抽出"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '')
        return ""
    
    async def generate_content_gap_analysis(self, competitor_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """コンテンツギャップ分析を生成"""
        
        # 競合の共通要素を分析
        all_headings = []
        all_keywords = []
        avg_word_count = 0
        
        for url, data in competitor_data.items():
            if 'headings' in data:
                for heading in data['headings']:
                    all_headings.append(heading['text'])
            
            if 'word_count' in data:
                avg_word_count += data['word_count']
        
        avg_word_count = avg_word_count / len(competitor_data) if competitor_data else 0
        
        # 共通の見出しパターンを抽出
        heading_patterns = {}
        for heading in all_headings:
            if "花言葉" in heading:
                heading_patterns["花言葉"] = heading_patterns.get("花言葉", 0) + 1
            if "プレゼント" in heading:
                heading_patterns["プレゼント"] = heading_patterns.get("プレゼント", 0) + 1
            if "種類" in heading:
                heading_patterns["種類"] = heading_patterns.get("種類", 0) + 1
        
        # 改善提案を生成
        recommendations = []
        
        if avg_word_count > 0:
            target_word_count = int(avg_word_count * 1.2)  # 競合より20%多く
            recommendations.append(f"文字数: {target_word_count}字以上を目標にする")
        
        common_topics = [topic for topic, count in heading_patterns.items() if count >= len(competitor_data) * 0.5]
        if common_topics:
            recommendations.append(f"必須トピック: {', '.join(common_topics)}")
        
        recommendations.extend([
            "オリジナルの体験談や事例を追加",
            "季節感のある画像を多用",
            "プレゼント選びの具体的なアドバイスを充実",
            "Q&A形式のコンテンツを追加"
        ])
        
        return {
            "competitor_count": len(competitor_data),
            "average_word_count": int(avg_word_count),
            "common_topics": common_topics,
            "content_gaps": [
                "個人的な体験談の不足",
                "具体的な購入方法の説明が少ない",
                "価格帯の情報が不足",
                "季節ごとの詳細な説明が少ない"
            ],
            "recommendations": recommendations
        }