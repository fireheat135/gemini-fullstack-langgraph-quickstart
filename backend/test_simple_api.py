#!/usr/bin/env python3
"""Simple test API for content generation without external dependencies."""

import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

app = FastAPI(title="Simple Content Generation API", version="1.0.0")

class ArticleRequest(BaseModel):
    topic: str
    keywords: Optional[List[str]] = []
    content_type: str = "article"
    target_length: int = 2000

class ArticleResponse(BaseModel):
    title: str
    content: str
    meta_description: str
    seo_score: int
    word_count: int

@app.get("/")
def read_root():
    return {"message": "SEO Agent Platform API is running!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "seo-agent-platform"}

@app.post("/generate-article", response_model=ArticleResponse)
def generate_article(request: ArticleRequest):
    """Generate a simple article about the given topic."""
    
    # Mock article generation for testing
    if "誕生花" in request.topic or "birth flower" in request.topic.lower():
        title = f"{request.topic}の完全ガイド - 月ごとの花言葉と歴史"
        content = f"""# {request.topic}の完全ガイド

## はじめに

{request.topic}は、それぞれの月に対応した美しい花々で、古くから人々に愛され続けています。各月の誕生花には特別な花言葉があり、その歴史的背景も興味深いものがあります。

## 月別誕生花一覧

### 1月 - 水仙（スイセン）
**花言葉**: 「自己愛」「神秘」
**歴史**: 古代ギリシャ神話のナルキッソスの物語に由来します。

### 2月 - 梅（ウメ）
**花言葉**: 「忠実」「独立」
**歴史**: 中国から伝来し、日本文化に深く根ざした花です。

### 3月 - 桜（サクラ）
**花言葉**: 「精神の美」「優雅な女性」
**歴史**: 日本の国花として親しまれ、春の象徴です。

### 4月 - 花水木（ハナミズキ）
**花言葉**: 「永続性」「返礼」
**歴史**: アメリカから贈られた友好の証として知られています。

### 5月 - 鈴蘭（スズラン）
**花言葉**: 「再び幸せが訪れる」「純潔」
**歴史**: ヨーロッパでは5月1日に愛する人に贈る習慣があります。

### 6月 - 薔薇（バラ）
**花言葉**: 「愛」「美」
**歴史**: 古代から愛と美の象徴として崇められてきました。

### 7月 - 百合（ユリ）
**花言葉**: 「純粋」「無垢」
**歴史**: キリスト教では聖母マリアの象徴とされています。

### 8月 - 向日葵（ヒマワリ）
**花言葉**: 「憧れ」「熱愛」
**歴史**: 太陽を追いかける特性から、忠誠心の象徴とされました。

### 9月 - 桔梗（キキョウ）
**花言葉**: 「永遠の愛」「誠実」
**歴史**: 万葉集にも詠まれた、日本古来の美しい花です。

### 10月 - コスモス
**花言葉**: 「乙女の真心」「調和」
**歴史**: メキシコ原産で、日本には明治時代に伝来しました。

### 11月 - 菊（キク）
**花言葉**: 「高貴」「高尚」
**歴史**: 皇室の紋章としても使われ、日本文化の重要な花です。

### 12月 - 水仙（スイセン）・ポインセチア
**花言葉**: 「神秘」「祝福」
**歴史**: クリスマスシーズンを彩る代表的な花として親しまれています。

## 誕生花の歴史的背景

誕生花の概念は、古代ローマ時代にまで遡ります。ローマ人は花や植物に神々が宿ると信じ、各月に特定の花を対応させていました。この伝統が現代まで受け継がれ、世界各地で独自の誕生花文化が発達しました。

日本においては、平安時代から花を愛でる文化が発達し、季節の花々が和歌や文学作品に頻繁に登場するようになりました。江戸時代には園芸文化が庶民にも広がり、現在の誕生花の基礎が形成されました。

## 誕生花の楽しみ方

1. **ギフトとして**: 大切な人の誕生月の花を贈る
2. **インテリアとして**: 季節感を演出する装飾に活用
3. **ガーデニング**: 庭やベランダで育てて楽しむ
4. **写真撮影**: 美しい花々を記録に残す

## まとめ

{request.topic}は、単なる装飾用の花ではなく、深い歴史と意味を持つ文化的な遺産です。それぞれの花が持つ特別な意味を理解することで、日常生活により豊かな彩りを添えることができるでしょう。

月ごとの誕生花を知ることで、季節の移ろいをより深く感じ、大切な人への贈り物選びにも役立てることができます。
"""
        
        meta_description = f"{request.topic}について詳しく解説。月ごとの花言葉、歴史的背景、楽しみ方を紹介します。"
        word_count = len(content)
        seo_score = 85
        
    else:
        # Generic article generation
        title = f"{request.topic}について - 詳細ガイド"
        content = f"""# {request.topic}について

## 概要

{request.topic}について詳しく説明します。

## 詳細情報

{request.topic}に関する重要なポイントをご紹介します。

## まとめ

{request.topic}について理解を深めることができました。
"""
        meta_description = f"{request.topic}について詳しく解説します。"
        word_count = len(content)
        seo_score = 75

    return ArticleResponse(
        title=title,
        content=content,
        meta_description=meta_description,
        seo_score=seo_score,
        word_count=word_count
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)