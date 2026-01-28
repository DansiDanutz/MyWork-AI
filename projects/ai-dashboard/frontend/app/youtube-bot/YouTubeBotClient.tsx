"use client";

import { useEffect, useState } from "react";
import {
  LuRefreshCw,
  LuPlus,
  LuPlay,
  LuCheck,
  LuPencil,
  LuEye,
  LuUpload,
  LuClock,
  LuCircleAlert,
} from "react-icons/lu";
import { getAutomations, createAutomation, Automation } from "@/lib/api";
import Link from "next/link";

export default function YouTubeBotClient() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [prompt, setPrompt] = useState("");
  const [targetAudience, setTargetAudience] = useState("tech enthusiasts");
  const [videoLength, setVideoLength] = useState("5-10");

  useEffect(() => {
    fetchAutomations();
  }, []);

  const fetchAutomations = async () => {
    try {
      setLoading(true);
      const data = await getAutomations();
      setAutomations(data);
      setError(null);
    } catch (err) {
      setError("Failed to load automations");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    try {
      setCreating(true);
      await createAutomation(prompt, targetAudience, videoLength);
      setShowCreateModal(false);
      setPrompt("");
      await fetchAutomations();
    } catch (err) {
      setError("Failed to create automation");
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { color: string; icon: React.ElementType }> = {
      draft: { color: "bg-gray-100 text-gray-700", icon: LuPencil },
      generating: { color: "bg-yellow-100 text-yellow-700", icon: LuClock },
      pending_review: { color: "bg-blue-100 text-blue-700", icon: LuEye },
      approved: { color: "bg-green-100 text-green-700", icon: LuCheck },
      ready_for_upload: {
        color: "bg-purple-100 text-purple-700",
        icon: LuUpload,
      },
      uploaded: { color: "bg-emerald-100 text-emerald-700", icon: LuCheck },
      failed: { color: "bg-red-100 text-red-700", icon: LuCircleAlert },
    };
    const badge = badges[status] || badges.draft;
    const Icon = badge.icon;
    return (
      <span
        className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${badge.color}`}
      >
        <Icon className="w-3 h-3" />
        {status.replace("_", " ")}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LuRefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">YouTube Bot</h1>
          <p className="text-gray-500 mt-1">
            Automated AI video creation pipeline
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchAutomations}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <LuRefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white hover:bg-purple-700 rounded-lg transition-colors"
          >
            <LuPlus className="w-4 h-4" />
            Create Video
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">{error}</div>
      )}

      {/* Pipeline Overview */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold mb-4">Pipeline Overview</h2>
        <div className="flex items-center justify-between overflow-x-auto pb-2">
          {[
            "Prompt",
            "Optimize",
            "Generate Script",
            "Create Video",
            "Review",
            "Upload",
          ].map((step, i) => (
            <div key={step} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
                  {i + 1}
                </div>
                <span className="text-xs text-gray-500 mt-2 whitespace-nowrap">
                  {step}
                </span>
              </div>
              {i < 5 && <div className="w-12 h-0.5 bg-purple-200 mx-2" />}
            </div>
          ))}
        </div>
      </div>

      {/* Automations List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-semibold">Your Videos</h2>
          <p className="text-sm text-gray-500 mt-1">
            Track your video automation progress
          </p>
        </div>

        {automations.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {automations.map((automation) => (
              <div
                key={automation.id}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      {getStatusBadge(automation.status)}
                      <span className="text-sm text-gray-500">
                        {new Date(automation.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {automation.video_title}
                    </h3>
                    <p className="text-sm text-gray-500 line-clamp-2">
                      {automation.video_description || automation.user_prompt}
                    </p>

                    {automation.video_tags &&
                      automation.video_tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-3">
                          {automation.video_tags.slice(0, 5).map((tag) => (
                            <span
                              key={tag}
                              className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    {automation.youtube_url && (
                      <a
                        href={automation.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                      >
                        <LuPlay className="w-4 h-4" />
                        Watch
                      </a>
                    )}
                    <Link
                      href={`/youtube-bot/${automation.id}`}
                      className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm"
                    >
                      <LuEye className="w-4 h-4" />
                      View
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-gray-500">
            <LuPlay className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>
              No videos yet. Click "Create Video" to start your first
              automation.
            </p>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-semibold">Create New Video</h2>
              <p className="text-sm text-gray-500 mt-1">
                Enter your video idea and let AI handle the rest
              </p>
            </div>

            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Video Idea / Prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., Explain how transformers work in AI..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  rows={4}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <select
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="tech enthusiasts">Tech Enthusiasts</option>
                  <option value="developers">Developers</option>
                  <option value="beginners">Beginners</option>
                  <option value="business professionals">
                    Business Professionals
                  </option>
                  <option value="students">Students</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Video Length (minutes)
                </label>
                <select
                  value={videoLength}
                  onChange={(e) => setVideoLength(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="2-5">Short (2-5 min)</option>
                  <option value="5-10">Medium (5-10 min)</option>
                  <option value="10-15">Long (10-15 min)</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || !prompt.trim()}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50"
                >
                  {creating ? (
                    <LuRefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <LuPlus className="w-4 h-4" />
                  )}
                  {creating ? "Creating..." : "Create Video"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
