import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, MoreHorizontal, Eye, Edit, Trash2, TrendingUp, FileText, Play, Clock, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api';

interface Article {
  id: number;
  title: string;
  content?: string;
  status: 'draft' | 'review' | 'published' | 'archived';
  content_type: string;
  word_count: number;
  reading_time: number;
  seo_score?: number;
  page_views: number;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

interface ArticleListResponse {
  items: Article[];
  total: number;
  skip: number;
  limit: number;
}

interface AnalyticsSummary {
  total_articles: number;
  total_page_views: number;
  total_unique_visitors: number;
  average_seo_score: number;
  top_performing_articles: Array<{
    id: number;
    title: string;
    page_views: number;
    performance_score: number;
  }>;
}

const ContentManager: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [newArticleTitle, setNewArticleTitle] = useState('');
  const [newArticleType, setNewArticleType] = useState('blog_post');
  const [newArticleDescription, setNewArticleDescription] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  
  // SEO Workflow State
  const [showWorkflowModal, setShowWorkflowModal] = useState(false);
  const [workflowKeyword, setWorkflowKeyword] = useState('');
  const [workflowSessionId, setWorkflowSessionId] = useState<string | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<any>(null);
  const [workflowProgress, setWorkflowProgress] = useState(0);
  const [isWorkflowRunning, setIsWorkflowRunning] = useState(false);

  const ITEMS_PER_PAGE = 10;

