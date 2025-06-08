import { useState } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  BarChart3, 
  FileText, 
  Home, 
  Key, 
  Search, 
  Settings, 
  Workflow,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { useLocation, Link } from 'react-router-dom'

const navigation = [
  { name: 'ホーム', href: '/dashboard', icon: Home },
  { name: 'キーワード分析', href: '/keywords', icon: Search },
  { name: 'SEO施策', href: '/seo-workflow', icon: Workflow },
  { name: 'コンテンツ', href: '/content', icon: FileText },
  { name: 'レポート', href: '/analytics', icon: BarChart3 },
  { name: 'API設定', href: '/api-keys', icon: Key },
  { name: '設定', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()

  return (
    <div className={cn(
      'fixed left-0 top-14 h-[calc(100vh-3.5rem)] bg-background border-r transition-all duration-300',
      collapsed ? 'w-16' : 'w-64'
    )}>
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between p-4">
          {!collapsed && (
            <h2 className="text-lg font-semibold">メニュー</h2>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setCollapsed(!collapsed)}
            className="h-8 w-8 p-0"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>
        
        <ScrollArea className="flex-1">
          <nav className="space-y-1 px-3">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              const Icon = item.icon
              
              return (
                <Button
                  key={item.name}
                  asChild
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={cn(
                    'w-full justify-start',
                    collapsed && 'justify-center px-0'
                  )}
                >
                  <Link to={item.href}>
                    <Icon className={cn('h-4 w-4', !collapsed && 'mr-2')} />
                    {!collapsed && item.name}
                  </Link>
                </Button>
              )
            })}
          </nav>
        </ScrollArea>
      </div>
    </div>
  )
}