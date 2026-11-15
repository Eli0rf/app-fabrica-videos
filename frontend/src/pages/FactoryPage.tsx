import { useState, useEffect, useCallback } from 'react';
import FactoryConveyor from '../components/FactoryConveyor';
import VideoQueue from '../components/VideoQueue';
import ErrorLog from '../components/ErrorLog';
import { createVideo, getVideoQueue, getVideoStatus } from '../services/api';
import type { VideoItem } from '../types';
import { Play, Loader2, TrendingUp, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

export default function FactoryPage() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<VideoItem | null>(null);
  const [ticker, setTicker] = useState('PETR4.SA');
  const [topic, setTopic] = useState('');
  const [autoUpload, setAutoUpload] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState(true);

  // Sugerencias de tickers
  const tickerSuggestions = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA',
    'ABEV3.SA', 'B3SA3.SA', '^BVSP', 'BTC-USD',
  ];

  // Carregar fila de videos
  const loadVideos = useCallback(async () => {
    try {
      const queue = await getVideoQueue();
      setVideos(queue);
      setApiOnline(true);

      // Atualizar video selecionado se existir
      if (selectedVideo) {
        const updated = queue.find((v) => v.id === selectedVideo.id);
        if (updated) {
          setSelectedVideo(updated);
        }
      }
    } catch {
      setApiOnline(false);
    }
  }, [selectedVideo]);

  // Polling da fila a cada 2 segundos
  useEffect(() => {
    loadVideos();
    const interval = setInterval(loadVideos, 2000);
    return () => clearInterval(interval);
  }, [loadVideos]);

  // Polling mais frequente do video selecionado (se estiver processando)
  useEffect(() => {
    if (!selectedVideo || selectedVideo.status !== 'processing') return;

    const interval = setInterval(async () => {
      try {
        const updated = await getVideoStatus(selectedVideo.id);
        setSelectedVideo(updated);
      } catch (err) {
        console.error('Erro ao buscar status:', err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [selectedVideo]);

  // Criar novo video
  const handleCreate = async () => {
    if (!ticker.trim()) return;
    setCreating(true);
    setError(null);
    try {
      const video = await createVideo(ticker.trim(), topic.trim() || undefined, autoUpload);
      setSelectedVideo(video);
      await loadVideos();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao criar video';
      setError(message);
    } finally {
      setCreating(false);
    }
  };

  // Erros agregados
  const allErrors = [
    ...(error ? [error] : []),
    ...(selectedVideo?.error_log ?? []),
  ];

  return (
    <div className="space-y-6">
      {/* Cabecalho */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Fabrica de Videos Dark</h1>
          <p className="text-sm text-dark-300 mt-1">
            Sistema autonomo de criacao de videos de financas
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={clsx(
              'w-2.5 h-2.5 rounded-full',
              apiOnline ? 'bg-accent-green animate-pulse' : 'bg-accent-red',
            )}
          />
          <span className="text-xs text-dark-300">
            {apiOnline ? 'Backend conectado' : 'Backend offline'}
          </span>
        </div>
      </div>

      {/* Alerta de erro global */}
      {allErrors.length > 0 && (
        <ErrorLog errors={allErrors} onClose={() => setError(null)} />
      )}

      {/* Painel de criacao */}
      <div className="dark-card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-accent-green" />
          Criar Novo Video
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Ticker */}
          <div>
            <label className="text-xs text-dark-200 uppercase tracking-wide mb-2 block">
              Ticker / Ativo
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="PETR4.SA"
              className="w-full bg-dark-900/60 border border-dark-600/50 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-purple"
            />
            <div className="flex gap-1 mt-2 flex-wrap">
              {tickerSuggestions.map((t) => (
                <button
                  key={t}
                  onClick={() => setTicker(t)}
                  className="text-xs px-2 py-0.5 rounded bg-dark-700/50 text-dark-200 hover:bg-dark-600 transition-colors"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Topico */}
          <div>
            <label className="text-xs text-dark-200 uppercase tracking-wide mb-2 block">
              Topico (opcional)
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Ex: Resultados do trimestre"
              className="w-full bg-dark-900/60 border border-dark-600/50 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-purple"
            />
          </div>

          {/* Botao criar */}
          <div className="flex items-end gap-2">
            <button
              onClick={handleCreate}
              disabled={creating || !ticker.trim()}
              className={clsx(
                'flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all',
                creating || !ticker.trim()
                  ? 'bg-dark-700 text-dark-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-accent-purple to-accent-blue text-white hover:opacity-90',
              )}
            >
              {creating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Criando...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Iniciar Producao
                </>
              )}
            </button>
          </div>
        </div>

        {/* Checkbox auto upload */}
        <div className="mt-4 flex items-center gap-2">
          <input
            type="checkbox"
            id="autoUpload"
            checked={autoUpload}
            onChange={(e) => setAutoUpload(e.target.checked)}
            className="rounded bg-dark-900 border-dark-600"
          />
          <label htmlFor="autoUpload" className="text-xs text-dark-200">
            Fazer upload automatico para YouTube apos renderizacao
          </label>
        </div>
      </div>

      {/* Esteira de producao */}
      <FactoryConveyor video={selectedVideo} />

      {/* Grid: Fila de renderizacao + detalhes do video selecionado */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <VideoQueue
          videos={videos}
          onSelectVideo={setSelectedVideo}
          selectedId={selectedVideo?.id ?? null}
          onRefresh={loadVideos}
        />

        {/* Detalhes do video selecionado */}
        <div className="dark-card p-6">
          <h2 className="text-lg font-bold text-white mb-4">Detalhes do Video</h2>

          {!selectedVideo ? (
            <div className="text-center py-8">
              <p className="text-dark-300 text-sm">Selecione um video da fila para ver detalhes</p>
            </div>
          ) : (
            <div className="space-y-3">
              {/* Info basica */}
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-dark-400 text-xs">ID</span>
                  <p className="text-white font-mono">{selectedVideo.id}</p>
                </div>
                <div>
                  <span className="text-dark-400 text-xs">Ticker</span>
                  <p className="text-white font-mono">{selectedVideo.ticker}</p>
                </div>
                <div>
                  <span className="text-dark-400 text-xs">Status</span>
                  <p className={clsx(
                    'font-semibold',
                    selectedVideo.status === 'error' ? 'text-accent-red' :
                    selectedVideo.status === 'ready' || selectedVideo.status === 'uploaded' ? 'text-accent-green' :
                    'text-accent-yellow'
                  )}>
                    {selectedVideo.status}
                  </p>
                </div>
                <div>
                  <span className="text-dark-400 text-xs">Estagio atual</span>
                  <p className="text-white">{selectedVideo.current_stage}</p>
                </div>
              </div>

              {/* Roteiro gerado */}
              {selectedVideo.script && (
                <div>
                  <span className="text-dark-400 text-xs uppercase tracking-wide">Roteiro</span>
                  <p className="text-sm text-gray-300 mt-1 p-3 bg-dark-900/60 rounded-lg max-h-32 overflow-y-auto">
                    {selectedVideo.script}
                  </p>
                </div>
              )}

              {/* Caminhos de saida */}
              {selectedVideo.video_path && (
                <div>
                  <span className="text-dark-400 text-xs uppercase tracking-wide">Video gerado</span>
                  <p className="text-xs text-accent-green font-mono mt-1 break-all">
                    {selectedVideo.video_path}
                  </p>
                </div>
              )}

              {selectedVideo.youtube_video_id && (
                <div className="p-2 rounded bg-accent-blue/10 border border-accent-blue/30">
                  <span className="text-xs text-accent-blue font-bold">
                    YouTube ID: {selectedVideo.youtube_video_id}
                  </span>
                </div>
              )}

              {/* Erros */}
              {selectedVideo.error_log.length > 0 && (
                <div>
                  <span className="text-accent-red text-xs uppercase tracking-wide flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Erros ({selectedVideo.error_log.length})
                  </span>
                  <div className="mt-1 space-y-1">
                    {selectedVideo.error_log.map((err, i) => (
                      <p key={i} className="text-xs text-red-300/70 font-mono p-2 bg-accent-red/5 rounded">
                        {err}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
