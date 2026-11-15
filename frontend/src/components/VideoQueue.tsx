import clsx from 'clsx';
import type { VideoItem } from '../types';
import { STAGE_LABELS } from '../types';
import { Upload, Trash2, Film, Clock } from 'lucide-react';
import { useState } from 'react';
import { uploadToYouTube, deleteVideo } from '../services/api';

interface VideoQueueProps {
  videos: VideoItem[];
  onSelectVideo: (video: VideoItem) => void;
  selectedId: string | null;
  onRefresh: () => void;
}

export default function VideoQueue({ videos, onSelectVideo, selectedId, onRefresh }: VideoQueueProps) {
  const [uploading, setUploading] = useState<string | null>(null);

  const handleUpload = async (e: React.MouseEvent, videoId: string) => {
    e.stopPropagation();
    setUploading(videoId);
    try {
      await uploadToYouTube(videoId);
      onRefresh();
    } catch (err) {
      console.error('Erro no upload:', err);
    } finally {
      setUploading(null);
    }
  };

  const handleDelete = async (e: React.MouseEvent, videoId: string) => {
    e.stopPropagation();
    try {
      await deleteVideo(videoId);
      onRefresh();
    } catch (err) {
      console.error('Erro ao deletar:', err);
    }
  };

  const statusConfig: Record<string, { label: string; color: string; dot: string }> = {
    queued: { label: 'Na fila', color: 'text-dark-300', dot: 'status-dot queued' },
    processing: { label: 'Processando', color: 'text-accent-yellow', dot: 'status-dot processing' },
    ready: { label: 'Pronto', color: 'text-accent-green', dot: 'status-dot ready' },
    uploaded: { label: 'Enviado', color: 'text-accent-blue', dot: 'status-dot ready' },
    error: { label: 'Erro', color: 'text-accent-red', dot: 'status-dot error' },
  };

  return (
    <div className="dark-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-white">Fila de Renderizacao</h2>
        <span className="text-sm text-dark-300">{videos.length} videos</span>
      </div>

      {videos.length === 0 ? (
        <div className="text-center py-8">
          <Film className="w-12 h-12 mx-auto text-dark-400 mb-2 opacity-50" />
          <p className="text-dark-300 text-sm">Nenhum video na fila</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {videos.map((video) => {
            const config = statusConfig[video.status] ?? statusConfig.queued;
            const isSelected = video.id === selectedId;
            const hasErrors = video.error_log.length > 0;

            return (
              <div
                key={video.id}
                onClick={() => onSelectVideo(video)}
                className={clsx(
                  'p-3 rounded-lg border cursor-pointer transition-all',
                  isSelected
                    ? 'border-accent-purple/50 bg-accent-purple/10'
                    : 'border-dark-600/30 bg-dark-800/40 hover:border-dark-500',
                  hasErrors && 'border-accent-red/30',
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {/* Status dot */}
                    <div className={config.dot} />

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm text-white font-bold">{video.ticker}</span>
                        <span className={clsx('text-xs', config.color)}>{config.label}</span>
                      </div>
                      <p className="text-xs text-dark-400 truncate">
                        {STAGE_LABELS[video.current_stage] ?? video.current_stage}
                      </p>
                    </div>

                    {/* Tempo */}
                    <div className="text-xs text-dark-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(video.created_at).toLocaleTimeString('pt-BR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>

                  {/* Acoes */}
                  <div className="flex items-center gap-1 ml-2">
                    {video.status === 'ready' && !video.youtube_video_id && (
                      <button
                        onClick={(e) => handleUpload(e, video.id)}
                        disabled={uploading === video.id}
                        className="p-1.5 rounded hover:bg-accent-blue/20 text-accent-blue transition-colors"
                        title="Upload para YouTube"
                      >
                        <Upload className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={(e) => handleDelete(e, video.id)}
                      className="p-1.5 rounded hover:bg-accent-red/20 text-accent-red transition-colors"
                      title="Remover"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Alerta de erro */}
                {hasErrors && (
                  <div className="mt-2 px-2 py-1.5 rounded bg-accent-red/10 border border-accent-red/30">
                    <p className="text-xs text-accent-red flex items-center gap-1">
                      <span className="font-bold">!</span>
                      {video.error_log[video.error_log.length - 1]}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
