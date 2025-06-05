import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface KeywordData {
  keyword: string;
  searchVolume: number;
  competition: number;
  difficulty: string;
}

interface CompetitorData {
  url: string;
  title: string;
  wordCount: number;
  domainAuthority: number;
}

export function SEODashboard() {
  const [keywords, setKeywords] = useState<KeywordData[]>([]);
  const [competitors, setCompetitors] = useState<CompetitorData[]>([]);
  const [seedKeyword, setSeedKeyword] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleKeywordResearch = async () => {
    if (!seedKeyword.trim()) return;
    
    setIsAnalyzing(true);
    try {
      // TODO: Integrate with SEO research API
      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock data
      const mockKeywords: KeywordData[] = [
        { keyword: `${seedKeyword} ガイド`, searchVolume: 1200, competition: 0.6, difficulty: 'Medium' },
        { keyword: `${seedKeyword} 方法`, searchVolume: 800, competition: 0.4, difficulty: 'Easy' },
        { keyword: `${seedKeyword} おすすめ`, searchVolume: 1500, competition: 0.8, difficulty: 'Hard' },
        { keyword: `${seedKeyword} 比較`, searchVolume: 600, competition: 0.3, difficulty: 'Easy' },
        { keyword: `${seedKeyword} 初心者`, searchVolume: 400, competition: 0.2, difficulty: 'Easy' },
      ];
      
      setKeywords(mockKeywords);
    } catch (error) {
      console.error('Error during keyword research:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCompetitorAnalysis = async () => {
    if (!seedKeyword.trim()) return;
    
    setIsAnalyzing(true);
    try {
      // TODO: Integrate with competitor analysis API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock data
      const mockCompetitors: CompetitorData[] = [
        {
          url: 'https://example1.com/article',
          title: `${seedKeyword}の完全ガイド`,
          wordCount: 3500,
          domainAuthority: 65
        },
        {
          url: 'https://example2.com/guide',
          title: `初心者向け${seedKeyword}講座`,
          wordCount: 2800,
          domainAuthority: 72
        },
        {
          url: 'https://example3.com/tutorial',
          title: `${seedKeyword}を学ぶための10のステップ`,
          wordCount: 4200,
          domainAuthority: 58
        },
      ];
      
      setCompetitors(mockCompetitors);
    } catch (error) {
      console.error('Error during competitor analysis:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-green-400';
      case 'medium':
        return 'text-yellow-400';
      case 'hard':
        return 'text-red-400';
      default:
        return 'text-neutral-400';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">SEOダッシュボード</h1>
        <p className="text-neutral-400">キーワードリサーチと競合分析を実行</p>
      </div>

      {/* Search Input */}
      <Card className="p-6 mb-6 bg-neutral-800 border-neutral-700">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-white mb-2">
              シードキーワード
            </label>
            <Input
              value={seedKeyword}
              onChange={(e) => setSeedKeyword(e.target.value)}
              placeholder="例: SEO最適化"
              className="bg-neutral-700 border-neutral-600 text-white"
            />
          </div>
          <div className="flex gap-2">
            <Button
              onClick={handleKeywordResearch}
              disabled={isAnalyzing || !seedKeyword.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isAnalyzing ? ' 分析中...' : 'キーワード分析'}
            </Button>
            <Button
              onClick={handleCompetitorAnalysis}
              disabled={isAnalyzing || !seedKeyword.trim()}
              variant="outline"
              className="border-neutral-600 text-white hover:bg-neutral-700"
            >
              競合分析
            </Button>
          </div>
        </div>
      </Card>

      {/* Results Tabs */}
      <Tabs defaultValue="keywords" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-neutral-800 border-neutral-700">
          <TabsTrigger value="keywords" className="data-[state=active]:bg-blue-600">
            キーワード ({keywords.length})
          </TabsTrigger>
          <TabsTrigger value="competitors" className="data-[state=active]:bg-blue-600">
            競合分析 ({competitors.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="keywords" className="mt-6">
          {keywords.length > 0 ? (
            <Card className="bg-neutral-800 border-neutral-700">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4">キーワード分析結果</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-neutral-700">
                        <th className="text-left py-2 text-white">キーワード</th>
                        <th className="text-left py-2 text-white">月間検索数</th>
                        <th className="text-left py-2 text-white">競合性</th>
                        <th className="text-left py-2 text-white">難易度</th>
                      </tr>
                    </thead>
                    <tbody>
                      {keywords.map((keyword, index) => (
                        <tr key={index} className="border-b border-neutral-700/50">
                          <td className="py-3 text-white">{keyword.keyword}</td>
                          <td className="py-3 text-neutral-300">
                            {keyword.searchVolume.toLocaleString()}
                          </td>
                          <td className="py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-neutral-700 rounded-full h-2">
                                <div
                                  className="bg-blue-500 h-2 rounded-full"
                                  style={{ width: `${keyword.competition * 100}%` }}
                                />
                              </div>
                              <span className="text-sm text-neutral-400">
                                {Math.round(keyword.competition * 100)}%
                              </span>
                            </div>
                          </td>
                          <td className="py-3">
                            <span className={`font-medium ${getDifficultyColor(keyword.difficulty)}`}>
                              {keyword.difficulty}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </Card>
          ) : (
            <Card className="p-8 text-center bg-neutral-800 border-neutral-700">
              <div className="text-neutral-400">
                <div className="text-4xl mb-2">🔍</div>
                <h3 className="text-lg font-medium text-white mb-2">キーワード分析を開始</h3>
                <p>シードキーワードを入力して分析を実行してください</p>
              </div>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="competitors" className="mt-6">
          {competitors.length > 0 ? (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white">競合分析結果</h3>
              {competitors.map((competitor, index) => (
                <Card key={index} className="p-6 bg-neutral-800 border-neutral-700">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-white mb-1">{competitor.title}</h4>
                      <a
                        href={competitor.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-sm"
                      >
                        {competitor.url}
                      </a>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-neutral-400">文字数: </span>
                      <span className="text-white">{competitor.wordCount.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-neutral-400">ドメインオーソリティ: </span>
                      <span className="text-white">{competitor.domainAuthority}</span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center bg-neutral-800 border-neutral-700">
              <div className="text-neutral-400">
                <div className="text-4xl mb-2">📊</div>
                <h3 className="text-lg font-medium text-white mb-2">競合分析を開始</h3>
                <p>シードキーワードを入力して競合サイトを分析してください</p>
              </div>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}