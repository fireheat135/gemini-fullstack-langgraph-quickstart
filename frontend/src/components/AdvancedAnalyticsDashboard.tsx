import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  TrendingUp, 
  BarChart3, 
  PieChart, 
  Activity,
  Target,
  Zap,
  Brain,
  AlertTriangle,
  CheckCircle,
  Clock,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'

// 型定義
interface CausalInferenceResult {
  method: string
  treatment_effect: number
  confidence_interval: [number, number]
  p_value: number
  statistical_significance: boolean
  effect_size: string
  interpretation: string
  recommendations: string[]
}

interface RegressionResult {
  model_performance: {
    r2_test: number
    adjusted_r2: number
    f_p_value: number
  }
  coefficients: Array<{
    feature: string
    coefficient: number
    p_value: number
    significant: boolean
  }>
  insights: string[]
  recommendations: string[]
}

interface ClusterResult {
  n_clusters: number
  silhouette_score: number
  cluster_profiles: Record<number, {
    size: number
    percentage: number
    feature_means: Record<string, number>
    common_characteristics: string[]
  }>
  insights: string[]
  recommendations: string[]
}

interface TimeSeriesResult {
  trend_analysis: {
    direction: string
    slope: number
    r_squared: number
    significance: boolean
  }
  seasonal_patterns: {
    weekday_effects: Record<number, number>
    best_weekday: number
    worst_weekday: number
  }
  insights: string[]
  recommendations: string[]
}

