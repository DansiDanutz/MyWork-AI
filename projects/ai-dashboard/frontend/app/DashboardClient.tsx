"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  LuVideo,
  LuNewspaper,
  LuFolderGit2,
  LuBot,
  LuRefreshCw,
  LuClock,
} from "react-icons/lu";
import { getStats, Stats } from "@/lib/api";

export default function DashboardClient() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await getStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError("Failed to load dashboard stats");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: "AI Videos",
      count: stats?.videos || 0,
      icon: LuVideo,
      href: "/videos",
      color: "from-red-500 to-pink-500",
    },
    {
      title: "AI News",
      count: stats?.news || 0,
      icon: LuNewspaper,
      href: "/news",
      color: "from-blue-500 to-cyan-500",
    },
    {
      title: "GitHub Projects",
      count: stats?.projects || 0,
      icon: LuFolderGit2,
      href: "/projects",
      color: "from-green-500 to-emerald-500",
    },
    {
      title: "Automations",
      count: stats?.automations || 0,
      icon: LuBot,
      href: "/youtube-bot",
      color: "from-purple-500 to-violet-500",
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LuRefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-red-500">{error}</p>
        <button
          onClick={fetchStats}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Your AI Command Center Overview</p>
        </div>
        <button
          onClick={fetchStats}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <LuRefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card) => (
          <Link
            key={card.title}
            href={card.href}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{card.title}</p>
                <p className="text-3xl font-bold mt-1">
                  {card.count.toLocaleString()}
                </p>
              </div>
              <div
                className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center`}
              >
                <card.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Recent Scrapes */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-semibold">Recent Scrapes</h2>
          <p className="text-sm text-gray-500 mt-1">
            Latest data collection activity
          </p>
        </div>
        <div className="divide-y divide-gray-100">
          {stats?.recent_scrapes && stats.recent_scrapes.length > 0 ? (
            stats.recent_scrapes.map((scrape, index) => (
              <div
                key={index}
                className="p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      scrape.status === "success"
                        ? "bg-green-500"
                        : scrape.status === "running"
                          ? "bg-yellow-500 animate-pulse"
                          : "bg-red-500"
                    }`}
                  />
                  <div>
                    <p className="font-medium capitalize">
                      {scrape.scraper.replace("_", " ")}
                    </p>
                    <p className="text-sm text-gray-500">
                      {scrape.items} items collected
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <LuClock className="w-4 h-4" />
                  {scrape.started_at
                    ? new Date(scrape.started_at).toLocaleString()
                    : "N/A"}
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-gray-500">
              No recent scrapes. Start the backend to begin collecting data.
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/youtube-bot"
            className="flex items-center gap-3 p-4 bg-gradient-to-r from-purple-500 to-violet-600 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <LuBot className="w-6 h-6" />
            <div>
              <p className="font-medium">Create Video</p>
              <p className="text-sm text-purple-100">Start a new automation</p>
            </div>
          </Link>
          <Link
            href="/videos"
            className="flex items-center gap-3 p-4 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <LuVideo className="w-6 h-6" />
            <div>
              <p className="font-medium">Browse Videos</p>
              <p className="text-sm text-red-100">Latest AI content</p>
            </div>
          </Link>
          <Link
            href="/projects"
            className="flex items-center gap-3 p-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <LuFolderGit2 className="w-6 h-6" />
            <div>
              <p className="font-medium">Trending Projects</p>
              <p className="text-sm text-green-100">Hot AI repositories</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
