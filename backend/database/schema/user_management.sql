-- ユーザー管理スキーマ（正規化済み）
-- User Management Schema (Normalized)

-- ユーザー基本情報（第1正規形）
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- インデックス
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- ユーザープロフィール情報（第2正規形）
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(200),
    bio TEXT,
    website VARCHAR(500),
    timezone VARCHAR(50) DEFAULT 'UTC',
    avatar_url VARCHAR(500),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT user_profiles_website_format CHECK (
        website IS NULL OR website ~* '^https?://[^\s/$.?#].[^\s]*$'
    )
);

-- ユーザーロール定義（第3正規形）
CREATE TYPE user_role_enum AS ENUM ('admin', 'editor', 'author', 'viewer');

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role user_role_enum NOT NULL,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    PRIMARY KEY (user_id, role)
);

-- サブスクリプション層定義
CREATE TYPE subscription_tier_enum AS ENUM ('free', 'basic', 'premium', 'enterprise');

CREATE TABLE subscription_tiers (
    tier subscription_tier_enum PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    monthly_price DECIMAL(10,2),
    yearly_price DECIMAL(10,2),
    features JSONB NOT NULL,
    usage_limits JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true
);

-- ユーザーサブスクリプション
CREATE TABLE user_subscriptions (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    tier subscription_tier_enum NOT NULL REFERENCES subscription_tiers(tier),
    is_active BOOLEAN DEFAULT true,
    starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT true,
    billing_email VARCHAR(255),
    payment_method_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ユーザー使用統計（時系列データ）
CREATE TABLE user_usage_statistics (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    articles_created INTEGER DEFAULT 0,
    meta_descriptions_generated INTEGER DEFAULT 0,
    images_generated INTEGER DEFAULT 0,
    api_calls_made INTEGER DEFAULT 0,
    storage_used_mb DECIMAL(10,2) DEFAULT 0,
    tokens_consumed INTEGER DEFAULT 0,
    cost_incurred DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT usage_stats_period_check CHECK (period_end > period_start),
    CONSTRAINT usage_stats_positive_values CHECK (
        articles_created >= 0 AND 
        meta_descriptions_generated >= 0 AND 
        images_generated >= 0 AND 
        api_calls_made >= 0 AND 
        storage_used_mb >= 0 AND 
        tokens_consumed >= 0 AND 
        cost_incurred >= 0
    )
);

-- 認証プロバイダー（OAuth等）
CREATE TYPE auth_provider_enum AS ENUM ('email', 'google', 'github', 'microsoft');

CREATE TABLE user_auth_providers (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider auth_provider_enum NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    provider_email VARCHAR(255),
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (user_id, provider),
    UNIQUE (provider, provider_user_id)
);

-- インデックス作成
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_user_subscriptions_tier ON user_subscriptions(tier);
CREATE INDEX idx_user_subscriptions_active ON user_subscriptions(is_active) WHERE is_active = true;
CREATE INDEX idx_usage_stats_user_period ON user_usage_statistics(user_id, period_start, period_end);

-- トリガー（更新時刻の自動更新）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_subscriptions_updated_at 
    BEFORE UPDATE ON user_subscriptions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 初期データ挿入
INSERT INTO subscription_tiers (tier, name, description, monthly_price, yearly_price, features, usage_limits) VALUES
('free', 'Free Plan', 'Basic features for individual users', 0.00, 0.00, 
 '["meta_description_generation", "basic_seo_analysis"]',
 '{"articles_per_month": 10, "api_calls_per_day": 100, "storage_mb": 100}'),
('basic', 'Basic Plan', 'Enhanced features for small teams', 29.99, 299.99,
 '["meta_description_generation", "thumbnail_generation", "advanced_seo_analysis", "basic_support"]',
 '{"articles_per_month": 100, "api_calls_per_day": 1000, "storage_mb": 1000}'),
('premium', 'Premium Plan', 'Advanced features for growing businesses', 99.99, 999.99,
 '["all_basic_features", "content_management", "fact_checking", "priority_support", "custom_templates"]',
 '{"articles_per_month": 1000, "api_calls_per_day": 10000, "storage_mb": 10000}'),
('enterprise', 'Enterprise Plan', 'Full-featured solution for large organizations', 299.99, 2999.99,
 '["all_premium_features", "white_labeling", "dedicated_support", "custom_integrations", "sla"]',
 '{"articles_per_month": -1, "api_calls_per_day": -1, "storage_mb": -1}');