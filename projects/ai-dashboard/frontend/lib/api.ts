import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Video {
  id: number;
  video_id: string;
  title: string;
  channel_name: string | null;
  view_count: number;
  like_count: number;
  quality_score: number;
  thumbnail_url: string | null;
  published_at: string | null;
}

export interface News {
  id: number;
  title: string;
  url: string;
  source: string;
  author: string | null;
  summary: string | null;
  score: number;
  comments_count: number;
  published_at: string | null;
  thumbnail_url: string | null;
}

export interface Project {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  url: string;
  stars: number;
  forks: number;
  language: string | null;
  topics: string[] | null;
  trending_score: number;
  weekly_stars: number;
  pushed_at: string | null;
}

export interface Automation {
  id: number;
  user_prompt: string;
  video_title: string;
  video_description: string | null;
  video_script: string | null;
  video_tags: string[] | null;
  thumbnail_url: string | null;
  heygen_video_url: string | null;
  youtube_url: string | null;
  status: string;
  created_at: string;
  approved_at: string | null;
  uploaded_at: string | null;
}

export interface Stats {
  videos: number;
  news: number;
  projects: number;
  automations: number;
  recent_scrapes: {
    scraper: string;
    status: string;
    items: number;
    started_at: string | null;
  }[];
}

// API Functions
export async function getVideos(limit = 20): Promise<Video[]> {
  const { data } = await api.get(`/api/videos?limit=${limit}`);
  return data;
}

export async function getNews(limit = 50): Promise<News[]> {
  const { data } = await api.get(`/api/news?limit=${limit}`);
  return data;
}

export async function getTrendingNews(limit = 20): Promise<News[]> {
  const { data } = await api.get(`/api/news/trending?limit=${limit}`);
  return data;
}

export async function getProjects(limit = 20): Promise<Project[]> {
  const { data } = await api.get(`/api/projects?limit=${limit}`);
  return data;
}

export async function getTrendingProjects(limit = 20): Promise<Project[]> {
  const { data } = await api.get(`/api/projects/trending?limit=${limit}`);
  return data;
}

export async function getAutomations(): Promise<Automation[]> {
  const { data } = await api.get('/api/automation');
  return data;
}

export async function getAutomation(id: number): Promise<Automation> {
  const { data } = await api.get(`/api/automation/${id}`);
  return data;
}

export async function createAutomation(prompt: string, targetAudience = 'tech enthusiasts', videoLength = '5-10'): Promise<Automation> {
  const { data } = await api.post('/api/automation', {
    prompt,
    target_audience: targetAudience,
    video_length: videoLength,
  });
  return data;
}

export async function updateAutomation(id: number, updates: Partial<Automation>): Promise<Automation> {
  const { data } = await api.patch(`/api/automation/${id}`, updates);
  return data;
}

export async function approveAutomation(id: number): Promise<{ status: string; youtube_url: string }> {
  const { data } = await api.post(`/api/automation/${id}/approve`);
  return data;
}

export async function generateVideo(id: number): Promise<{ status: string; automation_id: number; heygen_status: string }> {
  const { data } = await api.post(`/api/automation/${id}/generate-video`);
  return data;
}

export async function checkVideoStatus(id: number): Promise<{ status: string; video_url?: string; error?: string }> {
  const { data } = await api.get(`/api/automation/${id}/video-status`);
  return data;
}

export async function getStats(): Promise<Stats> {
  const { data } = await api.get('/api/stats');
  return data;
}

export async function triggerScraper(scraper: 'videos' | 'news' | 'projects'): Promise<{ status: string; message: string }> {
  const { data } = await api.post(`/api/${scraper}/scrape`);
  return data;
}

export async function getSchedulerStatus(): Promise<Record<string, any>> {
  const { data } = await api.get('/api/scheduler/status');
  return data;
}
