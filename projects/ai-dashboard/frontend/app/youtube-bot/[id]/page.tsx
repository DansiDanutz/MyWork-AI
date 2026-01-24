'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  RefreshCw, ArrowLeft, Save, Check, Play, Upload,
  Edit, Eye, Clock, AlertCircle, Video
} from 'lucide-react';
import { getAutomation, updateAutomation, approveAutomation, Automation } from '@/lib/api';

export default function AutomationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const automationId = parseInt(params.id as string);

  const [automation, setAutomation] = useState<Automation | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Editable fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [script, setScript] = useState('');
  const [tags, setTags] = useState('');

  useEffect(() => {
    fetchAutomation();
  }, [automationId]);

  const fetchAutomation = async () => {
    try {
      setLoading(true);
      const data = await getAutomation(automationId);
      setAutomation(data);
      setTitle(data.video_title);
      setDescription(data.video_description || '');
      setScript(data.video_script || '');
      setTags(data.video_tags?.join(', ') || '');
      setError(null);
    } catch (err) {
      setError('Failed to load automation');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const updates: Partial<Automation> = {};
      if (title !== automation?.video_title) {
        (updates as any).title = title;
      }
      if (description !== automation?.video_description) {
        (updates as any).description = description;
      }
      if (script !== automation?.video_script) {
        (updates as any).script = script;
      }

      const tagArray = tags.split(',').map(t => t.trim()).filter(t => t);
      if (JSON.stringify(tagArray) !== JSON.stringify(automation?.video_tags)) {
        (updates as any).tags = tagArray;
      }

      if (Object.keys(updates).length > 0) {
        const updated = await updateAutomation(automationId, updates);
        setAutomation(updated);
        setSuccess('Changes saved successfully!');
      }
    } catch (err) {
      setError('Failed to save changes');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    try {
      setApproving(true);
      setError(null);
      const result = await approveAutomation(automationId);
      setSuccess(`Video approved! ${result.youtube_url ? `URL: ${result.youtube_url}` : ''}`);
      await fetchAutomation();
    } catch (err) {
      setError('Failed to approve video');
      console.error(err);
    } finally {
      setApproving(false);
    }
  };

  const getStatusInfo = (status: string) => {
    const info: Record<string, { color: string; icon: React.ElementType; text: string }> = {
      draft: { color: 'bg-gray-100 text-gray-700', icon: Edit, text: 'Draft - Edit and review' },
      generating: { color: 'bg-yellow-100 text-yellow-700', icon: Clock, text: 'Video is being generated...' },
      pending_review: { color: 'bg-blue-100 text-blue-700', icon: Eye, text: 'Ready for review' },
      approved: { color: 'bg-green-100 text-green-700', icon: Check, text: 'Approved' },
      ready_for_upload: { color: 'bg-purple-100 text-purple-700', icon: Upload, text: 'Ready for YouTube upload' },
      uploaded: { color: 'bg-emerald-100 text-emerald-700', icon: Check, text: 'Uploaded to YouTube!' },
      failed: { color: 'bg-red-100 text-red-700', icon: AlertCircle, text: 'Generation failed' },
    };
    return info[status] || info.draft;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!automation) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
        <p className="text-gray-500">Automation not found</p>
        <Link href="/youtube-bot" className="text-blue-600 hover:underline mt-4 inline-block">
          Back to YouTube Bot
        </Link>
      </div>
    );
  }

  const statusInfo = getStatusInfo(automation.status);
  const StatusIcon = statusInfo.icon;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/youtube-bot"
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Edit Video</h1>
            <p className="text-gray-500">ID: {automation.id}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className={`flex items-center gap-2 px-3 py-2 rounded-lg ${statusInfo.color}`}>
            <StatusIcon className="w-4 h-4" />
            {statusInfo.text}
          </span>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}
      {success && (
        <div className="bg-green-50 text-green-600 p-4 rounded-lg flex items-center gap-2">
          <Check className="w-5 h-5" />
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Editor */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter video title..."
            />
          </div>

          {/* Description */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={5}
              placeholder="Enter video description..."
            />
          </div>

          {/* Script */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video Script
            </label>
            <textarea
              value={script}
              onChange={(e) => setScript(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
              rows={15}
              placeholder="Enter video script..."
            />
          </div>

          {/* Tags */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags (comma separated)
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="AI, machine learning, tutorial, ..."
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Actions */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-medium mb-4">Actions</h3>
            <div className="space-y-3">
              <button
                onClick={handleSave}
                disabled={saving}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
              >
                {saving ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                {saving ? 'Saving...' : 'Save Changes'}
              </button>

              {automation.status !== 'uploaded' && (
                <button
                  onClick={handleApprove}
                  disabled={approving}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white hover:bg-purple-700 rounded-lg transition-colors disabled:opacity-50"
                >
                  {approving ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Upload className="w-4 h-4" />
                  )}
                  {approving ? 'Approving...' : 'Approve & Upload'}
                </button>
              )}

              {automation.youtube_url && (
                <a
                  href={automation.youtube_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white hover:bg-red-700 rounded-lg transition-colors"
                >
                  <Play className="w-4 h-4" />
                  Watch on YouTube
                </a>
              )}
            </div>
          </div>

          {/* Preview */}
          {automation.heygen_video_url && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-medium mb-4">Video Preview</h3>
              <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                <video
                  src={automation.heygen_video_url}
                  controls
                  className="w-full h-full"
                />
              </div>
            </div>
          )}

          {/* Thumbnail */}
          {automation.thumbnail_url && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-medium mb-4">Thumbnail</h3>
              <img
                src={automation.thumbnail_url}
                alt="Thumbnail"
                className="w-full rounded-lg"
              />
            </div>
          )}

          {/* Info */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-medium mb-4">Details</h3>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Created</dt>
                <dd className="font-medium">
                  {new Date(automation.created_at).toLocaleString()}
                </dd>
              </div>
              {automation.approved_at && (
                <div>
                  <dt className="text-gray-500">Approved</dt>
                  <dd className="font-medium">
                    {new Date(automation.approved_at).toLocaleString()}
                  </dd>
                </div>
              )}
              {automation.uploaded_at && (
                <div>
                  <dt className="text-gray-500">Uploaded</dt>
                  <dd className="font-medium">
                    {new Date(automation.uploaded_at).toLocaleString()}
                  </dd>
                </div>
              )}
              <div>
                <dt className="text-gray-500">Original Prompt</dt>
                <dd className="font-medium text-gray-600 mt-1">
                  {automation.user_prompt}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
