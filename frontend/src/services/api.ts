/**
 * Serviço de comunicação com o backend FastAPI.
 * Base URL é relativa (usa o proxy do Vite em desenvolvimento).
 */

import axios from 'axios';
import type {
  VideoItem,
  DashboardMetrics,
  SystemHealth,
  OperationMode,
} from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// === Pipeline ===

export async function createVideo(ticker: string, topic?: string, autoUpload = false): Promise<VideoItem> {
  const { data } = await api.post<VideoItem>('/pipeline/create', {
    ticker,
    topic,
    auto_upload: autoUpload,
  });
  return data;
}

export async function getVideoStatus(videoId: string): Promise<VideoItem> {
  const { data } = await api.get<VideoItem>(`/pipeline/status/${videoId}`);
  return data;
}

export async function getVideoQueue(): Promise<VideoItem[]> {
  const { data } = await api.get<VideoItem[]>('/pipeline/queue');
  return data;
}

export async function getOperationMode(): Promise<OperationMode> {
  const { data } = await api.get<{ mode: OperationMode }>('/pipeline/mode');
  return data.mode;
}

export async function setOperationMode(mode: OperationMode): Promise<void> {
  await api.post('/pipeline/mode', mode, {
    headers: { 'Content-Type': 'application/json' },
  });
}

// === Vídeos ===

export async function listVideos(): Promise<VideoItem[]> {
  const { data } = await api.get<VideoItem[]>('/videos/');
  return data;
}

export async function getVideo(videoId: string): Promise<VideoItem> {
  const { data } = await api.get<VideoItem>(`/videos/${videoId}`);
  return data;
}

export async function getVideoLogs(videoId: string): Promise<string[]> {
  const { data } = await api.get<string[]>(`/videos/${videoId}/logs`);
  return data;
}

export async function deleteVideo(videoId: string): Promise<void> {
  await api.delete(`/videos/${videoId}`);
}

// === Dashboard ===

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  const { data } = await api.get<DashboardMetrics>('/dashboard/metrics');
  return data;
}

export async function getSystemHealth(): Promise<SystemHealth> {
  const { data } = await api.get<SystemHealth>('/dashboard/health');
  return data;
}

export async function getAdsenseStatus(): Promise<Record<string, unknown>> {
  const { data } = await api.get('/dashboard/adsense');
  return data;
}

// === YouTube ===

export async function getYouTubeAuthStatus(): Promise<{
  authenticated: boolean;
  secrets_file: string;
  secrets_file_exists: boolean;
  message: string;
}> {
  const { data } = await api.get('/youtube/auth/status');
  return data;
}

export async function uploadToYouTube(videoId: string, privacy = 'private'): Promise<{
  success: boolean;
  video_id: string;
  youtube_url: string;
}> {
  const { data } = await api.post(`/youtube/upload/${videoId}`, null, {
    params: { privacy },
  });
  return data;
}

// === Health ===

export async function checkApiHealth(): Promise<boolean> {
  try {
    await api.get('/health');
    return true;
  } catch {
    return false;
  }
}
