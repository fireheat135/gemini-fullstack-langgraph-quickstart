import { ReactNode, useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Search, 
  Plus, 
  TrendingUp, 
  FileText, 
  BarChart3, 
  Settings, 
  Home,
  Sparkles,
  Target,
  Users,
  Calendar,
  BookOpen,
  Zap,
  Filter,
  ArrowUpRight,
  Clock,
  Star
} from 'lucide-react'
import { apiClient } from '@/lib/api.ts'

interface NotionLayoutProps {
  children?: ReactNode
}

type ViewType = 'dashboard' | 'keywords' | 'content' | 'analytics' | 'seo-research' | 'settings'

interface KeywordData {
  keyword: string
  search_volume: number
  difficulty: number
  cpc: number
  trend: 'up' | 'down' | 'stable'
}

interface ArticleData {
  id: string
  title: string
  status: string
  created_at: string
  word_count: number
  performance_score?: number
}

export function NotionLayout({ children }: NotionLayoutProps) {
  const [activeView, setActiveView] = useState<ViewType>('dashboard')
  const [searchQuery, setSearchQuery] = useState('')
  const [keywords, setKeywords] = useState<KeywordData[]>([])
  const [articles, setArticles] = useState<ArticleData[]>([])
  const [loading, setLoading] = useState(false)
  const [analytics, setAnalytics] = useState<any>(null)

  // Load initial data
  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [analyticsData, articlesData] = await Promise.all([
        apiClient.getAnalyticsSummary().catch(() => null),
        apiClient.getArticles(1, 10).catch(() => ({ items: [] }))
      ])
      
      setAnalytics(analyticsData)
      setArticles((articlesData as any)?.items || [])
    } catch (error) {
      console.error('ダッシュボードデータの読み込みに失敗:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleKeywordAnalysis = async (keyword: string) => {
    if (!keyword.trim()) return
    
    try {
      setLoading(true)
      const result = await apiClient.analyzeKeyword(keyword) as any
      
      const newKeyword: KeywordData = {
        keyword,
        search_volume: result?.search_volume || 0,
        difficulty: result?.difficulty || 0,
        cpc: result?.cpc || 0,
        trend: result?.trend || 'stable'
      }
      
      setKeywords(prev => [newKeyword, ...prev.slice(0, 9)])
      setSearchQuery('')
    } catch (error) {
      console.error('キーワード分析エラー:', error)
    } finally {
      setLoading(false)
    }
  }

  const sidebarItems = [
    { id: 'dashboard', label: 'ホーム', icon: Home },
    { id: 'keywords', label: 'キーワード研究', icon: Target },
    { id: 'content', label: 'コンテンツ管理', icon: FileText },
    { id: 'seo-research', label: 'SEO分析', icon: TrendingUp },
    { id: 'analytics', label: 'アナリティクス', icon: BarChart3 },
    { id: 'settings', label: '設定', icon: Settings },
  ]

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">おはようございます🌅</h1>
          <p className="text-gray-600 mt-1">今日も素晴らしいコンテンツを作りましょう</p>
        </div>
        <Button className="bg-purple-600 hover:bg-purple-700">
          <Plus className="h-4 w-4 mr-2" />
          新しいプロジェクト
        </Button>
      </div>

      {/* Quick search */}
      <Card className="border-0 shadow-sm bg-gradient-to-r from-purple-50 to-blue-50">
        <CardContent className="p-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="キーワードを入力して分析を開始..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleKeywordAnalysis(searchQuery)}
                className="text-lg border-0 shadow-none bg-white/70"
              />
            </div>
            <Button 
              onClick={() => handleKeywordAnalysis(searchQuery)}
              disabled={loading || !searchQuery.trim()}
              className="px-8 bg-purple-600 hover:bg-purple-700"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <><Search className="h-4 w-4 mr-2" /> 分析</>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">総記事数</p>
                <p className="text-2xl font-bold text-gray-900">{articles.length}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowUpRight className="h-3 w-3 mr-1" />
                  +12% 先月比
                </p>
              </div>
              <div className="p-3 bg-blue-100 rounded-xl">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">分析キーワード</p>
                <p className="text-2xl font-bold text-gray-900">{keywords.length}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowUpRight className="h-3 w-3 mr-1" />
                  +{keywords.length} 今日
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-xl">
                <Target className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">月間PV</p>
                <p className="text-2xl font-bold text-gray-900">{analytics?.total_views || '---'}</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <TrendingUp className="h-3 w-3 mr-1" />
                  +8.4% 先月比
                </p>
              </div>
              <div className="p-3 bg-green-100 rounded-xl">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">コンバージョン率</p>
                <p className="text-2xl font-bold text-gray-900">{analytics?.conversion_rate || '---'}%</p>
                <p className="text-xs text-green-600 flex items-center mt-1">
                  <ArrowUpRight className="h-3 w-3 mr-1" />
                  +2.1% 先月比
                </p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-xl">
                <Zap className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent content and keywords */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent keywords */}
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center">
              <Target className="h-5 w-5 mr-2 text-purple-600" />
              最近のキーワード分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              {keywords.length === 0 ? (
                <div className="flex items-center justify-center h-32 text-gray-500">
                  <div className="text-center">
                    <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>キーワードを分析してみましょう</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {keywords.map((keyword, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{keyword.keyword}</span>
                          <Badge variant={keyword.trend === 'up' ? 'default' : keyword.trend === 'down' ? 'destructive' : 'secondary'} className="text-xs">
                            {keyword.trend === 'up' ? '上昇' : keyword.trend === 'down' ? '下降' : '安定'}
                          </Badge>
                        </div>
                        <div className="flex gap-4 text-sm text-gray-600">
                          <span>検索ボリューム: {keyword.search_volume.toLocaleString()}</span>
                          <span>難易度: {keyword.difficulty}/100</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Recent articles */}
        <Card className="border-0 shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center">
              <FileText className="h-5 w-5 mr-2 text-blue-600" />
              最近の記事
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64">
              {articles.length === 0 ? (
                <div className="flex items-center justify-center h-32 text-gray-500">
                  <div className="text-center">
                    <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>まだ記事がありません</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {articles.slice(0, 5).map((article) => (
                    <div key={article.id} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium truncate flex-1 mr-2">{article.title}</h4>
                        <Badge variant="outline" className="text-xs">
                          {article.status === 'published' ? '公開中' : 
                           article.status === 'draft' ? '下書き' : '編集中'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {new Date(article.created_at).toLocaleDateString('ja-JP')}
                        </span>
                        <span>{article.word_count} 文字</span>
                        {article.performance_score && (
                          <span className="flex items-center">
                            <Star className="h-3 w-3 mr-1" />
                            {article.performance_score}/100
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderKeywords = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">キーワード研究</h1>
        <Button className="bg-purple-600 hover:bg-purple-700">
          <Plus className="h-4 w-4 mr-2" />
          一括インポート
        </Button>
      </div>
      
      <Card className="border-0 shadow-sm">
        <CardContent className="p-6">
          <div className="flex gap-4 mb-6">
            <Input
              placeholder="キーワードを入力..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
            <Button onClick={() => handleKeywordAnalysis(searchQuery)} disabled={loading}>
              {loading ? '分析中...' : '分析開始'}
            </Button>
          </div>
          
          {keywords.length > 0 && (
            <div className="space-y-4">
              {keywords.map((keyword, idx) => (
                <div key={idx} className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-lg">{keyword.keyword}</h3>
                    <Badge variant={keyword.trend === 'up' ? 'default' : 'secondary'}>
                      {keyword.trend === 'up' ? '上昇トレンド' : '安定'}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">検索ボリューム</span>
                      <p className="font-semibold">{keyword.search_volume.toLocaleString()}/月</p>
                    </div>
                    <div>
                      <span className="text-gray-600">難易度</span>
                      <p className="font-semibold">{keyword.difficulty}/100</p>
                    </div>
                    <div>
                      <span className="text-gray-600">CPC</span>
                      <p className="font-semibold">¥{keyword.cpc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )

  const renderContent = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">コンテンツ管理</h1>
        <Button className="bg-purple-600 hover:bg-purple-700">
          <Plus className="h-4 w-4 mr-2" />
          新しい記事
        </Button>
      </div>
      
      <div className="grid gap-4">
        {articles.map((article) => (
          <Card key={article.id} className="border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">{article.title}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>{new Date(article.created_at).toLocaleDateString('ja-JP')}</span>
                    <span>{article.word_count} 文字</span>
                    <Badge variant="outline">
                      {article.status === 'published' ? '公開中' : 
                       article.status === 'draft' ? '下書き' : '編集中'}
                    </Badge>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">編集</Button>
                  <Button variant="outline" size="sm">統計</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderActiveContent = () => {
    switch (activeView) {
      case 'dashboard':
        return renderDashboard()
      case 'keywords':
        return renderKeywords()
      case 'content':
        return renderContent()
      case 'seo-research':
        return <div className="p-8 text-center text-gray-500">SEO分析機能は準備中です</div>
      case 'analytics':
        return <div className="p-8 text-center text-gray-500">アナリティクス機能は準備中です</div>
      case 'settings':
        return <div className="p-8 text-center text-gray-500">設定機能は準備中です</div>
      default:
        return renderDashboard()
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-gray-900">Scrib AI</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {sidebarItems.map((item) => {
              const Icon = item.icon
              const isActive = activeView === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id as ViewType)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    isActive
                      ? 'bg-purple-100 text-purple-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </button>
              )
            })}
          </div>
        </nav>

        {/* User info */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <Users className="h-4 w-4 text-gray-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">ユーザー名</p>
              <p className="text-xs text-gray-500 truncate">user@example.com</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {sidebarItems.find(item => item.id === activeView)?.label}
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                フィルター
              </Button>
              <Button variant="outline" size="sm">
                <Calendar className="h-4 w-4 mr-2" />
                期間選択
              </Button>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto p-6">
          {renderActiveContent()}
        </main>
      </div>
    </div>
  )
}
