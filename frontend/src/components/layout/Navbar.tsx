import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { LogIn, LogOut, Settings, User, Zap } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { AuthDialog } from '@/components/auth/AuthDialog'

export function Navbar() {
  const [authDialogOpen, setAuthDialogOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const isDemoMode = user?.email === 'dev@example.com'

  const handleLogin = () => {
    setAuthMode('login')
    setAuthDialogOpen(true)
  }

  const handleRegister = () => {
    setAuthMode('register')
    setAuthDialogOpen(true)
  }

  return (
    <>
      <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-14 items-center px-4">
          <div className="mr-4 hidden md:flex">
            <Link to="/" className="mr-6 flex items-center space-x-2">
              <span className="font-bold text-xl">Scriv</span>
              {isDemoMode && (
                <Badge variant="secondary" className="ml-2">
                  <Zap className="w-3 h-3 mr-1" />
                  開発モード
                </Badge>
              )}
            </Link>
          </div>
          
          <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
            <div className="w-full flex-1 md:w-auto md:flex-none">
              {/* 検索バー等があればここに配置 */}
            </div>
            
            <nav className="flex items-center space-x-2">
              {isAuthenticated ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src="/avatars/01.png" alt={user?.name || ''} />
                        <AvatarFallback>
                          {user?.name?.charAt(0).toUpperCase() || 'U'}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-56" align="end" forceMount>
                    <DropdownMenuLabel className="font-normal">
                      <div className="flex flex-col space-y-1">
                        <p className="text-sm font-medium leading-none">{user?.name}</p>
                        <p className="text-xs leading-none text-muted-foreground">
                          {user?.email}
                        </p>
                      </div>
                    </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => navigate('/dashboard')}>
                      <User className="mr-2 h-4 w-4" />
                      ダッシュボード
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => navigate('/settings')}>
                      <Settings className="mr-2 h-4 w-4" />
                      設定
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logout}>
                      <LogOut className="mr-2 h-4 w-4" />
                      ログアウト
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" onClick={handleLogin}>
                    <LogIn className="mr-2 h-4 w-4" />
                    ログイン
                  </Button>
                  <Button size="sm" onClick={handleRegister}>
                    新規登録
                  </Button>
                </div>
              )}
            </nav>
          </div>
        </div>
      </nav>

      <AuthDialog 
        open={authDialogOpen} 
        onOpenChange={setAuthDialogOpen}
        defaultMode={authMode}
      />
    </>
  )
}