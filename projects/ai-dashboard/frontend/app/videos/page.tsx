'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, ExternalLink, ThumbsUp, Eye, Play } from 'lucide-react';
import { getVideos, triggerScraper, Video } from '@/lib/api';

export default function VideosPage() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const data = await getVideos(50);
      setVideos(data);
      setError(null);
    } catch (err) {
      setError('Failed to load videos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async () => {
    try {
      setScraping(true);
      await triggerScraper('videos');
      await fetchVideos();
    } catch (err) {
      setError('Scraping failed');
      console.error(err);
    } finally {
      setScraping(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
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
          <h1 className="text-3xl font-bold text-gray-900">AI Videos</h1>
          <p className="text-gray-500 mt-1">Top rated AI and ML videos from YouTube</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchVideos}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50"
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

      {/* Videos Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {videos.map((video) => (
          <div
            key={video.id}
            className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
          >
            {/* Thumbnail */}
            <div className="relative aspect-video bg-gray-100">
              {video.thumbnail_url ? (
                <img
                  src={video.thumbnail_url}
                  alt={video.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-red-500 to-pink-600">
                  <Play className="w-12 h-12 text-white" />
                </div>
              )}
              <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                Score: {video.quality_score.toFixed(1)}
              </div>
            </div>

            {/* Content */}
            <div className="p-4">
              <h3 className="font-medium text-gray-900 line-clamp-2 mb-2">
                {video.title}
              </h3>
              <p className="text-sm text-gray-500 mb-3">
                {video.channel_name || 'Unknown Channel'}
              </p>

              {/* Stats */}
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <Eye className="w-4 h-4" />
                  {formatNumber(video.view_count)}
                </div>
                <div className="flex items-center gap-1">
                  <ThumbsUp className="w-4 h-4" />
                  {formatNumber(video.like_count)}
                </div>
              </div>

              {/* Watch Button */}
              <a
                href={`https://youtube.com/watch?v=${video.video_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                Watch on YouTube
              </a>
            </div>
          </div>
        ))}
      </div>

      {videos.length === 0 && !error && (
        <div className="text-center py-12 text-gray-500">
          <Play className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No videos yet. Click "Scrape Now" to fetch AI videos.</p>
        </div>
      )}
    </div>
  );
}