const AdvancedAnalyticsDashboard: React.FC = () => {
  // ステート管理
  const [selectedAnalysis, setSelectedAnalysis] = useState<string>('causal_inference')
  const [analysisResults, setAnalysisResults] = useState<{
    causal_inference?: CausalInferenceResult
    regression?: RegressionResult
    clustering?: ClusterResult
    time_series?: TimeSeriesResult
  }>({})
  const [isLoading, setIsLoading] = useState(false)
  const [selectedArticles] = useState<string[]>([])
  const [analysisConfig, setAnalysisConfig] = useState({
    target_variable: 'daily_pv',
    analysis_period: '30',
    significance_level: '0.05'
  })

  // 分析実行
  const runAnalysis = async (analysisType: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`/api/analytics/${analysisType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          article_ids: selectedArticles,
          config: analysisConfig
        })
      })

      if (response.ok) {
        const result = await response.json()
        setAnalysisResults(prev => ({
          ...prev,
          [analysisType]: result
        }))
      }
    } catch (error) {
      console.error('分析実行エラー:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // 因果推論ダッシュボード
  const CausalInferenceDashboard = () => {
    const result = analysisResults.causal_inference

    return (
      <div className="space-y-6">
        {/* 設定パネル */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              因果推論分析設定
            </CardTitle>
            <CardDescription>
              差分の差分法、CausalImpactによる真の効果測定
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">分析手法</label>
                <Select defaultValue="did">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="did">差分の差分法 (DID)</SelectItem>
                    <SelectItem value="causal_impact">CausalImpact</SelectItem>
                    <SelectItem value="synthetic_control">合成コントロール法</SelectItem>
                    <SelectItem value="rdd">回帰不連続デザイン</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">目的変数</label>
                <Select 
                  value={analysisConfig.target_variable} 
                  onValueChange={(value) => setAnalysisConfig(prev => ({ ...prev, target_variable: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily_pv">ページビュー</SelectItem>
                    <SelectItem value="conversions">コンバージョン</SelectItem>
                    <SelectItem value="engagement_score">エンゲージメント</SelectItem>
                    <SelectItem value="social_shares">ソーシャルシェア</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">分析期間</label>
                <Select 
                  value={analysisConfig.analysis_period} 
                  onValueChange={(value) => setAnalysisConfig(prev => ({ ...prev, analysis_period: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="7">1週間</SelectItem>
                    <SelectItem value="30">1ヶ月</SelectItem>
                    <SelectItem value="90">3ヶ月</SelectItem>
                    <SelectItem value="180">6ヶ月</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button 
              onClick={() => runAnalysis('causal_inference')} 
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  分析実行中...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  因果推論実行
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* 結果表示 */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 効果サマリー */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">因果効果サマリー</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center p-6 border rounded-lg">
                  <div className="text-4xl font-bold mb-2 flex items-center justify-center gap-2">
                    {result.treatment_effect > 0 ? '+' : ''}{result.treatment_effect.toFixed(3)}
                    {result.statistical_significance ? (
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    ) : (
                      <AlertTriangle className="w-6 h-6 text-orange-600" />
                    )}
                  </div>
                  <p className="text-lg font-medium">平均処置効果</p>
                  <p className="text-sm text-muted-foreground">{result.method}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded">
                    <p className="text-2xl font-bold text-blue-600">
                      {result.p_value.toFixed(4)}
                    </p>
                    <p className="text-sm text-blue-600">p値</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded">
                    <p className="text-2xl font-bold text-green-600">
                      {result.effect_size}
                    </p>
                    <p className="text-sm text-green-600">効果サイズ</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">信頼区間 (95%)</h4>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="font-mono">{result.confidence_interval[0].toFixed(3)}</span>
                    <span className="text-muted-foreground">〜</span>
                    <span className="font-mono">{result.confidence_interval[1].toFixed(3)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 解釈と推奨事項 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">分析結果と推奨事項</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">結果の解釈</h4>
                  <Alert>
                    <AlertDescription>{result.interpretation}</AlertDescription>
                  </Alert>
                </div>

                <div>
                  <h4 className="font-medium mb-2">推奨事項</h4>
                  <div className="space-y-2">
                    {result.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start gap-2 p-3 border rounded">
                        <Target className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                        <p className="text-sm">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <Badge variant={result.statistical_significance ? "default" : "secondary"}>
                    {result.statistical_significance ? "統計的有意" : "統計的非有意"}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    )
  }

  // 重回帰分析ダッシュボード
  const RegressionDashboard = () => {
    const result = analysisResults.regression

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              重回帰分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => runAnalysis('regression')} 
              disabled={isLoading}
              className="mb-4"
            >
              回帰分析実行
            </Button>

            {result && (
              <div className="space-y-6">
                {/* モデル性能 */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{(result.model_performance.r2_test * 100).toFixed(1)}%</p>
                    <p className="text-sm text-muted-foreground">決定係数 (R²)</p>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{(result.model_performance.adjusted_r2 * 100).toFixed(1)}%</p>
                    <p className="text-sm text-muted-foreground">調整済みR²</p>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{result.model_performance.f_p_value.toFixed(4)}</p>
                    <p className="text-sm text-muted-foreground">F統計量 p値</p>
                  </div>
                </div>

                {/* 係数表 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">回帰係数</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {result.coefficients.slice(0, 10).map((coef, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded">
                          <span className="font-medium">{coef.feature}</span>
                          <div className="flex items-center gap-2">
                            <span className={`font-mono ${coef.coefficient > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {coef.coefficient > 0 ? '+' : ''}{coef.coefficient.toFixed(4)}
                            </span>
                            <Badge variant={coef.significant ? "default" : "secondary"} className="text-xs">
                              p={coef.p_value.toFixed(3)}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* 洞察 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">主要な洞察</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {result.insights.map((insight, index) => (
                        <Alert key={index}>
                          <AlertTriangle className="h-4 w-4" />
                          <AlertDescription>{insight}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  // クラスター分析ダッシュボード
  const ClusteringDashboard = () => {
    const result = analysisResults.clustering

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              クラスター分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => runAnalysis('clustering')} 
              disabled={isLoading}
              className="mb-4"
            >
              クラスター分析実行
            </Button>

            {result && (
              <div className="space-y-6">
                {/* クラスター概要 */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{result.n_clusters}</p>
                    <p className="text-sm text-muted-foreground">クラスター数</p>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{result.silhouette_score.toFixed(3)}</p>
                    <p className="text-sm text-muted-foreground">シルエット係数</p>
                  </div>
                </div>

                {/* クラスタープロファイル */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(result.cluster_profiles).map(([clusterId, profile]) => (
                    <Card key={clusterId}>
                      <CardHeader>
                        <CardTitle className="text-lg">クラスター {clusterId}</CardTitle>
                        <CardDescription>{profile.size}記事 ({profile.percentage.toFixed(1)}%)</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <h5 className="font-medium mb-2">特徴</h5>
                          <div className="space-y-1">
                            {profile.common_characteristics.map((char, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {char}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h5 className="font-medium mb-2">平均PV</h5>
                          <p className="text-lg font-bold">
                            {profile.feature_means.daily_pv?.toFixed(0) || '--'}
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* 洞察 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">クラスター分析の洞察</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {result.insights.map((insight, index) => (
                        <Alert key={index}>
                          <Activity className="h-4 w-4" />
                          <AlertDescription>{insight}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  // 時系列分析ダッシュボード
  const TimeSeriesDashboard = () => {
    const result = analysisResults.time_series
    const weekdayNames = ['月', '火', '水', '木', '金', '土', '日']

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              時系列分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => runAnalysis('time_series')} 
              disabled={isLoading}
              className="mb-4"
            >
              時系列分析実行
            </Button>

            {result && (
              <div className="space-y-6">
                {/* トレンド概要 */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded">
                    <p className="text-lg font-bold">{result.trend_analysis.direction}</p>
                    <p className="text-sm text-muted-foreground">トレンド方向</p>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{result.trend_analysis.slope.toFixed(4)}</p>
                    <p className="text-sm text-muted-foreground">トレンド傾き</p>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <p className="text-2xl font-bold">{(result.trend_analysis.r_squared * 100).toFixed(1)}%</p>
                    <p className="text-sm text-muted-foreground">決定係数</p>
                  </div>
                </div>

                {/* 曜日パターン */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">曜日別パフォーマンス</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-7 gap-2">
                      {Object.entries(result.seasonal_patterns.weekday_effects).map(([dayIndex, effect]) => (
                        <div 
                          key={dayIndex} 
                          className={`text-center p-3 rounded ${
                            parseInt(dayIndex) === result.seasonal_patterns.best_weekday 
                              ? 'bg-green-50 border-green-500' 
                              : parseInt(dayIndex) === result.seasonal_patterns.worst_weekday
                              ? 'bg-red-50 border-red-500'
                              : 'bg-gray-50'
                          }`}
                        >
                          <p className="text-sm font-medium">{weekdayNames[parseInt(dayIndex)]}</p>
                          <p className="text-lg font-bold">{effect.toFixed(2)}</p>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4 flex justify-between text-sm text-muted-foreground">
                      <span>最適: {weekdayNames[result.seasonal_patterns.best_weekday]}曜日</span>
                      <span>最低: {weekdayNames[result.seasonal_patterns.worst_weekday]}曜日</span>
                    </div>
                  </CardContent>
                </Card>

                {/* 洞察と推奨 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">主要な洞察</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {result.insights.map((insight, index) => (
                          <Alert key={index}>
                            <Clock className="h-4 w-4" />
                            <AlertDescription>{insight}</AlertDescription>
                          </Alert>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">推奨事項</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {result.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-start gap-2 p-3 border rounded">
                            <Target className="w-4 h-4 mt-0.5 text-blue-600 flex-shrink-0" />
                            <p className="text-sm">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">高度データ分析</h1>
          <p className="text-muted-foreground">
            因果推論・統計分析による記事パフォーマンスの科学的解析
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            レポート出力
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            フィルター
          </Button>
        </div>
      </div>

      {/* 分析タブ */}
      <Tabs value={selectedAnalysis} onValueChange={setSelectedAnalysis} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="causal_inference">因果推論</TabsTrigger>
          <TabsTrigger value="regression">重回帰分析</TabsTrigger>
          <TabsTrigger value="clustering">クラスター分析</TabsTrigger>
          <TabsTrigger value="time_series">時系列分析</TabsTrigger>
        </TabsList>

        <TabsContent value="causal_inference" className="space-y-4">
          <CausalInferenceDashboard />
        </TabsContent>

        <TabsContent value="regression" className="space-y-4">
          <RegressionDashboard />
        </TabsContent>

        <TabsContent value="clustering" className="space-y-4">
          <ClusteringDashboard />
        </TabsContent>

        <TabsContent value="time_series" className="space-y-4">
          <TimeSeriesDashboard />
        </TabsContent>
      </Tabs>
    </div>
  )
}

export { AdvancedAnalyticsDashboard };
export default AdvancedAnalyticsDashboard;