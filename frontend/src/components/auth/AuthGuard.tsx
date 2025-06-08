import { ReactNode, useState } from 'react'
import { useAuth } from './AuthContext'
import { AuthDialog } from './AuthDialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Lock, LogIn, UserPlus, Zap } from 'lucide-react'
import apiClient from '@/lib/api'

interface AuthGuardProps {
  children: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const [authDialogOpen, setAuthDialogOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const { isAuthenticated, skipAuth } = useAuth()

  const handleLogin = () => {
    setAuthMode('login')
    setAuthDialogOpen(true)
  }

  const handleRegister = () => {
    setAuthMode('register')
    setAuthDialogOpen(true)
  }

  const handleSkipLogin = () => {
    skipAuth()
  }

  if (!isAuthenticated) {
    return (
      <>
        <div className="flex items-center justify-center min-h-[calc(100vh-3.5rem)] bg-gradient-to-br from-background to-muted/20">
          <Card className="w-full max-w-md mx-4">
            <CardHeader className="text-center space-y-4">
              <div className="mx-auto w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                <Lock className="w-6 h-6 text-primary" />
              </div>
              <CardTitle className="text-2xl">認証が必要です</CardTitle>
              <CardDescription>
                この機能を利用するにはログインまたは新規登録が必要です
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                onClick={handleLogin} 
                className="w-full"
                size="lg"
              >
                <LogIn className="mr-2 h-4 w-4" />
                ログイン
              </Button>
              <Button 
                onClick={handleRegister} 
                variant="outline" 
                className="w-full"
                size="lg"
              >
                <UserPlus className="mr-2 h-4 w-4" />
                新規登録
              </Button>
              <div className="pt-4 border-t">
                <Button 
                  onClick={handleSkipLogin} 
                  variant="secondary" 
                  className="w-full"
                  size="lg"
                >
                  <Zap className="mr-2 h-4 w-4" />
                  ログインスキップしてUIを体験
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <AuthDialog 
          open={authDialogOpen} 
          onOpenChange={setAuthDialogOpen}
          defaultMode={authMode}
        />
      </>
    )
  }

  return <>{children}</>
}