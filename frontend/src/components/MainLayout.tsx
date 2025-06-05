import React, { useState } from 'react'
import { 
  Home, 
  Search, 
  CheckSquare, 
  PenTool, 
  BarChart3, 
  Settings, 
  Brain,
  Zap,
  Target,
  User,
  Bell,
  Moon,
  Sun,
  Menu,
  X
} from 'lucide-react'
import { Button } from './ui/button'
import { 
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenuItem,
  SidebarMenuIcon,
  SidebarMenuBadge
} from './ui/sidebar'
import { Badge } from './ui/badge'
import { KeywordResearch } from './KeywordResearch'
import { TaskManager } from './TaskManager'

interface MainLayoutProps {
  children?: React.ReactNode
}

const navigationItems = [
  {
    id: 'dashboard',
    label: 'ダッシュボード',
    icon: Home,
    component: null
  },
  {
    id: 'keywords',
    label: 'キーワードリサーチ',
    icon: Target,
    component: KeywordResearch,
    badge: 'AI'
  },
  {
    id: 'tasks',
    label: 'タスク管理',
    icon: CheckSquare,
    component: TaskManager,
    badge: '12'
  },
  {
    id: 'content',
    label: 'コンテンツ生成',
    icon: PenTool,
    component: null,
    badge: 'NEW'
  },
  {
    id: 'analytics',
    label: '分析レポート',
    icon: BarChart3,
    component: null
  }
]

