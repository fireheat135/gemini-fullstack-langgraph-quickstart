// API client for Scrib AI backend
const API_BASE_URL = import.meta.env.PROD 
  ? import.meta.env.VITE_PRODUCTION_API_URL || 'https://scrib-ai-writing-superpowers-263183603168.us-west1.run.app'
  : import.meta.env.VITE_API_BASE_URL || 'http://localhost:8123';

interface APIError {
  detail?: string;
  message?: string;
  errors?: { [key: string]: string[] };
}

class APIClient {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('auth_token');
  }

  private getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }

  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  async get<T>(endpoint: string): Promise<{ data: T }> {
    return this.request(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any, options?: Partial<RequestInit>): Promise<{ data: T }> {
    return this.request(endpoint, { 
      method: 'POST', 
      body: data instanceof FormData ? data : JSON.stringify(data),
      ...options
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<{ data: T }> {
    return this.request(endpoint, { 
      method: 'PUT', 
      body: JSON.stringify(data) 
    });
  }

  async delete<T>(endpoint: string): Promise<{ data: T }> {
    return this.request(endpoint, { method: 'DELETE' });
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<{ data: T }> {
    // If using demo token, return mock data for certain endpoints
    const token = this.getToken();
    if (token === 'demo-token-for-ui-testing') {
      return this.getMockResponse<T>(endpoint, options);
    }

    const url = `${API_BASE_URL}${endpoint}`;
    const defaultHeaders = this.getHeaders();
    const headers = options.body instanceof FormData 
      ? Object.fromEntries(Object.entries(defaultHeaders).filter(([key]) => key !== 'Content-Type'))
      : defaultHeaders;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorData: APIError = {};
        try {
          errorData = await response.json();
        } catch {
          // If JSON parsing fails, use status text
        }

        // Handle specific error types
        if (response.status === 401) {
          this.clearToken();
          throw new Error('認証が必要です。ログインしてください。');
        }

        if (response.status === 403) {
          throw new Error('この操作を実行する権限がありません。');
        }

        if (response.status === 404) {
          throw new Error('リソースが見つかりません。');
        }

        if (response.status === 422) {
          // Validation errors
          const validationErrors = errorData.errors;
          if (validationErrors) {
            const errorMessages = Object.entries(validationErrors)
              .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
              .join('\n');
            throw new Error(errorMessages);
          }
        }

        const errorMessage = errorData.detail || errorData.message || 
          `サーバーエラーが発生しました (HTTP ${response.status})`;
        throw new Error(errorMessage);
      }

      const result = await response.json();
      return { data: result };
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('サーバーに接続できません。ネットワーク接続を確認してください。');
      }
      throw error;
    }
  }

  private getMockResponse<T>(endpoint: string, options: RequestInit = {}): Promise<{ data: T }> {
    // Return mock data for demo mode
    console.log('[Demo Mode] Mock API call:', endpoint, options);
    
    // Mock responses for different endpoints
    if (endpoint === '/api/v1/users/me') {
      return Promise.resolve({
        data: {
          id: 999,
          email: 'demo@example.com',
          full_name: 'デモユーザー',
          is_active: true,
          created_at: new Date().toISOString()
        } as T
      });
    }

    if (endpoint.startsWith('/api/v1/seo-workflow/start')) {
      return Promise.resolve({
        data: {
          session_id: 'demo-session-' + Date.now(),
          status: 'started',
          message: 'SEOワークフローを開始しました（デモモード）'
        } as T
      });
    }

    if (endpoint.includes('/api/v1/seo-workflow/status/')) {
      return Promise.resolve({
        data: {
          status: 'completed',
          current_step: 7,
          total_steps: 7,
          steps_completed: ['keyword_analysis', 'competitor_research', 'content_planning', 'heading_generation', 'approval', 'content_generation', 'finalization'],
          message: 'ワークフローが完了しました（デモモード）',
          results: {
            keyword_analysis: { 
              keyword: 'デモキーワード',
              search_volume: 1000,
              difficulty: 'medium'
            },
            competitor_research: {
              competitors: ['競合A', '競合B', '競合C']
            },
            content_planning: {
              target_audience: 'デモターゲット',
              content_type: 'blog_post'
            },
            headings: [
              { level: 1, text: 'デモ記事のタイトル' },
              { level: 2, text: 'セクション1: はじめに' },
              { level: 2, text: 'セクション2: 主要なポイント' },
              { level: 2, text: 'セクション3: まとめ' }
            ],
            content: {
              title: 'デモ記事のタイトル',
              body: 'これはデモモードで生成されたコンテンツです。実際のAPIを使用すると、AIが生成した高品質なSEOコンテンツがここに表示されます。',
              meta_description: 'デモ記事のメタディスクリプション',
              keywords: ['デモ', 'キーワード', 'SEO']
            }
          }
        } as T
      });
    }

    // Mock responses for keyword analysis
    if (endpoint === '/api/v1/keywords/analyze') {
      return Promise.resolve({
        data: {
          keyword: 'デモキーワード',
          search_volume: 1500,
          difficulty: 'medium',
          cpc: 250,
          competition: 0.65,
          trends: [
            { date: '2024-01', volume: 1200 },
            { date: '2024-02', volume: 1300 },
            { date: '2024-03', volume: 1500 }
          ],
          related_keywords: ['関連キーワード1', '関連キーワード2', '関連キーワード3']
        } as T
      });
    }

    // Mock responses for content articles
    if (endpoint.includes('/api/v1/content/articles')) {
      return Promise.resolve({
        data: {
          items: [
            {
              id: '1',
              title: 'デモ記事1',
              content: 'これはデモモードの記事です。',
              status: 'published',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            },
            {
              id: '2',
              title: 'デモ記事2',
              content: 'これもデモモードの記事です。',
              status: 'draft',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            }
          ],
          total: 2,
          page: 1,
          pages: 1
        } as T
      });
    }

    // Mock response for analytics
    if (endpoint.includes('/api/v1/analytics')) {
      return Promise.resolve({
        data: {
          total_articles: 10,
          total_views: 5000,
          average_reading_time: 4.5,
          engagement_rate: 0.75,
          top_keywords: ['キーワード1', 'キーワード2', 'キーワード3'],
          performance_trend: [
            { date: '2024-01', views: 1000 },
            { date: '2024-02', views: 1500 },
            { date: '2024-03', views: 2500 }
          ]
        } as T
      });
    }

    // Mock response for API keys
    if (endpoint === '/api/v1/api-keys') {
      return Promise.resolve({
        data: [
          {
            id: '1',
            name: 'Gemini API Key (Demo)',
            provider: 'gemini',
            is_active: true,
            created_at: new Date().toISOString(),
            usage_count: 100,
            daily_limit: 1000,
            monthly_limit: 30000
          }
        ] as T
      });
    }

    // Default mock response
    return Promise.resolve({
      data: {
        success: true,
        message: 'デモモードでの操作です'
      } as T
    });
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const data = new FormData();
    data.append('username', email);
    data.append('password', password);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        body: data,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'ログインに失敗しました');
      }
      
      const result = await response.json();
      this.setToken(result.access_token);
      return result;
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('サーバーに接続できません。ネットワーク接続を確認してください。');
      }
      throw error;
    }
  }

  async register(email: string, password: string, name: string) {
    try {
      const response = await this.post('/api/v1/auth/register', { 
        email, 
        password, 
        name: name 
      });
      return response;
    } catch (error) {
      throw error;
    }
  }

  async getCurrentUser() {
    return this.get('/api/v1/users/me');
  }

  async logout() {
    this.clearToken();
  }

  // Google OAuth2 endpoints
  async getGoogleAuthUrl() {
    return this.get('/api/v1/auth/google');
  }

  async handleGoogleCallback(code: string, state: string) {
    return this.get(`/api/v1/auth/google/callback?code=${code}&state=${state}`);
  }

  // Keywords endpoints
  async analyzeKeyword(keyword: string, includeTrends = true) {
    return this.post('/api/v1/keywords/analyze', { 
      keyword, 
      include_trends: includeTrends 
    });
  }

  async bulkAnalyzeKeywords(keywords: string[]) {
    return this.post('/api/v1/keywords/analyze/bulk', { keywords });
  }

  async getKeywordTrends(keyword: string, days = 30) {
    return this.post('/api/v1/keywords/trends', { keyword, days });
  }

  async analyzeCompetitors(keyword: string, limit = 10) {
    return this.post('/api/v1/keywords/competitors', { keyword, limit });
  }

  async clusterKeywords(keywords: string[]) {
    return this.post('/api/v1/keywords/cluster', { keywords });
  }

  async suggestKeywords(seedKeyword: string, count = 20) {
    return this.post('/api/v1/keywords/suggest', { 
      seed_keyword: seedKeyword, 
      count 
    });
  }

  // Content endpoints
  async getArticles(page = 1, limit = 20) {
    return this.get(`/api/v1/content/articles?page=${page}&limit=${limit}`);
  }

  async createArticle(article: {
    title: string;
    content: string;
    content_type: string;
    tags?: string[];
    meta_description?: string;
    keywords?: string[];
  }) {
    return this.post('/api/v1/content/articles', article);
  }

  async getArticle(id: string) {
    return this.get(`/api/v1/content/articles/${id}`);
  }

  async updateArticle(id: string, updates: any) {
    return this.put(`/api/v1/content/articles/${id}`, updates);
  }

  async deleteArticle(id: string) {
    return this.delete(`/api/v1/content/articles/${id}`);
  }

  async publishArticle(id: string, metadata: any = {}) {
    return this.post(`/api/v1/content/articles/${id}/publish`, metadata);
  }

  async duplicateArticle(id: string) {
    return this.post(`/api/v1/content/articles/${id}/duplicate`);
  }

  // SEO Research endpoints
  async startSeoResearch(keyword: string, effort: 'low' | 'medium' | 'high' = 'medium') {
    return this.post('/api/v1/seo-research/start', { keyword, effort });
  }

  async getSeoResearchStatus(sessionId: string) {
    return this.get(`/api/v1/seo-research/status/${sessionId}`);
  }

  async getSeoResearchResults(sessionId: string) {
    return this.get(`/api/v1/seo-research/results/${sessionId}`);
  }

  async getSeoResearchHistory(page = 1, limit = 20) {
    return this.get(`/api/v1/seo-research/history?page=${page}&limit=${limit}`);
  }

  async quickSeoAnalysis(keyword: string) {
    return this.post('/api/v1/seo-research/quick-analysis', { keyword });
  }

  // Analytics endpoints
  async getAnalyticsSummary(timeRange = '30d') {
    return this.get(`/api/v1/analytics/summary?time_range=${timeRange}`);
  }

  async getAnalyticsTrends(timeRange = '30d') {
    return this.get(`/api/v1/analytics/trends?time_range=${timeRange}`);
  }

  async getKeywordPerformance(timeRange = '30d') {
    return this.get(`/api/v1/analytics/keywords?time_range=${timeRange}`);
  }

  async getContentPerformance(timeRange = '30d') {
    return this.get(`/api/v1/analytics/content-performance?time_range=${timeRange}`);
  }

  async getEngagementMetrics(timeRange = '30d') {
    return this.get(`/api/v1/analytics/engagement?time_range=${timeRange}`);
  }

  async getConversionMetrics(timeRange = '30d') {
    return this.get(`/api/v1/analytics/conversions?time_range=${timeRange}`);
  }

  async compareAnalytics(periodA: string, periodB: string) {
    return this.get(`/api/v1/analytics/compare?period_a=${periodA}&period_b=${periodB}`);
  }

  async exportAnalytics(format: 'csv' | 'excel' | 'pdf' = 'csv', timeRange = '30d') {
    return this.get(`/api/v1/analytics/export?format=${format}&time_range=${timeRange}`);
  }

  // API Keys endpoints
  async getApiKeys() {
    return this.get('/api/v1/api-keys');
  }

  async createApiKey(data: {
    name: string;
    provider: string;
    api_key: string;
    daily_limit?: number;
    monthly_limit?: number;
  }) {
    return this.post('/api/v1/api-keys', data);
  }

  async updateApiKey(id: string, updates: any) {
    return this.put(`/api/v1/api-keys/${id}`, updates);
  }

  async deleteApiKey(id: string) {
    return this.delete(`/api/v1/api-keys/${id}`);
  }

  async testApiKey(id: string) {
    return this.post(`/api/v1/api-keys/${id}/test`);
  }

  // SEO Workflow endpoints
  async startSeoWorkflow(request: {
    keyword: string;
    target_audience?: string;
    content_type?: string;
    workflow_mode?: string;
    use_real_data?: boolean;
  }) {
    return this.post('/api/v1/seo-workflow/start', request);
  }

  async getSeoWorkflowStatus(sessionId: string) {
    return this.get(`/api/v1/seo-workflow/status/${sessionId}`);
  }

  async approveSeoWorkflowHeadings(request: {
    session_id: string;
    approved_headings: any[];
    modifications?: any;
  }) {
    return this.post('/api/v1/seo-workflow/approve-headings', request);
  }

  async getSeoWorkflowResults(sessionId: string) {
    return this.get(`/api/v1/seo-workflow/results/${sessionId}`);
  }

  // Content Generation endpoints  
  async generateContent(request: {
    selected_pattern: any;
    article_outline: any;
    research_data: any;
  }) {
    return this.post('/api/v1/writing/generate-content', request);
  }

  async generatePlanningPatterns(request: {
    keyword: string;
    research_data: any;
  }) {
    return this.post('/api/v1/planning/generate-patterns', request);
  }

  async editContent(request: {
    content: string;
    instruction: string;
    selected_range?: { start: number; end: number };
  }) {
    return this.post('/api/v1/editing/suggest', request);
  }
}

export const apiClient = new APIClient();
export default apiClient;
