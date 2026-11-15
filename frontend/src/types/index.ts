// Tipos partilhados entre frontend e backend

export type VideoStage =
  | 'ingestao'
  | 'ia_roteriro'
  | 'processamento_imagem'
  | 'renderizacao'
  | 'concluido'
  | 'falhou';

export type VideoStatus = 'queued' | 'processing' | 'ready' | 'uploaded' | 'error';

export type OperationMode = 'manual' | 'autonomous';

export interface StageInfo {
  name: string;
  status: VideoStage;
  progress: number;
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
}

export interface VideoItem {
  id: string;
  ticker: string;
  topic: string | null;
  status: VideoStatus;
  current_stage: VideoStage;
  stages: StageInfo[];
  created_at: string;
  updated_at: string;
  script: string | null;
  audio_path: string | null;
  video_path: string | null;
  youtube_video_id: string | null;
  error_log: string[];
}

export interface TickerData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number | null;
  news: NewsItem[];
}

export interface NewsItem {
  title: string;
  publisher: string;
  published: number;
  link: string;
  summary: string;
}

export interface DashboardMetrics {
  total_videos: number;
  completed_videos: number;
  failed_videos: number;
  processing_videos: number;
  total_views: number;
  trending_topics: TrendingTopic[];
  adsense_revenue: number;
  adsense_currency: string;
  system_health: string;
  uptime_seconds: number;
  pipeline_active: boolean;
}

export interface TrendingTopic {
  topic: string;
  ticker: string;
  trend_score: number;
  change_percent: number;
  direction: 'alta' | 'baixa';
}

export interface SystemHealth {
  status: string;
  ffmpeg_available: boolean;
  edge_tts_available: boolean;
  yfinance_available: boolean;
  youtube_authenticated: boolean;
  disk_space_mb: number;
  active_jobs: number;
}

// Definição dos 4 estágios do pipeline
export const PIPELINE_STAGES = [
  { id: 'ingestao', label: 'Ingestão de Dados', icon: '📥', color: 'blue' },
  { id: 'ia_roteriro', label: 'IA: Roteiro e Voz', icon: '🤖', color: 'purple' },
  { id: 'processamento_imagem', label: 'Processamento de Imagem', icon: '🎨', color: 'orange' },
  { id: 'renderizacao', label: 'Renderização', icon: '🎬', color: 'green' },
] as const;

export const STAGE_LABELS: Record<string, string> = {
  ingestao: 'Ingestão de Dados',
  ia_roteriro: 'IA: Roteiro e Voz',
  processamento_imagem: 'Processamento de Imagem',
  renderizacao: 'Renderização',
  concluido: 'Concluído',
  falhou: 'Falhou',
};
