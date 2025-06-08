import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ContentManager from '../components/ContentManager';

// Mock fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock data
const mockArticles = {
  items: [
    {
      id: 1,
      title: 'テスト記事1: 誕生花の育て方',
      content: 'これはテスト記事の内容です。',
      status: 'published',
      content_type: 'blog_post',
      word_count: 500,
      reading_time: 3,
      seo_score: 85.5,
      page_views: 1500,
      published_at: '2025-06-01T00:00:00Z',
      created_at: '2025-06-01T00:00:00Z',
      updated_at: '2025-06-01T00:00:00Z',
    },
    {
      id: 2,
      title: 'テスト記事2: SEO最適化ガイド',
      content: 'これは2番目のテスト記事です。',
      status: 'draft',
      content_type: 'guide',
      word_count: 750,
      reading_time: 4,
      seo_score: 72.0,
      page_views: 500,
      created_at: '2025-06-02T00:00:00Z',
      updated_at: '2025-06-02T00:00:00Z',
    },
  ],
  total: 2,
  skip: 0,
  limit: 10,
};

const mockAnalytics = {
  total_articles: 2,
  total_page_views: 2000,
  total_unique_visitors: 1800,
  average_seo_score: 78.8,
  top_performing_articles: [
    {
      id: 1,
      title: 'テスト記事1: 誕生花の育て方',
      page_views: 1500,
      performance_score: 95.0,
    },
  ],
};

describe('ContentManager', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockClear();
  });

  it('記事一覧とアナリティクスを正しく表示する', async () => {
    // Mock API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    // Check loading state
    expect(screen.getByText('読み込み中...')).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('テスト記事1: 誕生花の育て方')).toBeInTheDocument();
    });

    // Check article data
    expect(screen.getByText('テスト記事2: SEO最適化ガイド')).toBeInTheDocument();
    expect(screen.getByText('500文字 • 3分')).toBeInTheDocument();
    expect(screen.getByText('750文字 • 4分')).toBeInTheDocument();

    // Check analytics
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // total articles
      expect(screen.getByText('2,000')).toBeInTheDocument(); // total page views
      expect(screen.getByText('78.8')).toBeInTheDocument(); // average SEO score
    });
  });

  it('検索機能が正しく動作する', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('テスト記事1: 誕生花の育て方')).toBeInTheDocument();
    });

    // Test search functionality
    const searchInput = screen.getByPlaceholderText('記事を検索...');
    fireEvent.change(searchInput, { target: { value: '誕生花' } });

    // Verify search value is set
    expect(searchInput).toHaveValue('誕生花');
  });

  it('ステータスフィルターが正しく動作する', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('テスト記事1: 誕生花の育て方')).toBeInTheDocument();
    });

    // Test status filter
    const statusFilter = screen.getByDisplayValue('すべてのステータス');
    fireEvent.change(statusFilter, { target: { value: 'published' } });

    expect(statusFilter).toHaveValue('published');
  });

  it('記事詳細モーダルが正しく表示される', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('テスト記事1: 誕生花の育て方')).toBeInTheDocument();
    });

    // Click view button (eye icon)
    const viewButtons = screen.getAllByTitle('詳細表示');
    fireEvent.click(viewButtons[0]);

    // Check if modal is displayed
    await waitFor(() => {
      expect(screen.getByText('記事詳細')).toBeInTheDocument();
    });

    // Check modal content
    expect(screen.getByText('ページビュー')).toBeInTheDocument();
    expect(screen.getByText('1,500')).toBeInTheDocument();

    // Close modal
    const closeButton = screen.getByText('✕');
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('記事詳細')).not.toBeInTheDocument();
    });
  });

  it('記事削除機能が正しく動作する', async () => {
    // Mock window.confirm
    window.confirm = vi.fn(() => true);

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      })
      .mockResolvedValueOnce({
        ok: true,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockArticles, items: [mockArticles.items[1]] }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('テスト記事1: 誕生花の育て方')).toBeInTheDocument();
    });

    // Click delete button
    const deleteButtons = screen.getAllByTitle('削除');
    fireEvent.click(deleteButtons[0]);

    // Verify API calls
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/content/articles/1',
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token',
          }),
        })
      );
    });
  });

  it('記事公開機能が正しく動作する', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 2,
          status: 'published',
          published_at: '2025-06-06T00:00:00Z',
          message: 'Article published successfully',
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('テスト記事2: SEO最適化ガイド')).toBeInTheDocument();
    });

    // Click publish button for draft article
    const publishButton = screen.getByText('公開');
    fireEvent.click(publishButton);

    // Verify API call
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/content/articles/2/publish',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token',
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });

  it('SEOスコアバッジが正しく表示される', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticles,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('85.5')).toBeInTheDocument();
      expect(screen.getByText('72.0')).toBeInTheDocument();
    });

    // Check color classes (high score should be green)
    const highScoreElement = screen.getByText('85.5');
    expect(highScoreElement).toHaveClass('text-green-600');

    const mediumScoreElement = screen.getByText('72.0');
    expect(mediumScoreElement).toHaveClass('text-yellow-600');
  });

  it('ページネーションが正しく動作する', async () => {
    const mockArticlesWithPagination = {
      ...mockArticles,
      total: 25, // More than 10 items to trigger pagination
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticlesWithPagination,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnalytics,
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('1 から 2 / 25 件')).toBeInTheDocument();
    });

    // Test pagination controls
    expect(screen.getByText('前へ')).toBeDisabled();
    expect(screen.getByText('次へ')).not.toBeDisabled();
  });

  it('エラーハンドリングが正しく動作する', async () => {
    // Mock failed API calls
    mockFetch
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Network error'));

    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<ContentManager />);

    // Wait for error handling
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch articles:', expect.any(Error));
      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch analytics:', expect.any(Error));
    });

    consoleSpy.mockRestore();
  });

  it('ローディング状態が正しく表示される', () => {
    // Don't resolve the fetch promises to keep loading state
    mockFetch
      .mockReturnValueOnce(new Promise(() => {}))
      .mockReturnValueOnce(new Promise(() => {}));

    render(<ContentManager />);

    expect(screen.getByText('読み込み中...')).toBeInTheDocument();
  });

  it('記事が見つからない場合の表示が正しい', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, skip: 0, limit: 10 }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          total_articles: 0,
          total_page_views: 0,
          total_unique_visitors: 0,
          average_seo_score: 0,
          top_performing_articles: [],
        }),
      });

    render(<ContentManager />);

    await waitFor(() => {
      expect(screen.getByText('記事が見つかりません')).toBeInTheDocument();
    });
  });
});