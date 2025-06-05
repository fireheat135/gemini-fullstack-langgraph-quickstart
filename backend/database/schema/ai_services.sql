-- AIサービス管理スキーマ（正規化済み）
-- AI Services Management Schema (Normalized)

-- AIプロバイダー定義（第3正規形）
CREATE TYPE ai_provider_enum AS ENUM ('gemini', 'openai', 'anthropic', 'stability_ai');
CREATE TYPE ai_model_type_enum AS ENUM ('text_generation', 'image_generation', 'text_analysis', 'code_generation');
CREATE TYPE generation_status_enum AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'cancelled');

-- AIプロバイダー基本情報
CREATE TABLE ai_providers (
    id SERIAL PRIMARY KEY,
    name ai_provider_enum UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    api_endpoint VARCHAR(500) NOT NULL,
    documentation_url VARCHAR(500),
    supported_models TEXT[] NOT NULL,
    rate_limits JSONB NOT NULL,
    pricing JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ユーザーAPIキー管理（暗号化保存）
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_id INTEGER NOT NULL REFERENCES ai_providers(id),
    encrypted_key BYTEA NOT NULL, -- 暗号化されたAPIキー
    key_name VARCHAR(100), -- ユーザーが設定する識別名
    daily_limit INTEGER DEFAULT 1000,
    monthly_limit INTEGER DEFAULT 30000,
    cost_limit_per_month DECIMAL(10,2) DEFAULT 100.00,
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- 複合制約
    UNIQUE (user_id, provider_id),
    
    -- チェック制約
    CONSTRAINT positive_limits CHECK (
        daily_limit > 0 AND 
        monthly_limit > 0 AND 
        cost_limit_per_month > 0
    )
);

-- AI生成リクエスト履歴
CREATE TABLE ai_generation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key_id UUID REFERENCES user_api_keys(id) ON DELETE SET NULL,
    provider ai_provider_enum NOT NULL,
    model_type ai_model_type_enum NOT NULL,
    model_name VARCHAR(100),
    prompt TEXT NOT NULL,
    parameters JSONB,
    status generation_status_enum DEFAULT 'pending',
    
    -- 結果データ
    generated_content TEXT,
    tokens_used INTEGER,
    cost DECIMAL(10,4),
    generation_time_seconds DECIMAL(8,3),
    
    -- メタデータ
    request_metadata JSONB,
    response_metadata JSONB,
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- タイムスタンプ
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- インデックス用カラム
    request_date DATE GENERATED ALWAYS AS (DATE(requested_at)) STORED
);

-- API使用統計（日次集計）
CREATE TABLE api_usage_daily_stats (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider ai_provider_enum NOT NULL,
    usage_date DATE NOT NULL,
    
    -- カウント統計
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    
    -- 使用量統計
    total_tokens_used INTEGER DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0,
    
    -- パフォーマンス統計
    average_response_time DECIMAL(8,3),
    min_response_time DECIMAL(8,3),
    max_response_time DECIMAL(8,3),
    
    -- 更新タイムスタンプ
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 複合主キー
    UNIQUE (user_id, provider, usage_date)
);

-- プロバイダー別機能設定
CREATE TABLE provider_capabilities (
    provider_id INTEGER PRIMARY KEY REFERENCES ai_providers(id),
    max_tokens_per_request INTEGER NOT NULL,
    supports_streaming BOOLEAN DEFAULT false,
    supports_function_calling BOOLEAN DEFAULT false,
    supports_image_input BOOLEAN DEFAULT false,
    supports_image_output BOOLEAN DEFAULT false,
    supports_audio_input BOOLEAN DEFAULT false,
    supports_audio_output BOOLEAN DEFAULT false,
    context_window_size INTEGER,
    available_models JSONB NOT NULL,
    model_parameters JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API レート制限追跡
CREATE TABLE rate_limit_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider ai_provider_enum NOT NULL,
    time_window_start TIMESTAMP NOT NULL,
    time_window_end TIMESTAMP NOT NULL,
    requests_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    cost_incurred DECIMAL(10,4) DEFAULT 0,
    
    -- 制約
    CONSTRAINT rate_limit_window_check CHECK (time_window_end > time_window_start)
);

-- AI生成キューイングシステム
CREATE TABLE generation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    request_id UUID REFERENCES ai_generation_requests(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    retry_after TIMESTAMP,
    status generation_status_enum DEFAULT 'pending',
    worker_id VARCHAR(100),
    processing_started_at TIMESTAMP,
    
    -- インデックス
    INDEX idx_queue_status_priority (status, priority DESC, scheduled_at)
);

-- プロバイダー健全性監視
CREATE TABLE provider_health_checks (
    id SERIAL PRIMARY KEY,
    provider ai_provider_enum NOT NULL,
    endpoint_url VARCHAR(500) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    is_healthy BOOLEAN DEFAULT false,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- インデックス
    INDEX idx_health_checks_provider_time (provider, checked_at DESC)
);

