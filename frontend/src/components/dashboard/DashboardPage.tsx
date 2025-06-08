import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  BarChart3, 
  FileText, 
  Search, 
  TrendingUp, 
  Users,
  ArrowUpRight,
  Calendar,
  Clock
} from 'lucide-react'
import { apiClient } from '@/lib/api.ts'

interface DashboardStats {
  totalKeywords: number
  totalArticles: number
  totalTraffic: number
  activeProjects: number
  keywordGrowth: number
  articleGrowth: number
  trafficGrowth: number
}

interface RecentActivity {
  id: string
  type: 'keyword' | 'article' | 'seo-research'
  title: string
  timestamp: string
  status: 'completed' | 'pending' | 'failed'
}

export function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalKeywords: 0,
    totalArticles: 0,
    totalTraffic: 0,
    activeProjects: 0,
    keywordGrowth: 0,
    articleGrowth: 0,
    trafficGrowth: 0,
  })
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // 実際のAPIエンドポイントに置き換える予定
        // const { data } = await apiClient.get('/api/v1/analytics/summary')
        
        // モックデータ（実装時に削除）
        setStats({
          totalKeywords: 1247,
          totalArticles: 89,
          totalTraffic: 15642,
          activeProjects: 5,
          keywordGrowth: 12.5,
          articleGrowth: 8.3,
          trafficGrowth: 23.1,
        })

        setRecentActivity([
          {
            id: '1',
            type: 'keyword',
            title: '「AI ライティング」のキーワード分析が完了',
            timestamp: '5分前',
            status: 'completed'
          },
          {
            id: '2',
            type: 'article',
            title: 'SEO記事「効果的なコンテンツマーケティング」を公開',
            timestamp: '1時間前',
            status: 'completed'
          },
          {
            id: '3',
            type: 'seo-research',
            title: '競合分析レポートを生成中',
            timestamp: '2時間前',
            status: 'pending'
          }
        ])
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const statCards = [
    {
      title: 'トータルキーワード',
      value: stats.totalKeywords.toLocaleString(),
      change: `+${stats.keywordGrowth}%`,
      icon: Search,
      trend: 'up' as const
    },
    {
      title: '公開記事数',
      value: stats.totalArticles.toLocaleString(),
      change: `+${stats.articleGrowth}%`,
      icon: FileText,
      trend: 'up' as const
    },
    {
      title: '月間トラフィック',
      value: stats.totalTraffic.toLocaleString(),
      change: `+${stats.trafficGrowth}%`,
      icon: TrendingUp,
      trend: 'up' as const
    },
    {
      title: 'アクティブプロジェクト',
      value: stats.activeProjects.toString(),
      change: '+2',
      icon: Users,
      trend: 'up' as const
    }
  ]

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">ダッシュボード</h1>
          <p className="text-muted-foreground">
            SEOプラットフォームの概要と最新の活動を確認できます
          </p>
        </div>
        <Button>
          <ArrowUpRight className="mr-2 h-4 w-4" />
          レポート生成
        </Button>
      </div>

      {/* 統計カード */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <Card key={card.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {card.title}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{card.value}</div>
                <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                  <Badge variant="secondary" className="text-green-600">
                    {card.change}
                  </Badge>
                  <span>前月比</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">概要</TabsTrigger>
          <TabsTrigger value="activity">最近の活動</TabsTrigger>
          <TabsTrigger value="performance">パフォーマンス</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>クイックアクション</CardTitle>
                <CardDescription>
                  よく使用される機能への素早いアクセス
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <Search className="mr-2 h-4 w-4" />
                  新しいキーワード研究
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <FileText className="mr-2 h-4 w-4" />
                  記事を作成
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  分析レポート
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>今日の予定</CardTitle>
                <CardDescription>
                  スケジュールされたタスクと活動
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">記事レビュー</p>
                    <p className="text-xs text-muted-foreground">14:00</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">SEO分析レポート</p>
                    <p className="text-xs text-muted-foreground">16:30</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>最近の活動</CardTitle>
              <CardDescription>
                システム内の最新の活動とステータス
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-4 rounded-lg border p-4">
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.title}</p>
                      <p className="text-xs text-muted-foreground">{activity.timestamp}</p>
                    </div>
                    <Badge variant={
                      activity.status === 'completed' ? 'default' : 
                      activity.status === 'pending' ? 'secondary' : 'destructive'
                    }>
                      {activity.status === 'completed' ? '完了' :
                       activity.status === 'pending' ? '処理中' : '失敗'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>パフォーマンス概要</CardTitle>
              <CardDescription>
                キーワードランキングとトラフィックの推移
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                チャート実装予定 (Chart.js または Recharts)
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}