export function MainLayout({ children }: MainLayoutProps) {
  const [activeItem, setActiveItem] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [isDarkMode, setIsDarkMode] = useState(true)

  const renderContent = () => {
    const item = navigationItems.find(item => item.id === activeItem)
    if (item?.component) {
      const Component = item.component
      return <Component />
    }
    
    if (activeItem === 'dashboard') {
      return (
        <div className="h-full flex flex-col space-y-6 p-6 animate-fade-in">
          <div className="space-y-2">
            <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
              <div className="relative">
                <Brain className="h-8 w-8 text-primary" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
              </div>
              SEO Agent Dashboard
              <Badge className="bg-gradient-to-r from-primary to-accent text-primary-foreground border-none">
                Powered by AI
              </Badge>
            </h1>
            <p className="text-muted-foreground text-lg">
              AIが支援する最高のライティングツールへようこそ
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-effect p-6 rounded-lg border border-border/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">総キーワード数</p>
                  <p className="text-2xl font-bold text-primary">1,247</p>
                </div>
                <Target className="h-8 w-8 text-primary/60" />
              </div>
              <div className="mt-2 flex items-center gap-1 text-sm">
                <span className="text-green-400">+12%</span>
                <span className="text-muted-foreground">from last month</span>
              </div>
            </div>

            <div className="glass-effect p-6 rounded-lg border border-border/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">アクティブタスク</p>
                  <p className="text-2xl font-bold text-blue-400">23</p>
                </div>
                <CheckSquare className="h-8 w-8 text-blue-400/60" />
              </div>
              <div className="mt-2 flex items-center gap-1 text-sm">
                <span className="text-yellow-400">5 urgent</span>
                <span className="text-muted-foreground">need attention</span>
              </div>
            </div>

            <div className="glass-effect p-6 rounded-lg border border-border/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">生成記事数</p>
                  <p className="text-2xl font-bold text-green-400">89</p>
                </div>
                <PenTool className="h-8 w-8 text-green-400/60" />
              </div>
              <div className="mt-2 flex items-center gap-1 text-sm">
                <span className="text-green-400">+8 this week</span>
                <span className="text-muted-foreground">auto-generated</span>
              </div>
            </div>

            <div className="glass-effect p-6 rounded-lg border border-border/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">SEOスコア</p>
                  <p className="text-2xl font-bold text-purple-400">92/100</p>
                </div>
                <BarChart3 className="h-8 w-8 text-purple-400/60" />
              </div>
              <div className="mt-2 flex items-center gap-1 text-sm">
                <span className="text-green-400">Excellent</span>
                <span className="text-muted-foreground">performance</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground">クイックアクション</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Button
                variant="outline"
                className="h-24 flex-col gap-2 glass-effect hover:bg-primary/10"
                onClick={() => setActiveItem('keywords')}
              >
                <Target className="h-6 w-6" />
                <span>キーワードリサーチ</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-24 flex-col gap-2 glass-effect hover:bg-blue-500/10"
                onClick={() => setActiveItem('content')}
              >
                <Zap className="h-6 w-6" />
                <span>AIライティング</span>
              </Button>
              
              <Button
                variant="outline"
                className="h-24 flex-col gap-2 glass-effect hover:bg-green-500/10"
                onClick={() => setActiveItem('tasks')}
              >
                <CheckSquare className="h-6 w-6" />
                <span>タスク作成</span>
              </Button>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-foreground">最近のアクティビティ</h2>
            <div className="space-y-3">
              {[
                { action: 'キーワード「AIライティング」を分析', time: '2分前', type: 'research' },
                { action: '記事「SEO最適化ガイド」を生成完了', time: '15分前', type: 'content' },
                { action: 'タスク「競合分析」を完了', time: '1時間前', type: 'task' },
                { action: 'レポート「月次パフォーマンス」を作成', time: '3時間前', type: 'analytics' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center gap-3 p-3 rounded-lg glass-effect">
                  <div className="w-2 h-2 bg-primary rounded-full" />
                  <span className="flex-1 text-sm text-foreground">{activity.action}</span>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )
    }
    
    return children
  }

  return (
    <div className={`h-screen flex ${isDarkMode ? 'dark' : ''}`}>
      {/* Sidebar */}
      <Sidebar 
        variant="default" 
        className={`transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-16'}`}
      >
        <SidebarHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative">
                <Brain className="h-8 w-8 text-primary" />
                <div className="absolute -top-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full" />
              </div>
              {sidebarOpen && (
                <div>
                  <h1 className="font-bold text-lg text-foreground">SEO Agent</h1>
                  <p className="text-xs text-muted-foreground">AI Writing Platform</p>
                </div>
              )}
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="h-8 w-8"
            >
              {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </SidebarHeader>

        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupContent>
              {navigationItems.map((item) => (
                <SidebarMenuItem
                  key={item.id}
                  variant={activeItem === item.id ? 'active' : 'default'}
                  onClick={() => setActiveItem(item.id)}
                  className="cursor-pointer"
                >
                  <SidebarMenuIcon>
                    <item.icon />
                  </SidebarMenuIcon>
                  {sidebarOpen && (
                    <>
                      <span>{item.label}</span>
                      {item.badge && (
                        <SidebarMenuBadge>
                          {item.badge}
                        </SidebarMenuBadge>
                      )}
                    </>
                  )}
                </SidebarMenuItem>
              ))}
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <div className="space-y-2">
            <SidebarMenuItem>
              <SidebarMenuIcon>
                <Settings />
              </SidebarMenuIcon>
              {sidebarOpen && <span>設定</span>}
            </SidebarMenuItem>
            
            <div className="flex items-center justify-between">
              {sidebarOpen && (
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-primary-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">あなた</p>
                    <p className="text-xs text-muted-foreground">Pro Plan</p>
                  </div>
                </div>
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDarkMode(!isDarkMode)}
                className="h-8 w-8"
              >
                {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </SidebarFooter>
      </Sidebar>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 border-b border-border glass-effect flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-foreground">
              {navigationItems.find(item => item.id === activeItem)?.label || 'Dashboard'}
            </h2>
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-400 rounded-full" />
            </Button>
            
            <Button variant="glow" className="relative">
              <Brain className="h-4 w-4" />
              AI アシスタント
            </Button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto bg-background/50">
          {renderContent()}
        </main>
      </div>
    </div>
  )
}