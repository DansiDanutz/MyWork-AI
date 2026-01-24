'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, ExternalLink, MessageSquare, TrendingUp, Clock, Play } from 'lucide-react';
import { getNews, getTrendingNews, triggerScraper, News } from '@/lib/api';

export default function NewsPage() {
  const [news, setNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [showTrending, setShowTrending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchNews();
  }, [showTrending]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const data = showTrending ? await getTrendingNews(30) : await getNews(50);
      setNews(data);
      setError(null);
    } catch (err) {
      setError('Failed to load news');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async () => {
    try {
      setScraping(true);
      await triggerScraper('news');
      await fetchNews();
    } catch (err) {
      setError('Scraping failed');
      console.error(err);
    } finally {
      setScraping(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Unknown';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getSourceColor = (source: string) => {
    const colors: Record<string, string> = {
      'Hacker News': 'bg-orange-100 text-orange-700',
      'TechCrunch': 'bg-green-100 text-green-700',
      'The Verge': 'bg-purple-100 text-purple-700',
      'MIT Technology Review': 'bg-red-100 text-red-700',
      'Ars Technica': 'bg-blue-100 text-blue-700',
      'VentureBeat': 'bg-indigo-100 text-indigo-700',
    };
    return colors[source] || 'bg-gray-100 text-gray-700';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI News</h1>
          <p className="text-gray-500 mt-1">Latest AI and ML news from top sources</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowTrending(!showTrending)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showTrending
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            Trending
          </button>
          <button
            onClick={fetchNews}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            {scraping ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            {scraping ? 'Scraping...' : 'Scrape Now'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">
          {error}
        </div>
      )}

      {/* News List */}
      <div className="space-y-4">
        {news.map((item) => (
          <div
            key={item.id}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex gap-6">
              {/* Thumbnail */}
              {item.thumbnail_url && (
                <div className="hidden md:block flex-shrink-0">
                  <img
                    src={item.thumbnail_url}
                    alt={item.title}
                    className="w-48 h-32 object-cover rounded-lg"
                  />
                </div>
              )}

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${getSourceColor(item.source)}`}>
                    {item.source}
                  </span>
                  {item.score > 100 && (
                    <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      Hot
                    </span>
                  )}
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                  {item.title}
                </h3>

                {item.summary && (
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {item.summary}
                  </p>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    {item.author && (
                      <span>by {item.author}</span>
                    )}
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDate(item.published_at)}
                    </div>
                    {item.comments_count > 0 && (
                      <div className="flex items-center gap-1">
                        <MessageSquare className="w-4 h-4" />
                        {item.comments_count}
                      </div>
                    )}
                    {item.score > 0 && (
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-4 h-4" />
                        {item.score} points
                      </div>
                    )}
                  </div>

                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    Read More
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {news.length === 0 && !error && (
        <div className="text-center py-12 text-gray-500">
          <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No news yet. Click "Scrape Now" to fetch AI news.</p>
        </div>
      )}
    </div>
  );
}
