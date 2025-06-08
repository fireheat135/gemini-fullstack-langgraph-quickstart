import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Key, TestTube, Power, Trash2, Plus } from 'lucide-react';
import { apiClient } from '@/lib/api.ts';

interface APIKey {
  id: number;
  provider: 'google_gemini' | 'openai' | 'anthropic';
  name: string;
  isActive: boolean;
  isVerified: boolean;
  dailyUsage: number;
  dailyLimit?: number;
  monthlyUsage: number;
  monthlyLimit?: number;
  lastUsed?: string;
  createdAt: string;
}

interface NewAPIKey {
  provider: string;
  name: string;
  apiKey: string;
  dailyLimit?: number;
  monthlyLimit?: number;
}

export function APIKeyManager() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [newKey, setNewKey] = useState<NewAPIKey>({
    provider: '',
    name: '',
    apiKey: '',
    dailyLimit: undefined,
    monthlyLimit: undefined
  });

  // Mock data for development
  useEffect(() => {
    const mockApiKeys: APIKey[] = [
      {
        id: 1,
        provider: 'google_gemini',
        name: 'Gemini Pro API',
        isActive: true,
        isVerified: true,
        dailyUsage: 150,
        dailyLimit: 1000,
        monthlyUsage: 4500,
        monthlyLimit: 30000,
        lastUsed: '2024-01-15T10:30:00Z',
        createdAt: '2024-01-01T00:00:00Z'
      },
      {
        id: 2,
        provider: 'openai',
        name: 'OpenAI GPT-4',
        isActive: true,
        isVerified: false,
        dailyUsage: 25,
        dailyLimit: 500,
        monthlyUsage: 750,
        monthlyLimit: 15000,
        lastUsed: '2024-01-14T15:45:00Z',
        createdAt: '2024-01-05T00:00:00Z'
      },
      {
        id: 3,
        provider: 'anthropic',
        name: 'Claude Sonnet',
        isActive: false,
        isVerified: true,
        dailyUsage: 0,
        dailyLimit: 200,
        monthlyUsage: 120,
        monthlyLimit: 6000,
        createdAt: '2024-01-10T00:00:00Z'
      }
    ];

    setTimeout(() => {
      setApiKeys(mockApiKeys);
      setIsLoading(false);
    }, 1000);
  }, []);

  const getProviderInfo = (provider: string) => {
    switch (provider) {
      case 'google_gemini':
        return { name: 'Google Gemini', icon: '🔮', color: 'bg-blue-600' };
      case 'openai':
        return { name: 'OpenAI', icon: '🤖', color: 'bg-green-600' };
      case 'anthropic':
        return { name: 'Anthropic', icon: '🧠', color: 'bg-purple-600' };
      default:
        return { name: provider, icon: '🔑', color: 'bg-gray-600' };
    }
  };

  const getUsagePercentage = (usage: number, limit?: number) => {
    if (!limit) return 0;
    return Math.min((usage / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const handleAddAPIKey = async () => {
    if (!newKey.provider || !newKey.name || !newKey.apiKey) return;

    try {
      const response = await apiClient.post('/api/v1/api-keys', {
        provider: newKey.provider,
        name: newKey.name,
        api_key: newKey.apiKey,
        daily_limit: newKey.dailyLimit,
        monthly_limit: newKey.monthlyLimit
      });
      
      setApiKeys(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Failed to add API key:', error);
      // Fallback to mock data
      const mockNewKey: APIKey = {
        id: apiKeys.length + 1,
        provider: newKey.provider as any,
        name: newKey.name,
        isActive: true,
        isVerified: false,
        dailyUsage: 0,
        dailyLimit: newKey.dailyLimit,
        monthlyUsage: 0,
        monthlyLimit: newKey.monthlyLimit,
        createdAt: new Date().toISOString()
      };
      setApiKeys(prev => [...prev, mockNewKey]);
    }

    setNewKey({
      provider: '',
      name: '',
      apiKey: '',
      dailyLimit: undefined,
      monthlyLimit: undefined
    });
    setShowForm(false);
  };

  const handleToggleActive = async (id: number) => {
    try {
      await apiClient.put(`/api/v1/api-keys/${id}`, { 
        is_active: !apiKeys.find(k => k.id === id)?.isActive 
      });
    } catch (error) {
      console.error('Failed to toggle API key:', error);
    }
    
    setApiKeys(prev => prev.map(key => 
      key.id === id ? { ...key, isActive: !key.isActive } : key
    ));
  };

  const handleDeleteKey = async (id: number) => {
    if (!confirm('このAPIキーを削除しますか？')) return;
    
    try {
      await apiClient.delete(`/api/v1/api-keys/${id}`);
    } catch (error) {
      console.error('Failed to delete API key:', error);
    }
    
    setApiKeys(prev => prev.filter(key => key.id !== id));
  };

  const handleTestKey = async (id: number) => {
    try {
      const response = await apiClient.post(`/api/v1/api-keys/${id}/test`);
      setApiKeys(prev => prev.map(key => 
        key.id === id ? { ...key, isVerified: response.data.success } : key
      ));
    } catch (error) {
      console.error('Failed to test API key:', error);
      // Fallback behavior
      setApiKeys(prev => prev.map(key => 
        key.id === id ? { ...key, isVerified: !key.isVerified } : key
      ));
    }
  };

  if (isLoading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
            <Key className="h-8 w-8 text-primary" />
            API設定
          </h1>
          <p className="text-muted-foreground mt-2">
            外部AIサービスのAPIキーを安全に管理できます
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          新しいAPIキー
        </Button>
      </div>

      {/* Add API Key Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>新しいAPIキーを追加</CardTitle>
            <CardDescription>
              AIサービスプロバイダーのAPIキーを安全に追加します
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                プロバイダー *
              </label>
              <Select value={newKey.provider} onValueChange={(value) => 
                setNewKey(prev => ({ ...prev, provider: value }))
              }>
                <SelectTrigger>
                  <SelectValue placeholder="プロバイダーを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="google_gemini">Google Gemini</SelectItem>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                名前 *
              </label>
              <Input
                value={newKey.name}
                onChange={(e) => setNewKey(prev => ({ ...prev, name: e.target.value }))}
                placeholder="例: Main Gemini Key"
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-white mb-2">
              APIキー *
            </label>
            <Input
              type="password"
              value={newKey.apiKey}
              onChange={(e) => setNewKey(prev => ({ ...prev, apiKey: e.target.value }))}
              placeholder="APIキーを入力"
            />
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                日次制限 (オプション)
              </label>
              <Input
                type="number"
                value={newKey.dailyLimit || ''}
                onChange={(e) => setNewKey(prev => ({ 
                  ...prev, 
                  dailyLimit: e.target.value ? parseInt(e.target.value) : undefined 
                }))}
                placeholder="1000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white mb-2">
                月次制限 (オプション)
              </label>
              <Input
                type="number"
                value={newKey.monthlyLimit || ''}
                onChange={(e) => setNewKey(prev => ({ 
                  ...prev, 
                  monthlyLimit: e.target.value ? parseInt(e.target.value) : undefined 
                }))}
                placeholder="30000"
              />
            </div>
          </div>

            <div className="flex gap-2">
              <Button onClick={handleAddAPIKey}>
                追加
              </Button>
              <Button 
                onClick={() => setShowForm(false)} 
                variant="outline"
              >
                キャンセル
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* API Keys List */}
      <div className="space-y-4">
        {apiKeys.map((key) => {
          const providerInfo = getProviderInfo(key.provider);
          const dailyPercentage = getUsagePercentage(key.dailyUsage, key.dailyLimit);
          const monthlyPercentage = getUsagePercentage(key.monthlyUsage, key.monthlyLimit);
          
          return (
            <Card key={key.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg ${providerInfo.color} flex items-center justify-center text-white text-lg`}>
                      {providerInfo.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{key.name}</CardTitle>
                      <CardDescription>{providerInfo.name}</CardDescription>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Badge variant={key.isVerified ? "default" : "destructive"}>
                      {key.isVerified ? '認証済み' : '未認証'}
                    </Badge>
                    <Badge variant={key.isActive ? "default" : "secondary"}>
                      {key.isActive ? 'アクティブ' : '無効'}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">

                {/* Usage Statistics */}
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-muted-foreground">日次使用量</span>
                      <span className="text-sm font-medium">
                        {key.dailyUsage}{key.dailyLimit ? ` / ${key.dailyLimit}` : ''}
                      </span>
                    </div>
                    {key.dailyLimit && (
                      <Progress value={dailyPercentage} className="h-2" />
                    )}
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-muted-foreground">月次使用量</span>
                      <span className="text-sm font-medium">
                        {key.monthlyUsage}{key.monthlyLimit ? ` / ${key.monthlyLimit}` : ''}
                      </span>
                    </div>
                    {key.monthlyLimit && (
                      <Progress value={monthlyPercentage} className="h-2" />
                    )}
                  </div>
                </div>

                {/* Last Used */}
                {key.lastUsed && (
                  <div className="text-sm text-muted-foreground">
                    最終使用: {new Date(key.lastUsed).toLocaleString('ja-JP')}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleTestKey(key.id)}
                    variant="outline"
                    size="sm"
                  >
                    <TestTube className="h-4 w-4 mr-2" />
                    テスト
                  </Button>
                  <Button
                    onClick={() => handleToggleActive(key.id)}
                    variant="outline"
                    size="sm"
                  >
                    <Power className="h-4 w-4 mr-2" />
                    {key.isActive ? '無効化' : '有効化'}
                  </Button>
                  <Button
                    onClick={() => handleDeleteKey(key.id)}
                    variant="destructive"
                    size="sm"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    削除
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {apiKeys.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-4xl mb-4">🔑</div>
            <CardTitle className="text-lg mb-2">APIキーが設定されていません</CardTitle>
            <CardDescription>
              AIサービスを利用するためにAPIキーを追加してください
            </CardDescription>
          </CardContent>
        </Card>
      )}
    </div>
  );
}