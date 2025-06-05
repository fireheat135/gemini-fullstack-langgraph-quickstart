import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

interface ContentRequest {
  topic: string;
  keywords: string[];
  contentType: string;
  targetLength: number;
  tone: string;
  targetAudience: string;
}

interface GeneratedContent {
  title: string;
  metaDescription: string;
  content: string;
  seoScore: number;
  readabilityScore: number;
  suggestions: string[];
}

export function ContentGenerator() {
  const [request, setRequest] = useState<ContentRequest>({
    topic: '',
    keywords: [],
    contentType: 'blog_post',
    targetLength: 2000,
    tone: 'professional',
    targetAudience: '一般的な読者'
  });
  
  const [keywordInput, setKeywordInput] = useState('');
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<'form' | 'preview' | 'analysis'>('form');

  const handleAddKeyword = () => {
    if (keywordInput.trim() && !request.keywords.includes(keywordInput.trim())) {
      setRequest(prev => ({
        ...prev,
        keywords: [...prev.keywords, keywordInput.trim()]
      }));
      setKeywordInput('');
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setRequest(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keyword)
    }));
  };

  const handleGenerate = async () => {
    if (!request.topic.trim()) return;

    setIsGenerating(true);
    try {
      // TODO: Integrate with content generation API
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Mock generated content
      const mockContent: GeneratedContent = {
        title: `${request.topic}の完全ガイド - 2024年最新版`,
        metaDescription: `${request.topic}について知っておくべきすべてを解説。${request.keywords.slice(0, 2).join('、')}などの重要ポイントを詳しく説明します。`,
        content: `# ${request.topic}の完全ガイド

## はじめに

${request.topic}は現代において非常に重要なトピックです。この記事では、${request.keywords.join('、')}について詳しく解説し、実践的な知識を提供します。

## ${request.topic}とは

${request.topic}は...（ここに詳細な説明が続きます）

### 主要なポイント

1. **基本概念の理解**
   - ${request.keywords[0] || 'キーワード'}の重要性
   - 基礎となる知識の習得

2. **実践的なアプローチ**
   - 具体的な手順
   - ベストプラクティス

3. **応用と展開**
   - 発展的な活用方法
   - 将来的な展望

## 実装方法

### ステップ1: 準備段階
（詳細な手順）

### ステップ2: 実行段階
（具体的な実装方法）

### ステップ3: 最適化
（改善のポイント）

## まとめ

${request.topic}について理解を深めることで、より効果的な成果を得ることができます。${request.keywords.join('、')}を活用して、継続的な改善を図りましょう。`,
        seoScore: 87,
        readabilityScore: 72,
        suggestions: [
          'H2見出しにターゲットキーワードを追加してください',
          'メタディスクリプションを150文字以内に調整してください',
          '内部リンクを3-5個追加することをお勧めします',
          '画像のalt属性にキーワードを含めてください'
        ]
      };

      setGeneratedContent(mockContent);
      setActiveTab('preview');
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">AIコンテンツ生成</h1>
        <p className="text-neutral-400">SEO最適化されたコンテンツを自動生成</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-neutral-800 p-1 rounded-lg w-fit">
        {[
          { id: 'form', label: '設定' },
          { id: 'preview', label: 'プレビュー' },
          { id: 'analysis', label: '分析' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-md transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-neutral-300 hover:text-white hover:bg-neutral-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content based on active tab */}
      {activeTab === 'form' && (
        <Card className="p-6 bg-neutral-800 border-neutral-700">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                トピック *
              </label>
              <Input
                value={request.topic}
                onChange={(e) => setRequest(prev => ({ ...prev, topic: e.target.value }))}
                placeholder="例: React Hooks の使い方"
                className="bg-neutral-700 border-neutral-600 text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-2">
                ターゲットキーワード
              </label>
              <div className="flex gap-2 mb-2">
                <Input
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  placeholder="キーワードを入力"
                  className="bg-neutral-700 border-neutral-600 text-white"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
                />
                <Button onClick={handleAddKeyword} variant="outline" className="border-neutral-600">
                  追加
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {request.keywords.map((keyword) => (
                  <Badge
                    key={keyword}
                    variant="secondary"
                    className="bg-blue-600 text-white cursor-pointer"
                    onClick={() => handleRemoveKeyword(keyword)}
                  >
                    {keyword} ×
                  </Badge>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  コンテンツタイプ
                </label>
                <Select value={request.contentType} onValueChange={(value) => 
                  setRequest(prev => ({ ...prev, contentType: value }))
                }>
                  <SelectTrigger className="bg-neutral-700 border-neutral-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="blog_post">ブログ記事</SelectItem>
                    <SelectItem value="landing_page">ランディングページ</SelectItem>
                    <SelectItem value="product_description">商品説明</SelectItem>
                    <SelectItem value="guide">ガイド記事</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  文字数目標
                </label>
                <Select value={request.targetLength.toString()} onValueChange={(value) => 
                  setRequest(prev => ({ ...prev, targetLength: parseInt(value) }))
                }>
                  <SelectTrigger className="bg-neutral-700 border-neutral-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1000">1,000文字</SelectItem>
                    <SelectItem value="2000">2,000文字</SelectItem>
                    <SelectItem value="3000">3,000文字</SelectItem>
                    <SelectItem value="5000">5,000文字</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  トーン
                </label>
                <Select value={request.tone} onValueChange={(value) => 
                  setRequest(prev => ({ ...prev, tone: value }))
                }>
                  <SelectTrigger className="bg-neutral-700 border-neutral-600 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="professional">専門的</SelectItem>
                    <SelectItem value="casual">カジュアル</SelectItem>
                    <SelectItem value="friendly">親しみやすい</SelectItem>
                    <SelectItem value="formal">フォーマル</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  ターゲット読者
                </label>
                <Input
                  value={request.targetAudience}
                  onChange={(e) => setRequest(prev => ({ ...prev, targetAudience: e.target.value }))}
                  placeholder="例: 初心者の開発者"
                  className="bg-neutral-700 border-neutral-600 text-white"
                />
              </div>
            </div>

            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !request.topic.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700"
              size="lg"
            >
              {isGenerating ? '生成中...' : 'コンテンツを生成'}
            </Button>
          </div>
        </Card>
      )}

      {activeTab === 'preview' && (
        <div className="space-y-6">
          {generatedContent ? (
            <>
              <Card className="p-6 bg-neutral-800 border-neutral-700">
                <h3 className="text-lg font-semibold text-white mb-4">メタデータ</h3>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-neutral-400 mb-1">
                      タイトル
                    </label>
                    <div className="text-white">{generatedContent.title}</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-neutral-400 mb-1">
                      メタディスクリプション
                    </label>
                    <div className="text-neutral-300">{generatedContent.metaDescription}</div>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-neutral-800 border-neutral-700">
                <h3 className="text-lg font-semibold text-white mb-4">コンテンツ</h3>
                <div className="prose prose-invert max-w-none">
                  <pre className="whitespace-pre-wrap text-neutral-300 leading-relaxed">
                    {generatedContent.content}
                  </pre>
                </div>
              </Card>
            </>
          ) : (
            <Card className="p-8 text-center bg-neutral-800 border-neutral-700">
              <div className="text-neutral-400">
                <div className="text-4xl mb-2">✍️</div>
                <h3 className="text-lg font-medium text-white mb-2">コンテンツが生成されていません</h3>
                <p>設定タブでコンテンツを生成してください</p>
              </div>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'analysis' && (
        <div className="space-y-6">
          {generatedContent ? (
            <>
              <Card className="p-6 bg-neutral-800 border-neutral-700">
                <h3 className="text-lg font-semibold text-white mb-4">SEOスコア</h3>
                <div className="grid grid-cols-2 gap-6">
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(generatedContent.seoScore)}`}>
                      {generatedContent.seoScore}
                    </div>
                    <div className="text-sm text-neutral-400">SEOスコア</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(generatedContent.readabilityScore)}`}>
                      {generatedContent.readabilityScore}
                    </div>
                    <div className="text-sm text-neutral-400">可読性スコア</div>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-neutral-800 border-neutral-700">
                <h3 className="text-lg font-semibold text-white mb-4">改善提案</h3>
                <ul className="space-y-2">
                  {generatedContent.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-yellow-400 mt-0.5">💡</span>
                      <span className="text-neutral-300">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </>
          ) : (
            <Card className="p-8 text-center bg-neutral-800 border-neutral-700">
              <div className="text-neutral-400">
                <div className="text-4xl mb-2">📊</div>
                <h3 className="text-lg font-medium text-white mb-2">分析結果がありません</h3>
                <p>コンテンツを生成してから分析してください</p>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}