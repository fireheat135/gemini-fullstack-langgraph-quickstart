import { ReactNode, useState } from 'react'
import { ModernLanding } from './ModernLanding'
import { ModernDashboard } from './ModernDashboard'

interface ModernLayoutProps {
  children: ReactNode
}

export function ModernLayout({ children }: ModernLayoutProps) {
  const [showDashboard, setShowDashboard] = useState(false)
  const [activeView, setActiveView] = useState('overview')

  if (!showDashboard) {
    return <ModernLanding onGetStarted={() => setShowDashboard(true)} />
  }

  return <ModernDashboard activeView={activeView} onViewChange={setActiveView} />
}