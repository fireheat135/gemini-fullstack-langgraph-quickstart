import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  BarChart3, 
  TrendingUp, 
  Search, 
  FileText, 
  Zap, 
  Brain,
  Target,
  Globe,
  Users,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Sparkles,
  RefreshCw,
  Plus,
  Eye,
  Edit,
  Share
} from 'lucide-react';

interface ModernDashboardProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export function ModernDashboard({ activeView, onViewChange }: ModernDashboardProps) {
  const [stats, setStats] = useState({
    totalKeywords: 1247,
    contentPieces: 89,
    avgRanking: 12.4,
    traffic: 45672,
    conversionRate: 3.2,
    activeProjects: 8
  });

  const [recentActivity] = useState([
    { action: 'Keyword analysis completed', time: '2 minutes ago', type: 'success' },
    { action: 'Content published: "Best SEO Practices"', time: '1 hour ago', type: 'info' },
    { action: 'Competitor analysis updated', time: '3 hours ago', type: 'warning' },
    { action: 'AI research workflow finished', time: '5 hours ago', type: 'success' }
  ]);

  const [topKeywords] = useState([
    { keyword: 'AI SEO tools', position: 3, change: +2, volume: 8900 },
    { keyword: 'content optimization', position: 7, change: -1, volume: 5400 },
    { keyword: 'keyword research', position: 1, change: 0, volume: 12000 },
    { keyword: 'SEO analytics', position: 12, change: +5, volume: 3200 }
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-purple-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800/50 bg-slate-900/50 backdrop-blur-xl">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-purple-300 bg-clip-text text-transparent">
                Scrib AI Dashboard
              </h1>
              <p className="text-slate-400 text-sm">Welcome back, Creator</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Button size="sm" variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-800">
              <RefreshCw className="w-4 h-4 mr-2" />
              Sync
            </Button>
            <Button size="sm" className="bg-gradient-to-r from-purple-600 to-blue-600">
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-slate-900/30 backdrop-blur-xl border-r border-slate-800/50 min-h-screen">
          <nav className="p-4 space-y-2">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'research', label: 'AI Research', icon: Brain },
              { id: 'keywords', label: 'Keywords', icon: Search },
              { id: 'content', label: 'Content', icon: FileText },
              { id: 'analytics', label: 'Analytics', icon: TrendingUp },
              { id: 'settings', label: 'Settings', icon: Target }
            ].map((item) => (
              <Button
                key={item.id}
                variant={activeView === item.id ? "default" : "ghost"}
                className={`w-full justify-start ${
                  activeView === item.id
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
                onClick={() => onViewChange(item.id)}
              >
                <item.icon className="w-4 h-4 mr-3" />
                {item.label}
              </Button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeView === 'overview' && (
            <div className="space-y-6">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-400">
                      Total Keywords
                    </CardTitle>
                    <Search className="h-4 w-4 text-purple-400" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">{stats.totalKeywords.toLocaleString()}</div>
                    <div className="flex items-center text-xs text-green-400">
                      <ArrowUpRight className="w-3 h-3 mr-1" />
                      +12% from last month
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-400">
                      Content Pieces
                    </CardTitle>
                    <FileText className="h-4 w-4 text-blue-400" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">{stats.contentPieces}</div>
                    <div className="flex items-center text-xs text-green-400">
                      <ArrowUpRight className="w-3 h-3 mr-1" />
                      +8 this week
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-400">
                      Avg. Ranking
                    </CardTitle>
                    <TrendingUp className="h-4 w-4 text-green-400" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">{stats.avgRanking}</div>
                    <div className="flex items-center text-xs text-green-400">
                      <ArrowUpRight className="w-3 h-3 mr-1" />
                      Improved by 2.1
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-slate-400">
                      Monthly Traffic
                    </CardTitle>
                    <Users className="h-4 w-4 text-orange-400" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-white">{stats.traffic.toLocaleString()}</div>
                    <div className="flex items-center text-xs text-red-400">
                      <ArrowDownRight className="w-3 h-3 mr-1" />
                      -3% from last month
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid lg:grid-cols-3 gap-6">
                {/* Top Keywords */}
                <Card className="lg:col-span-2 bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center">
                      <Target className="w-5 h-5 mr-2 text-purple-400" />
                      Top Performing Keywords
                    </CardTitle>
                    <CardDescription className="text-slate-400">
                      Your best ranking keywords this month
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {topKeywords.map((keyword, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                          <div className="flex-1">
                            <div className="text-white font-medium">{keyword.keyword}</div>
                            <div className="text-slate-400 text-sm">{keyword.volume.toLocaleString()} monthly searches</div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <Badge variant="outline" className="border-purple-400/50 text-purple-300">
                              #{keyword.position}
                            </Badge>
                            <div className={`flex items-center text-sm ${
                              keyword.change > 0 ? 'text-green-400' : keyword.change < 0 ? 'text-red-400' : 'text-slate-400'
                            }`}>
                              {keyword.change > 0 ? <ArrowUpRight className="w-3 h-3" /> : 
                               keyword.change < 0 ? <ArrowDownRight className="w-3 h-3" /> : 
                               <Activity className="w-3 h-3" />}
                              {keyword.change !== 0 && Math.abs(keyword.change)}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Recent Activity */}
                <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="text-white flex items-center">
                      <Clock className="w-5 h-5 mr-2 text-blue-400" />
                      Recent Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {recentActivity.map((activity, index) => (
                        <div key={index} className="flex items-start space-x-3">
                          <div className={`w-2 h-2 rounded-full mt-2 ${
                            activity.type === 'success' ? 'bg-green-400' :
                            activity.type === 'warning' ? 'bg-orange-400' :
                            'bg-blue-400'
                          }`} />
                          <div className="flex-1">
                            <div className="text-white text-sm">{activity.action}</div>
                            <div className="text-slate-400 text-xs">{activity.time}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions */}
              <Card className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 border-purple-500/30 backdrop-blur-sm">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">
                        Ready to boost your SEO?
                      </h3>
                      <p className="text-slate-300">
                        Start a new AI-powered research session or optimize existing content.
                      </p>
                    </div>
                    <div className="flex space-x-3">
                      <Button 
                        onClick={() => onViewChange('research')}
                        className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                      >
                        <Brain className="w-4 h-4 mr-2" />
                        Start Research
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => onViewChange('content')}
                        className="border-slate-600 text-slate-300 hover:bg-slate-800"
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        Create Content
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Other views would be rendered here based on activeView */}
          {activeView !== 'overview' && (
            <div className="flex items-center justify-center h-96">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">
                  {activeView.charAt(0).toUpperCase() + activeView.slice(1)} Coming Soon
                </h3>
                <p className="text-slate-400">
                  This section is under development. Check back soon for updates!
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}