"use client";

import { useState } from "react";
import {
  LuSave,
  LuRefreshCw,
  LuKey,
  LuClock,
  LuDatabase,
} from "react-icons/lu";

export default function SettingsClient() {
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  // Settings state
  const [youtubeInterval, setYoutubeInterval] = useState("8");
  const [newsInterval, setNewsInterval] = useState("4");
  const [githubInterval, setGithubInterval] = useState("12");
  const [minViews, setMinViews] = useState("10000");
  const [minStars, setMinStars] = useState("100");

  const handleSave = async () => {
    setSaving(true);
    // Simulate save
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setSaving(false);
    setSuccess(true);
    setTimeout(() => setSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">
          Configure your AI Dashboard preferences
        </p>
      </div>

      {success && (
        <div className="bg-green-50 text-green-600 p-4 rounded-lg flex items-center gap-2">
          <LuSave className="w-5 h-5" />
          Settings saved successfully!
        </div>
      )}

      {/* Scheduler Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <LuClock className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Scheduler</h2>
            <p className="text-sm text-gray-500">
              Configure scraping intervals
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              YouTube Scraper Interval (hours)
            </label>
            <select
              value={youtubeInterval}
              onChange={(e) => setYoutubeInterval(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="4">Every 4 hours</option>
              <option value="8">Every 8 hours</option>
              <option value="12">Every 12 hours</option>
              <option value="24">Every 24 hours</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              News Aggregator Interval (hours)
            </label>
            <select
              value={newsInterval}
              onChange={(e) => setNewsInterval(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="2">Every 2 hours</option>
              <option value="4">Every 4 hours</option>
              <option value="8">Every 8 hours</option>
              <option value="12">Every 12 hours</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              GitHub Scraper Interval (hours)
            </label>
            <select
              value={githubInterval}
              onChange={(e) => setGithubInterval(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="6">Every 6 hours</option>
              <option value="12">Every 12 hours</option>
              <option value="24">Every 24 hours</option>
            </select>
          </div>
        </div>
      </div>

      {/* Filter Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
            <LuDatabase className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Filters</h2>
            <p className="text-sm text-gray-500">
              Set minimum thresholds for content
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Video Views
            </label>
            <input
              type="number"
              value={minViews}
              onChange={(e) => setMinViews(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="10000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum GitHub Stars
            </label>
            <input
              type="number"
              value={minStars}
              onChange={(e) => setMinStars(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="100"
            />
          </div>
        </div>
      </div>

      {/* API Keys (Read-only display) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <LuKey className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">API Keys</h2>
            <p className="text-sm text-gray-500">
              Configured in backend .env file
            </p>
          </div>
        </div>

        <div className="space-y-3 text-sm">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Apify API Key</span>
            <span className="text-gray-400">Configure in .env</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Anthropic API Key</span>
            <span className="text-gray-400">Configure in .env</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">HeyGen API Key</span>
            <span className="text-gray-400">Configure in .env</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-500">GitHub Token</span>
            <span className="text-gray-400">Configure in .env</span>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
      >
        {saving ? (
          <LuRefreshCw className="w-4 h-4 animate-spin" />
        ) : (
          <LuSave className="w-4 h-4" />
        )}
        {saving ? "Saving..." : "Save Settings"}
      </button>
    </div>
  );
}