  // Fetch articles from API
  const fetchArticles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: (currentPage * ITEMS_PER_PAGE).toString(),
        limit: ITEMS_PER_PAGE.toString(),
      });

      if (searchTerm) params.append('search', searchTerm);
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const response = await apiClient.get(`/api/v1/content/articles/?${params}`);
      setArticles(response.data.items);
      setTotalItems(response.data.total);
    } catch (error) {
      console.error('Failed to fetch articles:', error);
      // Fallback to mock data
      setArticles([
        {
          id: 1,
          title: 'AI時代のSEO戦略',
          status: 'published' as const,
          content_type: 'blog',
          word_count: 2500,
          reading_time: 10,
          seo_score: 85,
          page_views: 1250,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z'
        },
        {
          id: 2,
          title: 'キーワード調査の基本',
          status: 'draft' as const,
          content_type: 'blog',
          word_count: 1800,
          reading_time: 7,
          seo_score: 72,
          page_views: 0,
          created_at: '2024-01-14T14:30:00Z',
          updated_at: '2024-01-14T14:30:00Z'
        }
      ]);
      setTotalItems(2);
    } finally {
      setLoading(false);
    }
  };

  // Fetch analytics summary
  const fetchAnalytics = async () => {
    try {
      const response = await apiClient.get('/api/v1/analytics/summary');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      // Fallback to mock data
      setAnalytics({
        total_articles: 15,
        total_page_views: 12500,
        total_unique_visitors: 8200,
        average_seo_score: 78.5,
        top_performing_articles: []
      });
    }
  };

  // Handle article creation
  const handleCreateArticle = async () => {
    if (!newArticleTitle.trim()) return;
    
    setIsCreating(true);
    try {
      await apiClient.createArticle({
        title: newArticleTitle,
        content: '# ' + newArticleTitle + '\n\n記事の内容をここに記述してください。',
        content_type: newArticleType,
        meta_description: newArticleDescription || undefined,
        keywords: []
      });
      
      // Reset form and close modal
      setNewArticleTitle('');
      setNewArticleType('blog_post');
      setNewArticleDescription('');
      setShowCreateModal(false);
      
      // Refresh articles list
      fetchArticles();
    } catch (error) {
      console.error('Failed to create article:', error);
      alert('記事の作成に失敗しました。もう一度お試しください。');
    } finally {
      setIsCreating(false);
    }
  };

  // Start SEO Workflow
  const startSeoWorkflow = async () => {
    if (!workflowKeyword.trim()) return;
    
    setIsWorkflowRunning(true);
    try {
      const response = await apiClient.startSeoWorkflow({
        keyword: workflowKeyword,
        target_audience: '一般',
        content_type: '記事',
        workflow_mode: 'semi_auto',
        use_real_data: true
      });

      setWorkflowSessionId(response.data.session_id);
      setShowWorkflowModal(false);
      
      // Start polling for status
      pollWorkflowStatus(response.data.session_id);
    } catch (error) {
      console.error('Failed to start workflow:', error);
      alert('ワークフローの開始に失敗しました。');
      setIsWorkflowRunning(false);
    }
  };

  // Poll workflow status
  const pollWorkflowStatus = (sessionId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await apiClient.getSeoWorkflowStatus(sessionId);
        const status = response.data;
        
        setWorkflowStatus(status);
        setWorkflowProgress(status.progress);
        
        if (status.status === 'completed' || status.status === 'error') {
          clearInterval(interval);
          setIsWorkflowRunning(false);
          
          if (status.status === 'completed') {
            alert(`「${status.keyword}」の記事が完成しました！`);
            fetchArticles(); // Refresh articles list
          }
        }
      } catch (error) {
        console.error('Status polling error:', error);
        clearInterval(interval);
        setIsWorkflowRunning(false);
      }
    }, 3000);
  };

  useEffect(() => {
    fetchArticles();
    fetchAnalytics();
  }, [currentPage, searchTerm, statusFilter]);

  const handleDelete = async (articleId: number) => {
    if (!confirm('この記事を削除しますか？')) return;

    try {
      await apiClient.delete(`/api/v1/content/articles/${articleId}`);
      fetchArticles();
      fetchAnalytics();
    } catch (error) {
      console.error('Failed to delete article:', error);
    }
  };

  const handlePublish = async (articleId: number) => {
    try {
      await apiClient.post(`/api/v1/content/articles/${articleId}/publish`);
      fetchArticles();
      fetchAnalytics();
    } catch (error) {
      console.error('Failed to publish article:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      draft: 'secondary' as const,
      review: 'outline' as const,
      published: 'default' as const,
      archived: 'destructive' as const,
    };

    const labels = {
      draft: '下書き',
      review: 'レビュー中',
      published: '公開済み',
      archived: 'アーカイブ'
    };

    return (
      <Badge variant={variants[status as keyof typeof variants]}>
        {labels[status as keyof typeof labels]}
      </Badge>
    );
  };

  const getSEOScoreBadge = (score?: number) => {
    if (!score) return <span className="text-muted-foreground">-</span>;

    const color = score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-600';
    return <span className={`font-medium ${color}`}>{score.toFixed(1)}</span>;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
            <FileText className="h-8 w-8 text-primary" />
            コンテンツ
          </h1>
          <p className="text-muted-foreground mt-2">
            記事の作成、編集、分析を効率的に管理できます
          </p>
        </div>
        <div className="flex space-x-2">
          <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                新規記事
              </Button>
            </DialogTrigger>
          </Dialog>
          
          <Dialog open={showWorkflowModal} onOpenChange={setShowWorkflowModal}>
            <DialogTrigger asChild>
              <Button>
                <Play className="h-4 w-4 mr-2" />
                AI記事生成
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>AI記事生成ワークフロー</DialogTitle>
                <DialogDescription>
                  キーワードを入力してAIによる7ステップ記事生成を開始します
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">ターゲットキーワード</label>
                  <Input
                    placeholder="例: React Hooks 使い方"
                    value={workflowKeyword}
                    onChange={(e) => setWorkflowKeyword(e.target.value)}
                  />
                </div>
                <Button 
                  onClick={startSeoWorkflow} 
                  disabled={!workflowKeyword.trim() || isWorkflowRunning}
                  className="w-full"
                >
                  {isWorkflowRunning ? '開始中...' : 'ワークフロー開始'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
        
        {/* Regular Article Creation Dialog */}
        <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>新規記事作成</DialogTitle>
              <DialogDescription>
                新しい記事を作成します。記事タイトルとタイプを選択してください。
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">記事タイトル</label>
                <Input
                  placeholder="記事のタイトルを入力してください"
                  value={newArticleTitle}
                  onChange={(e) => setNewArticleTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">コンテンツタイプ</label>
                <Select value={newArticleType} onValueChange={setNewArticleType}>
                  <SelectTrigger>
                    <SelectValue placeholder="コンテンツタイプを選択" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="blog_post">ブログ記事</SelectItem>
                    <SelectItem value="guide">ガイド記事</SelectItem>
                    <SelectItem value="tutorial">チュートリアル</SelectItem>
                    <SelectItem value="review">レビュー記事</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">メタディスクリプション（オプション）</label>
                <Input
                  placeholder="検索結果に表示される説明文"
                  value={newArticleDescription}
                  onChange={(e) => setNewArticleDescription(e.target.value)}
                />
              </div>
              <Button 
                onClick={handleCreateArticle} 
                disabled={!newArticleTitle.trim() || isCreating}
                className="w-full"
              >
                {isCreating ? '作成中...' : '記事を作成'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Workflow Status */}
      {isWorkflowRunning && workflowStatus && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-600 animate-pulse" />
              <span>AI記事生成中...</span>
            </CardTitle>
            <CardDescription>
              「{workflowStatus.keyword}」の記事を生成しています
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>進捗状況</span>
                <span>{workflowProgress}%</span>
              </div>
              <Progress value={workflowProgress} className="h-2" />
              <div className="text-xs text-muted-foreground">
                現在のステップ: {workflowStatus.current_step}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Workflow Completed */}
      {workflowStatus?.status === 'completed' && !isWorkflowRunning && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription>
            「{workflowStatus.keyword}」の記事生成が完了しました！記事一覧をご確認ください。
          </AlertDescription>
        </Alert>
      )}

      {/* Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Edit className="h-5 w-5 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">総記事数</p>
                  <p className="text-2xl font-bold text-foreground">{analytics.total_articles}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Eye className="h-5 w-5 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">総ページビュー</p>
                  <p className="text-2xl font-bold text-foreground">{analytics.total_page_views.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">平均SEOスコア</p>
                  <p className="text-2xl font-bold text-foreground">{analytics.average_seo_score.toFixed(1)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Eye className="h-5 w-5 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">ユニークビジター</p>
                  <p className="text-2xl font-bold text-foreground">{analytics.total_unique_visitors.toLocaleString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder="記事を検索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="ステータス選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">すべてのステータス</SelectItem>
                  <SelectItem value="draft">下書き</SelectItem>
                  <SelectItem value="review">レビュー中</SelectItem>
                  <SelectItem value="published">公開済み</SelectItem>
                  <SelectItem value="archived">アーカイブ</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Articles Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>記事</TableHead>
                <TableHead>ステータス</TableHead>
                <TableHead>SEOスコア</TableHead>
                <TableHead>ページビュー</TableHead>
                <TableHead>更新日</TableHead>
                <TableHead className="text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12">
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                      <span className="ml-2">読み込み中...</span>
                    </div>
                  </TableCell>
                </TableRow>
              ) : articles.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-12 text-muted-foreground">
                    記事が見つかりません
                  </TableCell>
                </TableRow>
              ) : (
                articles.map((article) => (
                  <TableRow key={article.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div>
                        <div className="font-medium truncate max-w-xs">{article.title}</div>
                        <div className="text-sm text-muted-foreground">
                          {article.word_count}文字 • {article.reading_time}分
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(article.status)}</TableCell>
                    <TableCell>{getSEOScoreBadge(article.seo_score)}</TableCell>
                    <TableCell>{article.page_views.toLocaleString()}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(article.updated_at).toLocaleDateString('ja-JP')}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setSelectedArticle(article)}
                          className="h-8 w-8"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Edit className="h-4 w-4" />
                        </Button>
                        {article.status === 'draft' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePublish(article.id)}
                          >
                            公開
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(article.id)}
                          className="h-8 w-8 text-destructive hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          {totalItems > ITEMS_PER_PAGE && (
            <div className="flex items-center justify-between p-4 border-t">
              <div className="text-sm text-muted-foreground">
                {currentPage * ITEMS_PER_PAGE + 1} - {Math.min((currentPage + 1) * ITEMS_PER_PAGE, totalItems)} / {totalItems} 件
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                  disabled={currentPage === 0}
                >
                  前へ
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={(currentPage + 1) * ITEMS_PER_PAGE >= totalItems}
                >
                  次へ
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Article Detail Modal */}
      <Dialog open={!!selectedArticle} onOpenChange={() => setSelectedArticle(null)}>
        <DialogContent className="max-w-2xl">
          {selectedArticle && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedArticle.title}</DialogTitle>
                <DialogDescription>
                  記事の詳細情報とパフォーマンス指標
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-4 text-sm">
                  <span>{selectedArticle.word_count}文字</span>
                  <span>{selectedArticle.reading_time}分</span>
                  {getStatusBadge(selectedArticle.status)}
                  {selectedArticle.seo_score && (
                    <Badge variant="outline">
                      SEO: {getSEOScoreBadge(selectedArticle.seo_score)}
                    </Badge>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <p className="text-sm font-medium text-muted-foreground">ページビュー</p>
                      <p className="text-2xl font-bold">{selectedArticle.page_views.toLocaleString()}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <p className="text-sm font-medium text-muted-foreground">最終更新</p>
                      <p className="text-2xl font-bold">
                        {new Date(selectedArticle.updated_at).toLocaleDateString('ja-JP')}
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {selectedArticle.content && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">コンテンツプレビュー</p>
                    <Card>
                      <CardContent className="p-4 max-h-40 overflow-y-auto">
                        <p className="text-sm">
                          {selectedArticle.content.substring(0, 300)}
                          {selectedArticle.content.length > 300 && '...'}
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export { ContentManager };
export default ContentManager;