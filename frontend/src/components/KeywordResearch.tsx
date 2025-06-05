import React, { useState, useCallback } from 'react'
import { Search, TrendingUp, Target, Brain, Zap, Filter, Download, Star } from 'lucide-react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

interface KeywordData {
  id: string
  keyword: string
  searchVolume: number
  difficulty: number
  cpc: number
  trend: 'up' | 'down' | 'stable'
  intent: 'informational' | 'commercial' | 'navigational' | 'transactional'
  relatedKeywords: string[]
}

interface KeywordResearchProps {
  onKeywordSelect?: (keyword: KeywordData) => void
}

const mockKeywords: KeywordData[] = [
  {
    id: '1',
    keyword: 'SEO ツール',
    searchVolume: 8900,
    difficulty: 65,
    cpc: 320,
    trend: 'up',
    intent: 'commercial',
    relatedKeywords: ['SEO 分析', 'SEO チェック', 'SEO 対策']
  },
  {
    id: '2',
    keyword: 'コンテンツマーケティング',
    searchVolume: 5600,
    difficulty: 45,
    cpc: 280,
    trend: 'stable',
    intent: 'informational',
    relatedKeywords: ['コンテンツ戦略', 'ブログマーケティング']
  },
  {
    id: '3',
    keyword: 'キーワード調査',
    searchVolume: 3400,
    difficulty: 38,
    cpc: 195,
    trend: 'up',
    intent: 'informational',
    relatedKeywords: ['キーワード分析', 'SEO キーワード']
  }
]

export function KeywordResearch({ onKeywordSelect }: KeywordResearchProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [keywords, setKeywords] = useState<KeywordData[]>(mockKeywords)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedTab, setSelectedTab] = useState('search')

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return
    
    setIsAnalyzing(true)
    
    // Simulate API call
    setTimeout(() => {
      const newKeywords = [...mockKeywords]
      setKeywords(newKeywords)
      setIsAnalyzing(false)
    }, 2000)
  }, [searchQuery])

  const getDifficultyColor = (difficulty: number) => {
    if (difficulty < 30) return 'text-green-400'
    if (difficulty < 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getDifficultyLabel = (difficulty: number) => {
    if (difficulty < 30) return 'Easy'
    if (difficulty < 60) return 'Medium'
    return 'Hard'
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-400" />
      case 'down':
        return <TrendingUp className="h-4 w-4 text-red-400 rotate-180" />
      default:
        return <div className="h-4 w-4 rounded-full bg-gray-400" />
    }
  }

  const getIntentBadge = (intent: string) => {
    const colors = {
      informational: 'bg-blue-500/20 text-blue-300',
      commercial: 'bg-green-500/20 text-green-300',
      navigational: 'bg-purple-500/20 text-purple-300',
      transactional: 'bg-orange-500/20 text-orange-300'
    }
    
    return (
      <Badge className={`${colors[intent as keyof typeof colors]} border-none`}>
        {intent}
      </Badge>
    )
  }

  return (
    <div className="h-full flex flex-col space-y-6 p-6 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Target className="h-6 w-6 text-primary" />
          キーワードリサーチ
          <Badge className="ml-2 bg-primary/20 text-primary border-primary/50">
            AI Powered
          </Badge>
        </h1>
        <p className="text-muted-foreground">
          AIを活用してSEOに最適なキーワードを発見し、競合分析を実行します
        </p>
      </div>

      {/* Search Input */}
      <Card className="glass-effect p-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="シードキーワードを入力..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-background/50 border-border/50"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button 
            onClick={handleSearch}
            disabled={isAnalyzing || !searchQuery.trim()}
            variant="glow"
            className="relative"
          >
            {isAnalyzing ? (
              <>
                <Brain className="h-4 w-4 animate-pulse" />
                分析中...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                AI分析開始
              </>
            )}
          </Button>
        </div>
      </Card>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Tabs value={selectedTab} onValueChange={setSelectedTab} className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-4 glass-effect">
            <TabsTrigger value="search" className="data-[state=active]:bg-primary/20">
              検索結果
            </TabsTrigger>
            <TabsTrigger value="trends" className="data-[state=active]:bg-primary/20">
              トレンド
            </TabsTrigger>
            <TabsTrigger value="competition" className="data-[state=active]:bg-primary/20">
              競合分析
            </TabsTrigger>
            <TabsTrigger value="suggestions" className="data-[state=active]:bg-primary/20">
              AI提案
            </TabsTrigger>
          </TabsList>

          <TabsContent value="search" className="flex-1 mt-6 space-y-4 overflow-auto">
            {/* Filters and Actions */}
            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4" />
                  フィルター
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4" />
                  エクスポート
                </Button>
              </div>
              <div className="text-sm text-muted-foreground">
                {keywords.length} keywords found
              </div>
            </div>

            {/* Keywords List */}
            <div className="space-y-3">
              {keywords.map((keyword) => (
                <Card 
                  key={keyword.id}
                  className="p-4 hover:shadow-lg transition-all duration-200 cursor-pointer glass-effect hover:bg-accent/5"
                  onClick={() => onKeywordSelect?.(keyword)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-foreground">{keyword.keyword}</h3>
                        {getTrendIcon(keyword.trend)}
                        {getIntentBadge(keyword.intent)}
                        <Button variant="ghost" size="icon" className="h-6 w-6">
                          <Star className="h-3 w-3" />
                        </Button>
                      </div>
                      
                      <div className="flex items-center gap-6 text-sm">
                        <div className="flex items-center gap-1">
                          <span className="text-muted-foreground">検索ボリューム:</span>
                          <span className="font-medium text-primary">
                            {keyword.searchVolume.toLocaleString()}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-1">
                          <span className="text-muted-foreground">難易度:</span>
                          <span className={`font-medium ${getDifficultyColor(keyword.difficulty)}`}>
                            {keyword.difficulty}/100
                          </span>
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${getDifficultyColor(keyword.difficulty)} border-current`}
                          >
                            {getDifficultyLabel(keyword.difficulty)}
                          </Badge>
                        </div>
                        
                        <div className="flex items-center gap-1">
                          <span className="text-muted-foreground">CPC:</span>
                          <span className="font-medium text-green-400">
                            ¥{keyword.cpc}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-1">
                        {keyword.relatedKeywords.slice(0, 3).map((related, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {related}
                          </Badge>
                        ))}
                        {keyword.relatedKeywords.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{keyword.relatedKeywords.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="trends" className="flex-1 mt-6">
            <Card className="h-full glass-effect p-6">
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground" />
                  <h3 className="text-lg font-semibold">トレンド分析</h3>
                  <p className="text-muted-foreground">
                    キーワードのトレンドデータを分析中...
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="competition" className="flex-1 mt-6">
            <Card className="h-full glass-effect p-6">
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <Target className="h-12 w-12 mx-auto text-muted-foreground" />
                  <h3 className="text-lg font-semibold">競合分析</h3>
                  <p className="text-muted-foreground">
                    競合サイトの分析データを準備中...
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="suggestions" className="flex-1 mt-6">
            <Card className="h-full glass-effect p-6">
              <div className="flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <Brain className="h-12 w-12 mx-auto text-muted-foreground" />
                  <h3 className="text-lg font-semibold">AI キーワード提案</h3>
                  <p className="text-muted-foreground">
                    AIがあなたのコンテンツに最適なキーワードを提案します
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}