-- インデックス作成
CREATE INDEX idx_user_api_keys_user_provider ON user_api_keys(user_id, provider_id);
CREATE INDEX idx_user_api_keys_active ON user_api_keys(is_active) WHERE is_active = true;

CREATE INDEX idx_generation_requests_user_date ON ai_generation_requests(user_id, request_date DESC);
CREATE INDEX idx_generation_requests_provider_status ON ai_generation_requests(provider, status);
CREATE INDEX idx_generation_requests_status_requested ON ai_generation_requests(status, requested_at DESC);

CREATE INDEX idx_daily_stats_user_date ON api_usage_daily_stats(user_id, usage_date DESC);
CREATE INDEX idx_daily_stats_provider_date ON api_usage_daily_stats(provider, usage_date DESC);

CREATE INDEX idx_rate_limit_user_provider_window ON rate_limit_tracking(user_id, provider, time_window_start);

-- トリガー（統計更新）
CREATE OR REPLACE FUNCTION update_daily_stats()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO api_usage_daily_stats (
        user_id, provider, usage_date, 
        total_requests, successful_requests, failed_requests,
        total_tokens_used, total_cost
    ) VALUES (
        NEW.user_id, NEW.provider, DATE(NEW.completed_at),
        1, 
        CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END,
        COALESCE(NEW.tokens_used, 0),
        COALESCE(NEW.cost, 0)
    )
    ON CONFLICT (user_id, provider, usage_date) 
    DO UPDATE SET
        total_requests = api_usage_daily_stats.total_requests + 1,
        successful_requests = api_usage_daily_stats.successful_requests + 
            CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
        failed_requests = api_usage_daily_stats.failed_requests + 
            CASE WHEN NEW.status = 'failed' THEN 1 ELSE 0 END,
        total_tokens_used = api_usage_daily_stats.total_tokens_used + COALESCE(NEW.tokens_used, 0),
        total_cost = api_usage_daily_stats.total_cost + COALESCE(NEW.cost, 0),
        last_updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_daily_stats
    AFTER UPDATE OF status ON ai_generation_requests
    FOR EACH ROW
    WHEN (NEW.status IN ('completed', 'failed') AND OLD.status != NEW.status)
    EXECUTE FUNCTION update_daily_stats();

-- 初期データ挿入
INSERT INTO ai_providers (name, display_name, api_endpoint, supported_models, rate_limits, pricing) VALUES
('gemini', 'Google Gemini', 'https://generativelanguage.googleapis.com/v1', 
 ARRAY['gemini-pro', 'gemini-pro-vision'], 
 '{"requests_per_minute": 60, "tokens_per_minute": 32000}',
 '{"text_generation": 0.002, "image_analysis": 0.0025}'),
('openai', 'OpenAI', 'https://api.openai.com/v1',
 ARRAY['gpt-4', 'gpt-3.5-turbo', 'dall-e-3'],
 '{"requests_per_minute": 500, "tokens_per_minute": 150000}',
 '{"text_generation": 0.03, "image_generation": 0.04}'),
('anthropic', 'Anthropic Claude', 'https://api.anthropic.com/v1',
 ARRAY['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
 '{"requests_per_minute": 100, "tokens_per_minute": 40000}',
 '{"text_generation": 0.015, "text_analysis": 0.015}'),
('stability_ai', 'Stability AI', 'https://api.stability.ai/v1',
 ARRAY['stable-diffusion-xl', 'stable-diffusion-3'],
 '{"requests_per_minute": 150, "images_per_minute": 30}',
 '{"image_generation": 0.01, "image_editing": 0.015}');

-- プロバイダー機能設定
INSERT INTO provider_capabilities (provider_id, max_tokens_per_request, supports_streaming, supports_function_calling, supports_image_input, supports_image_output, context_window_size, available_models) 
SELECT 
    id, 
    CASE name 
        WHEN 'gemini' THEN 30720
        WHEN 'openai' THEN 128000 
        WHEN 'anthropic' THEN 200000
        WHEN 'stability_ai' THEN 1024
    END,
    CASE name WHEN 'openai' THEN true WHEN 'anthropic' THEN true ELSE false END,
    CASE name WHEN 'openai' THEN true WHEN 'gemini' THEN true ELSE false END,
    CASE name WHEN 'gemini' THEN true WHEN 'openai' THEN true ELSE false END,
    CASE name WHEN 'stability_ai' THEN true WHEN 'openai' THEN true ELSE false END,
    CASE name 
        WHEN 'gemini' THEN 30720
        WHEN 'openai' THEN 128000 
        WHEN 'anthropic' THEN 200000
        WHEN 'stability_ai' THEN 77
    END,
    '{"models": ["default"]}' -- 簡易版、実際にはより詳細な設定
FROM ai_providers;