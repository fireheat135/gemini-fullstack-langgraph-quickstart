-- コンテンツ管理スキーマ（正規化済み）
-- Content Management Schema (Normalized)

-- コンテンツタイプ定義
CREATE TYPE content_type_enum AS ENUM ('article', 'blog_post', 'product_description', 'landing_page', 'birth_flower_article');
CREATE TYPE content_status_enum AS ENUM ('draft', 'in_review', 'published', 'archived');
CREATE TYPE seo_difficulty_enum AS ENUM ('low', 'medium', 'high', 'very_high');

-- 記事基本情報（第1正規形）
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE,
    content TEXT,
    content_type content_type_enum NOT NULL DEFAULT 'article',
    status content_status_enum NOT NULL DEFAULT 'draft',
    word_count INTEGER DEFAULT 0,
    reading_time_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    archived_at TIMESTAMP,
    
    -- 制約
    CONSTRAINT articles_word_count_positive CHECK (word_count >= 0),
    CONSTRAINT articles_reading_time_positive CHECK (reading_time_minutes >= 0),
    CONSTRAINT articles_slug_format CHECK (slug ~* '^[a-z0-9\-]+$')
);

-- SEOメタデータ（第2正規形）
CREATE TABLE article_seo_metadata (
    article_id UUID PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    meta_description VARCHAR(160),
    meta_keywords TEXT,
    primary_keyword VARCHAR(100),
    secondary_keywords TEXT[], -- PostgreSQL配列型
    focus_keyphrase VARCHAR(200),
    canonical_url VARCHAR(500),
    og_title VARCHAR(60),
    og_description VARCHAR(200),
    og_image_url VARCHAR(500),
    schema_markup JSONB,
    seo_score DECIMAL(3,2) CHECK (seo_score >= 0 AND seo_score <= 100),
    readability_score DECIMAL(3,2) CHECK (readability_score >= 0 AND readability_score <= 100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- キーワード分析結果（第3正規形）
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword VARCHAR(200) UNIQUE NOT NULL,
    search_volume INTEGER,
    competition_level seo_difficulty_enum,
    cpc DECIMAL(8,2),
    seasonal_trends JSONB,
    last_analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- インデックス
    INDEX idx_keywords_keyword (keyword),
    INDEX idx_keywords_search_volume (search_volume DESC),
    INDEX idx_keywords_competition (competition_level)
);

-- 記事-キーワード関連付け
CREATE TABLE article_keywords (
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    density DECIMAL(5,4) CHECK (density >= 0 AND density <= 1),
    position_rank INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (article_id, keyword_id)
);

-- コンテンツ品質メトリクス
CREATE TABLE content_quality_metrics (
    article_id UUID PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    originality_score DECIMAL(3,2) CHECK (originality_score >= 0 AND originality_score <= 100),
    fact_check_score DECIMAL(3,2) CHECK (fact_check_score >= 0 AND fact_check_score <= 100),
    tone_consistency_score DECIMAL(3,2) CHECK (tone_consistency_score >= 0 AND tone_consistency_score <= 100),
    grammar_score DECIMAL(3,2) CHECK (grammar_score >= 0 AND grammar_score <= 100),
    overall_quality_score DECIMAL(3,2) CHECK (overall_quality_score >= 0 AND overall_quality_score <= 100),
    last_analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 画像・メディア管理
CREATE TABLE article_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT CHECK (file_size_bytes > 0),
    mime_type VARCHAR(100) NOT NULL,
    width INTEGER,
    height INTEGER,
    alt_text TEXT,
    caption TEXT,
    is_thumbnail BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- インデックス
    INDEX idx_article_media_article (article_id),
    INDEX idx_article_media_thumbnail (is_thumbnail) WHERE is_thumbnail = true
);

-- 重複コンテンツ検出
CREATE TABLE duplicate_content_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    compared_against_url VARCHAR(500),
    similarity_percentage DECIMAL(5,2) CHECK (similarity_percentage >= 0 AND similarity_percentage <= 100),
    duplicate_sections TEXT[],
    is_duplicate BOOLEAN GENERATED ALWAYS AS (similarity_percentage > 80) STORED,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- インデックス
    INDEX idx_duplicate_checks_article (article_id),
    INDEX idx_duplicate_checks_similarity (similarity_percentage DESC),
    INDEX idx_duplicate_checks_date (checked_at DESC)
);

-- トーン・マナー分析
CREATE TABLE tone_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    detected_tone VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    tone_keywords TEXT[],
    style_characteristics JSONB,
    brand_consistency_score DECIMAL(3,2) CHECK (brand_consistency_score >= 0 AND brand_consistency_score <= 100),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 記事変更履歴（監査ログ）
CREATE TABLE article_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    title VARCHAR(500),
    content TEXT,
    changes_summary TEXT,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (article_id, revision_number)
);

-- パフォーマンス分析
CREATE TABLE article_performance (
    article_id UUID PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    page_views INTEGER DEFAULT 0,
    unique_visitors INTEGER DEFAULT 0,
    average_time_on_page INTEGER DEFAULT 0, -- 秒単位
    bounce_rate DECIMAL(5,2) CHECK (bounce_rate >= 0 AND bounce_rate <= 100),
    social_shares INTEGER DEFAULT 0,
    backlinks_count INTEGER DEFAULT 0,
    search_ranking_position INTEGER,
    organic_traffic INTEGER DEFAULT 0,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT performance_positive_values CHECK (
        page_views >= 0 AND 
        unique_visitors >= 0 AND 
        average_time_on_page >= 0 AND 
        social_shares >= 0 AND 
        backlinks_count >= 0 AND 
        organic_traffic >= 0
    )
);

-- インデックス作成
CREATE INDEX idx_articles_user_id ON articles(user_id);
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_content_type ON articles(content_type);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC) WHERE published_at IS NOT NULL;
CREATE INDEX idx_articles_slug ON articles(slug) WHERE slug IS NOT NULL;

CREATE INDEX idx_seo_metadata_primary_keyword ON article_seo_metadata(primary_keyword);
CREATE INDEX idx_seo_metadata_seo_score ON article_seo_metadata(seo_score DESC);

CREATE INDEX idx_article_keywords_primary ON article_keywords(is_primary) WHERE is_primary = true;
CREATE INDEX idx_article_keywords_density ON article_keywords(density DESC);

-- トリガー（更新時刻の自動更新）
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_seo_metadata_updated_at 
    BEFORE UPDATE ON article_seo_metadata 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_updated_at 
    BEFORE UPDATE ON article_performance 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ビュー：完全な記事情報
CREATE VIEW article_details AS
SELECT 
    a.id,
    a.user_id,
    a.title,
    a.slug,
    a.content,
    a.content_type,
    a.status,
    a.word_count,
    a.reading_time_minutes,
    a.created_at,
    a.updated_at,
    a.published_at,
    seo.meta_description,
    seo.primary_keyword,
    seo.seo_score,
    seo.readability_score,
    qm.overall_quality_score,
    perf.page_views,
    perf.organic_traffic,
    perf.search_ranking_position
FROM articles a
LEFT JOIN article_seo_metadata seo ON a.id = seo.article_id
LEFT JOIN content_quality_metrics qm ON a.id = qm.article_id
LEFT JOIN article_performance perf ON a.id = perf.article_id;