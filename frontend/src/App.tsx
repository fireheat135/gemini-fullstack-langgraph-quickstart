import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/components/auth/AuthContext'
import { MainLayout } from '@/components/layout/MainLayout'
import { DashboardPage } from '@/components/dashboard/DashboardPage'
import { KeywordResearch } from '@/components/KeywordResearch'
import { ContentManager } from '@/components/ContentManager'
import { APIKeyManager } from '@/components/APIKeyManager'
import { SEOResearchDashboard } from '@/components/SEOResearchDashboard'
import SEOWorkflowDashboard from '@/components/SEOWorkflowDashboard'
import { AdvancedAnalyticsDashboard } from '@/components/AdvancedAnalyticsDashboard'
import { WelcomeScreen } from '@/components/WelcomeScreen'
import "@/styles/globals.css"

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* パブリックページ */}
          <Route path="/" element={
            <MainLayout requireAuth={false}>
              <WelcomeScreen />
            </MainLayout>
          } />
          
          {/* 認証が必要なページ */}
          <Route path="/dashboard" element={
            <MainLayout requireAuth={true}>
              <DashboardPage />
            </MainLayout>
          } />
          
          <Route path="/keywords" element={
            <MainLayout requireAuth={true}>
              <KeywordResearch />
            </MainLayout>
          } />
          
          <Route path="/seo-workflow" element={
            <MainLayout requireAuth={false}>
              <SEOWorkflowDashboard />
            </MainLayout>
          } />
          
          <Route path="/seo-research" element={
            <MainLayout requireAuth={true}>
              <SEOResearchDashboard />
            </MainLayout>
          } />
          
          <Route path="/content" element={
            <MainLayout requireAuth={true}>
              <ContentManager />
            </MainLayout>
          } />
          
          <Route path="/analytics" element={
            <MainLayout requireAuth={true}>
              <AdvancedAnalyticsDashboard />
            </MainLayout>
          } />
          
          <Route path="/api-keys" element={
            <MainLayout requireAuth={true}>
              <APIKeyManager />
            </MainLayout>
          } />
          
          <Route path="/settings" element={
            <MainLayout requireAuth={true}>
              <div className="p-6">
                <h1 className="text-2xl font-bold">設定</h1>
                <p className="text-muted-foreground mt-2">設定ページは実装予定です</p>
              </div>
            </MainLayout>
          } />
          
          {/* デフォルトリダイレクト */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}
