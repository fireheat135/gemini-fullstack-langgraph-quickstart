import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { InputForm } from "./InputForm";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sparkles, Zap, ArrowRight } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/components/auth/AuthContext";

interface WelcomeScreenProps {
  handleSubmit?: (
    submittedInputValue: string,
    effort: string,
    model: string
  ) => void;
  onCancel?: () => void;
  isLoading?: boolean;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
}) => {
  const navigate = useNavigate();
  const { skipAuth } = useAuth();

  // Handle OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');
    
    if (token) {
      // Store token and redirect to dashboard
      apiClient.setToken(token);
      navigate('/dashboard');
    } else if (error) {
      // Show error message
      console.error('OAuth error:', urlParams.get('message'));
      alert('ログインエラーが発生しました: ' + urlParams.get('message'));
    }
  }, [navigate]);

  return (
  <div className="flex flex-col items-center justify-center text-center px-4 flex-1 w-full max-w-4xl mx-auto gap-8 py-12">
    <div className="space-y-4">
      <div className="flex items-center justify-center gap-2 mb-4">
        <Sparkles className="h-12 w-12 text-primary" />
        <h1 className="text-5xl md:text-6xl font-bold text-foreground">
          Scriv
        </h1>
      </div>
      <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl">
        AI駆動のSEOコンテンツ制作プラットフォーム
      </p>
      <div className="flex items-center justify-center gap-2 mt-4">
        <Badge variant="secondary" className="text-sm">
          <Zap className="h-3 w-3 mr-1" />
          LangGraph Powered
        </Badge>
        <Badge variant="outline" className="text-sm">
          Multi-AI Integration
        </Badge>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
      <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/keyword-research')}>
        <CardContent className="p-6 text-center">
          <div className="text-2xl mb-2">🔍</div>
          <h3 className="font-semibold mb-2">キーワード分析</h3>
          <p className="text-sm text-muted-foreground">
            AIによる包括的なキーワードリサーチとトレンド分析
          </p>
        </CardContent>
      </Card>

      <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/seo-workflow')}>
        <CardContent className="p-6 text-center">
          <div className="text-2xl mb-2">⚡</div>
          <h3 className="font-semibold mb-2">SEO施策</h3>
          <p className="text-sm text-muted-foreground">
            LangGraphワークフローによる自動化されたSEO最適化
          </p>
        </CardContent>
      </Card>

      <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/analytics')}>
        <CardContent className="p-6 text-center">
          <div className="text-2xl mb-2">📊</div>
          <h3 className="font-semibold mb-2">分析レポート</h3>
          <p className="text-sm text-muted-foreground">
            高度な統計分析とパフォーマンストラッキング
          </p>
        </CardContent>
      </Card>
    </div>

    <div className="flex flex-col sm:flex-row gap-4 mt-8">
      <Button onClick={() => navigate('/dashboard')} size="lg" className="flex items-center gap-2">
        ダッシュボードを開く
        <ArrowRight className="h-4 w-4" />
      </Button>
      <Button onClick={() => navigate('/keyword-research')} variant="outline" size="lg">
        キーワード研究を開始
      </Button>
      <Button 
        onClick={async () => {
          // Use skipAuth from context to connect to real backend
          await skipAuth();
          navigate('/dashboard');
        }} 
        variant="secondary" 
        size="lg" 
        className="flex items-center gap-2"
      >
        <Zap className="h-4 w-4" />
        ログインスキップしてUIを体験
      </Button>
    </div>

    {handleSubmit && (
      <div className="w-full max-w-2xl mt-8">
        <InputForm
          onSubmit={handleSubmit}
          isLoading={isLoading || false}
          onCancel={onCancel || (() => {})}
          hasHistory={false}
        />
      </div>
    )}

    <p className="text-xs text-muted-foreground">
      Powered by Google Gemini, OpenAI, and Anthropic Claude
    </p>
  </div>
  );
};
