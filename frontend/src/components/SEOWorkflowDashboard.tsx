import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Checkbox } from '@/components/ui/checkbox'
import { apiClient } from '@/lib/api'
import { useAuth } from '@/components/auth/AuthContext'
import { 
  Search, 
  Lightbulb, 
  PenTool, 
  Edit3, 
  Send, 
  BarChart3, 
  RefreshCw,
  Play,
  Pause,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  Users,
  Eye,
  MousePointer,
  Check,
  X,
  UserCheck
} from 'lucide-react'

// 型定義
interface WorkflowStep {
  id: string
  name: string
  icon: React.ElementType
  status: 'pending' | 'in_progress' | 'completed' | 'error' | 'waiting_approval'
  progress: number
  description: string
}

interface HeadingItem {
  level: string
  text: string
  keywords?: string[]
}

interface SEOWorkflowState {
  sessionId: string | null
  currentStep: string
  keyword: string
  status: string
  progress: number
  isRunning: boolean
  pendingApproval: any | null
  results: {
    research?: any
    planning?: any
    writing?: any
    editing?: any
    publishing?: any
    analysis?: any
    improvement?: any
  }
}

const SEOWorkflowDashboard: React.FC = () => {
  const { isAuthenticated, skipAuth, user } = useAuth()
  
  // ステート管理
  const [workflowState, setWorkflowState] = useState<SEOWorkflowState>({
    sessionId: null,
    currentStep: 'research',
    keyword: '',
    status: 'idle',
    progress: 0,
    isRunning: false,
    pendingApproval: null,
    results: {}
  })

  const [formData, setFormData] = useState({
    keyword: '',
    targetAudience: '一般',
    contentType: '記事',
    workflowMode: 'semi_auto',
    useRealData: true
  })

  const [error, setError] = useState<string | null>(null)
  const [approvalHeadings, setApprovalHeadings] = useState<HeadingItem[]>([])
  const [headingModifications, setHeadingModifications] = useState<string>('')

  // ワークフローステップ定義
  const workflowSteps: WorkflowStep[] = [
    {
      id: 'research',
      name: 'リサーチ',
      icon: Search,
      status: 'pending',
      progress: 0,
      description: 'Google Trends・Search Console分析・競合調査'
    },
    {
      id: 'planning',
      name: '企画',
      icon: Lightbulb,
      status: 'pending',
      progress: 0,
      description: 'SEO最適化見出し構成・4パターン戦略'
    },
    {
      id: 'writing',
      name: '執筆',
      icon: PenTool,
      status: 'pending',
      progress: 0,
      description: 'LangGraph品質ループ・Deep Research統合'
    },
    {
      id: 'editing',
      name: '修正',
      icon: Edit3,
      status: 'pending',
      progress: 0,
      description: 'AI品質チェック・改善提案・最適化'
    },
    {
      id: 'publishing',
      name: '出稿',
      icon: Send,
      status: 'pending',
      progress: 0,
      description: 'スケジュール最適化・CMS連携準備'
    },
    {
      id: 'analysis',
      name: '分析',
      icon: BarChart3,
      status: 'pending',
      progress: 0,
      description: 'パフォーマンス予測・KPI設定・A/Bテスト'
    },
    {
      id: 'improvement',
      name: '改善',
      icon: RefreshCw,
      status: 'pending',
      progress: 0,
      description: '継続改善提案・学習ループ・最適化戦略'
    }
  ]

  // ステップステータス更新
  const updateStepStatus = (stepId: string, status: WorkflowStep['status'], progress: number) => {
    workflowSteps.forEach(step => {
      if (step.id === stepId) {
        step.status = status
        step.progress = progress
      }
    })
  }

  // ワークフロー開始
  const startWorkflow = async () => {
    if (!formData.keyword.trim()) {
      setError('キーワードを入力してください')
      return
    }

    try {
      setError(null)
      setWorkflowState(prev => ({ ...prev, isRunning: true }))

      const response = await apiClient.startSeoWorkflow({
        keyword: formData.keyword,
        target_audience: formData.targetAudience,
        content_type: formData.contentType,
        workflow_mode: formData.workflowMode,
        use_real_data: formData.useRealData
      })

      const data = response.data
      setWorkflowState(prev => ({
        ...prev,
        sessionId: data.session_id,
        keyword: data.keyword,
        status: 'in_progress',
        currentStep: 'research'
      }))

      // ステータス監視開始
      startStatusPolling(data.session_id)

    } catch (error: any) {
      setError(error.response?.data?.detail || 'ワークフロー開始エラー')
      setWorkflowState(prev => ({ ...prev, isRunning: false }))
    }
  }

  // ステータスポーリング
  const startStatusPolling = (sessionId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await apiClient.getSeoWorkflowStatus(sessionId)
        const status = response.data

        setWorkflowState(prev => ({
          ...prev,
          currentStep: status.current_step,
          status: status.status,
          progress: status.progress,
          results: status.step_results || {},
          pendingApproval: status.pending_approval,
          isRunning: status.status === 'in_progress'
        }))

        // ステップ状態更新
        updateStepStatus(status.current_step, 
          status.status === 'waiting_approval' ? 'waiting_approval' : 
          status.status === 'in_progress' ? 'in_progress' : 'completed', 
          status.progress)

        // 完了または承認待ちの場合、ポーリング停止
        if (status.status === 'completed' || status.status === 'waiting_approval' || status.status === 'error') {
          clearInterval(pollInterval)
          
          if (status.status === 'waiting_approval' && status.pending_approval?.type === 'headings') {
            // 見出し承認データを設定
            setApprovalHeadings(status.pending_approval.data || [])
          }

          if (status.status === 'completed') {
            setWorkflowState(prev => ({ ...prev, isRunning: false }))
            // 完成通知
            alert(`「${status.keyword}」のSEO記事が完成しました！`)
          }
        }

      } catch (error) {
        console.error('Status polling error:', error)
        clearInterval(pollInterval)
      }
    }, 3000) // 3秒間隔でポーリング
  }

  // 見出し承認送信
  const approveHeadings = async () => {
    if (!workflowState.sessionId) return

    try {
      setError(null)
      
      const response = await apiClient.approveSeoWorkflowHeadings({
        session_id: workflowState.sessionId,
        approved_headings: approvalHeadings,
        modifications: headingModifications ? { general: headingModifications } : {}
      })

      setWorkflowState(prev => ({
        ...prev,
        status: 'in_progress',
        pendingApproval: null,
        isRunning: true
      }))

      // ポーリング再開
      startStatusPolling(workflowState.sessionId)

    } catch (error: any) {
      setError(error.response?.data?.detail || '承認送信エラー')
    }
  }

  // 見出し編集
  const updateHeading = (index: number, field: string, value: string) => {
    const updated = [...approvalHeadings]
    updated[index] = { ...updated[index], [field]: value }
    setApprovalHeadings(updated)
  }

  // ステップアイコンコンポーネント
  const StepIcon = ({ step }: { step: WorkflowStep }) => {
    const IconComponent = step.icon
    
    if (step.status === 'completed') {
      return <CheckCircle className="w-6 h-6 text-green-500" />
    } else if (step.status === 'in_progress') {
      return <Clock className="w-6 h-6 text-blue-500 animate-pulse" />
    } else if (step.status === 'waiting_approval') {
      return <AlertCircle className="w-6 h-6 text-orange-500" />
    } else if (step.status === 'error') {
      return <X className="w-6 h-6 text-red-500" />
    } else {
      return <IconComponent className="w-6 h-6 text-gray-400" />
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* ヘッダー */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-8 bg-primary rounded-sm"></div>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">SEO Workflow</h1>
              <p className="text-sm text-muted-foreground">
                AI-powered content creation with real-time data integration
              </p>
            </div>
          </div>
        </div>

        {/* 認証状態表示 */}
        {!isAuthenticated && (
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg border border-border">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Demo mode for testing</span>
              {user && <span className="text-xs text-muted-foreground">({user.email})</span>}
            </div>
            <Button onClick={skipAuth} variant="outline" size="sm">
              <UserCheck className="w-4 h-4 mr-2" />
              Enable Demo Mode
            </Button>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 設定パネル */}
        {!workflowState.isRunning && !workflowState.sessionId && (
          <Card className="border-border">
            <CardHeader className="space-y-1">
              <CardTitle className="text-lg font-medium">New Workflow</CardTitle>
              <CardDescription className="text-muted-foreground">
                Configure your SEO content generation workflow
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Target Keyword
                  </label>
                  <Input
                    placeholder="Enter your main keyword..."
                    value={formData.keyword}
                    onChange={(e) => setFormData(prev => ({ ...prev, keyword: e.target.value }))}
                    className="bg-background"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none">Target Audience</label>
                    <Select value={formData.targetAudience} onValueChange={(value) => setFormData(prev => ({ ...prev, targetAudience: value }))}>
                      <SelectTrigger className="bg-background">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="一般">General</SelectItem>
                        <SelectItem value="初心者">Beginners</SelectItem>
                        <SelectItem value="中級者">Intermediate</SelectItem>
                        <SelectItem value="専門家">Experts</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none">Workflow Mode</label>
                    <Select value={formData.workflowMode} onValueChange={(value) => setFormData(prev => ({ ...prev, workflowMode: value }))}>
                      <SelectTrigger className="bg-background">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="semi_auto">Semi-automatic (with approval)</SelectItem>
                        <SelectItem value="full_auto">Fully automatic</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="useRealData"
                    checked={formData.useRealData}
                    onCheckedChange={(checked) => setFormData(prev => ({ ...prev, useRealData: !!checked }))}
                  />
                  <label htmlFor="useRealData" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Use real-time data (Google Trends, Search Console)
                  </label>
                </div>
              </div>
              
              <Button onClick={startWorkflow} className="w-full">
                <Play className="w-4 h-4 mr-2" />
                Start Workflow
              </Button>
            </CardContent>
          </Card>
        )}

        {/* ワークフロー進行状況 */}
        {workflowState.sessionId && (
          <div className="space-y-6">
            {/* 全体進捗 */}
            <Card className="border-border">
              <CardHeader className="space-y-1">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg font-medium">
                      {workflowState.keyword}
                    </CardTitle>
                    <CardDescription className="text-muted-foreground">
                      Workflow Progress
                    </CardDescription>
                  </div>
                  <Badge variant={workflowState.status === 'completed' ? 'default' : 'secondary'} className="text-xs">
                    {workflowState.status === 'in_progress' ? 'Running' : 
                     workflowState.status === 'waiting_approval' ? 'Pending Approval' :
                     workflowState.status === 'completed' ? 'Completed' : workflowState.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Progress</span>
                    <span>{workflowState.progress}%</span>
                  </div>
                  <Progress value={workflowState.progress} className="h-2" />
                </div>
              </CardContent>
            </Card>

            {/* ステップ詳細 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {workflowSteps.map((step) => (
                <Card 
                  key={step.id} 
                  className={`border-border transition-all ${
                    step.id === workflowState.currentStep ? 'ring-1 ring-ring shadow-sm' : ''
                  }`}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <StepIcon step={step} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{step.name}</p>
                        <p className="text-xs text-muted-foreground truncate">{step.description}</p>
                        {step.progress > 0 && (
                          <Progress value={step.progress} className="h-1 mt-2" />
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 見出し承認セクション */}
            {workflowState.pendingApproval?.type === 'headings' && (
              <Card className="border-border">
                <CardHeader className="space-y-1">
                  <CardTitle className="text-lg font-medium">Heading Structure Approval</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Review and approve the AI-generated heading structure before proceeding.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <Alert className="border-border">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-sm">
                      {workflowState.pendingApproval.message}
                    </AlertDescription>
                  </Alert>

                  {/* 見出し一覧 */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-medium">Proposed Structure</h4>
                    {approvalHeadings.map((heading, index) => (
                      <div key={index} className="border border-border rounded-lg p-3 space-y-2 bg-muted/50">
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className="text-xs font-mono bg-background">
                            {heading.level}
                          </Badge>
                          <Input
                            value={heading.text}
                            onChange={(e) => updateHeading(index, 'text', e.target.value)}
                            className="flex-1 bg-background border-border"
                          />
                        </div>
                        {heading.keywords && (
                          <div className="text-xs text-muted-foreground pl-2">
                            Keywords: {Array.isArray(heading.keywords) ? heading.keywords.join(', ') : heading.keywords}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* 修正指示 */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none">Additional Instructions (Optional)</label>
                    <Textarea
                      placeholder="Enter any additional modifications for the heading structure..."
                      value={headingModifications}
                      onChange={(e) => setHeadingModifications(e.target.value)}
                      className="bg-background border-border"
                    />
                  </div>

                  {/* 承認ボタン */}
                  <Button onClick={approveHeadings} className="w-full">
                    <Check className="w-4 h-4 mr-2" />
                    Approve & Continue
                  </Button>
                </CardContent>
              </Card>
            )}

          {/* 結果表示 */}
          {workflowState.results && Object.keys(workflowState.results).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>ワークフロー結果</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="research">
                  <TabsList className="grid w-full grid-cols-7">
                    <TabsTrigger value="research">リサーチ</TabsTrigger>
                    <TabsTrigger value="planning">企画</TabsTrigger>
                    <TabsTrigger value="writing">執筆</TabsTrigger>
                    <TabsTrigger value="editing">修正</TabsTrigger>
                    <TabsTrigger value="publishing">出稿</TabsTrigger>
                    <TabsTrigger value="analysis">分析</TabsTrigger>
                    <TabsTrigger value="improvement">改善</TabsTrigger>
                  </TabsList>

                  <TabsContent value="research" className="space-y-4">
                    {workflowState.results.research && (
                      <div className="space-y-4">
                        <h3 className="font-semibold">SEO機会分析</h3>
                        {workflowState.results.research.real_data_analysis && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Card>
                              <CardHeader>
                                <CardTitle className="text-sm">機会スコア</CardTitle>
                              </CardHeader>
                              <CardContent>
                                <div className="text-2xl font-bold">
                                  {workflowState.results.research.real_data_analysis.opportunity_score?.toFixed(1) || 'N/A'}
                                </div>
                              </CardContent>
                            </Card>
                            <Card>
                              <CardHeader>
                                <CardTitle className="text-sm">推奨キーワード</CardTitle>
                              </CardHeader>
                              <CardContent>
                                <div className="flex flex-wrap gap-1">
                                  {workflowState.results.research.real_data_analysis.suggested_keywords?.slice(0, 5).map((keyword: string, index: number) => (
                                    <Badge key={index} variant="secondary" className="text-xs">
                                      {keyword}
                                    </Badge>
                                  )) || <span className="text-muted-foreground">データなし</span>}
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        )}
                        {workflowState.results.research.ai_analysis && (
                          <div>
                            <h4 className="font-medium mb-2">AI分析結果</h4>
                            <pre className="bg-muted p-4 rounded-lg text-sm overflow-auto">
                              {JSON.stringify(workflowState.results.research.ai_analysis, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="planning" className="space-y-4">
                    {workflowState.results.planning && (
                      <div>
                        <h3 className="font-semibold mb-4">記事企画・見出し構成</h3>
                        {workflowState.results.planning.proposed_headings && (
                          <div className="space-y-2">
                            {workflowState.results.planning.proposed_headings.map((heading: any, index: number) => (
                              <div key={index} className="flex items-center space-x-2 p-2 border rounded">
                                <Badge variant="outline">{heading.level}</Badge>
                                <span className="flex-1">{heading.text}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="writing" className="space-y-4">
                    {workflowState.results.writing && (
                      <div>
                        <h3 className="font-semibold mb-4">執筆結果</h3>
                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <Card>
                            <CardContent className="pt-4">
                              <div className="text-center">
                                <div className="text-2xl font-bold">{workflowState.results.writing.article_content?.word_count || 'N/A'}</div>
                                <div className="text-sm text-muted-foreground">文字数</div>
                              </div>
                            </CardContent>
                          </Card>
                          <Card>
                            <CardContent className="pt-4">
                              <div className="text-center">
                                <div className="text-2xl font-bold">{workflowState.results.writing.quality_score || 'N/A'}</div>
                                <div className="text-sm text-muted-foreground">品質スコア</div>
                              </div>
                            </CardContent>
                          </Card>
                          <Card>
                            <CardContent className="pt-4">
                              <div className="text-center">
                                <div className="text-2xl font-bold">{workflowState.results.writing.iterations || 'N/A'}</div>
                                <div className="text-sm text-muted-foreground">改善回数</div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                        {workflowState.results.writing.article_content && (
                          <div>
                            <h4 className="font-medium mb-2">記事タイトル</h4>
                            <p className="font-semibold text-lg mb-4">{workflowState.results.writing.article_content.title}</p>
                            <h4 className="font-medium mb-2">メタディスクリプション</h4>
                            <p className="text-muted-foreground mb-4">{workflowState.results.writing.article_content.meta_description}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="editing">
                    {workflowState.results.editing && (
                      <div>
                        <h3 className="font-semibold mb-4">編集・改善結果</h3>
                        <p>品質スコア: {workflowState.results.editing.final_quality_score}</p>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="publishing">
                    {workflowState.results.publishing && (
                      <div>
                        <h3 className="font-semibold mb-4">出稿準備</h3>
                        <p>出稿準備完了: {workflowState.results.publishing.ready_for_publish ? 'はい' : 'いいえ'}</p>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="analysis">
                    {workflowState.results.analysis && (
                      <div>
                        <h3 className="font-semibold mb-4">パフォーマンス予測</h3>
                        {workflowState.results.analysis.predicted_performance && (
                          <div className="grid grid-cols-3 gap-4">
                            <Card>
                              <CardContent className="pt-4">
                                <div className="text-center">
                                  <div className="text-2xl font-bold">{workflowState.results.analysis.predicted_performance.estimated_monthly_views}</div>
                                  <div className="text-sm text-muted-foreground">月間予想PV</div>
                                </div>
                              </CardContent>
                            </Card>
                            <Card>
                              <CardContent className="pt-4">
                                <div className="text-center">
                                  <div className="text-2xl font-bold">{workflowState.results.analysis.predicted_performance.expected_ranking}</div>
                                  <div className="text-sm text-muted-foreground">予想順位</div>
                                </div>
                              </CardContent>
                            </Card>
                            <Card>
                              <CardContent className="pt-4">
                                <div className="text-center">
                                  <div className="text-2xl font-bold">{workflowState.results.analysis.predicted_performance.seo_score}</div>
                                  <div className="text-sm text-muted-foreground">SEOスコア</div>
                                </div>
                              </CardContent>
                            </Card>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="improvement">
                    {workflowState.results.improvement && (
                      <div>
                        <h3 className="font-semibold mb-4">改善提案</h3>
                        <div className="space-y-4">
                          {workflowState.results.improvement.recommendations && (
                            <div>
                              <h4 className="font-medium mb-2">推奨事項</h4>
                              <ul className="list-disc pl-5 space-y-1">
                                {workflowState.results.improvement.recommendations.map((rec: string, index: number) => (
                                  <li key={index}>{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {workflowState.results.improvement.next_actions && (
                            <div>
                              <h4 className="font-medium mb-2">次のアクション</h4>
                              <ul className="list-disc pl-5 space-y-1">
                                {workflowState.results.improvement.next_actions.map((action: string, index: number) => (
                                  <li key={index}>{action}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          )}

          {/* 完成通知 */}
          {workflowState.status === 'completed' && workflowState.results.completion_notification && (
            <Card className="border-green-200 bg-green-50">
              <CardHeader>
                <CardTitle className="text-green-800">🎉 記事生成完了！</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-green-700">
                  <p className="font-medium">{workflowState.results.completion_notification.message}</p>
                  <div className="mt-2 text-sm">
                    <p>完成時刻: {new Date(workflowState.results.completion_notification.completed_at).toLocaleString()}</p>
                    <p>文字数: {workflowState.results.completion_notification.final_word_count}文字</p>
                    <p>SEOスコア: {workflowState.results.completion_notification.seo_score}点</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          </div>
        )}
      </div>
    </div>
  )
}

export default SEOWorkflowDashboard