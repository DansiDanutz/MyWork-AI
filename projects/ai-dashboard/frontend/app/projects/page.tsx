'use client';

import { useEffect, useState } from 'react';
import { RefreshCw, ExternalLink, Star, GitFork, TrendingUp, Code, Play } from 'lucide-react';
import { getProjects, getTrendingProjects, triggerScraper, Project } from '@/lib/api';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [showTrending, setShowTrending] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, [showTrending]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = showTrending ? await getTrendingProjects(20) : await getProjects(50);
      setProjects(data);
      setError(null);
    } catch (err) {
      setError('Failed to load projects');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async () => {
    try {
      setScraping(true);
      await triggerScraper('projects');
      await fetchProjects();
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

  const getLanguageColor = (lang: string | null) => {
    const colors: Record<string, string> = {
      Python: 'bg-blue-500',
      JavaScript: 'bg-yellow-500',
      TypeScript: 'bg-blue-600',
      Rust: 'bg-orange-500',
      Go: 'bg-cyan-500',
      Java: 'bg-red-500',
      'C++': 'bg-pink-500',
      C: 'bg-gray-600',
      Jupyter: 'bg-orange-400',
    };
    return colors[lang || ''] || 'bg-gray-400';
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
          <h1 className="text-3xl font-bold text-gray-900">GitHub Projects</h1>
          <p className="text-gray-500 mt-1">Top AI and ML open source projects</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowTrending(!showTrending)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showTrending
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            Trending
          </button>
          <button
            onClick={fetchProjects}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
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

      {/* Projects Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {projects.map((project, index) => (
          <div
            key={project.id}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {showTrending && (
                    <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                  )}
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {project.name}
                  </h3>
                </div>
                <p className="text-sm text-gray-500 truncate">{project.full_name}</p>
              </div>
              {project.weekly_stars > 0 && (
                <span className="flex items-center gap-1 text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full">
                  <TrendingUp className="w-3 h-3" />
                  +{formatNumber(project.weekly_stars)} this week
                </span>
              )}
            </div>

            {project.description && (
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {project.description}
              </p>
            )}

            {/* Topics */}
            {project.topics && project.topics.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {project.topics.slice(0, 5).map((topic) => (
                  <span
                    key={topic}
                    className="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded-full"
                  >
                    {topic}
                  </span>
                ))}
                {project.topics.length > 5 && (
                  <span className="text-xs px-2 py-1 bg-gray-100 text-gray-500 rounded-full">
                    +{project.topics.length - 5} more
                  </span>
                )}
              </div>
            )}

            {/* Stats */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm text-gray-500">
                {project.language && (
                  <div className="flex items-center gap-1">
                    <span className={`w-3 h-3 rounded-full ${getLanguageColor(project.language)}`} />
                    {project.language}
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-yellow-500" />
                  {formatNumber(project.stars)}
                </div>
                <div className="flex items-center gap-1">
                  <GitFork className="w-4 h-4" />
                  {formatNumber(project.forks)}
                </div>
              </div>

              <a
                href={project.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Code className="w-4 h-4" />
                View
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && !error && (
        <div className="text-center py-12 text-gray-500">
          <Code className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No projects yet. Click "Scrape Now" to fetch GitHub projects.</p>
        </div>
      )}
    </div>
  );
}
