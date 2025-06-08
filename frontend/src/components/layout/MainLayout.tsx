import { ReactNode } from 'react'
import { Navbar } from './Navbar'
import { Sidebar } from './Sidebar'
import { useAuth } from '../auth/AuthContext'
import { AuthGuard } from '@/components/auth/AuthGuard'

interface MainLayoutProps {
  children: ReactNode
  requireAuth?: boolean
}

export function MainLayout({ children, requireAuth = false }: MainLayoutProps) {
  const { isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex">
        {requireAuth && <Sidebar />}
        <main className={`flex-1 ${requireAuth ? 'ml-64' : ''}`}>
          {requireAuth ? (
            <AuthGuard>{children}</AuthGuard>
          ) : (
            children
          )}
        </main>
      </div>
    </div>
  )
}