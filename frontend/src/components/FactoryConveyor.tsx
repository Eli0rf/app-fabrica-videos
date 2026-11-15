import StageCard from './StageCard';
import type { VideoItem } from '../types';
import { PIPELINE_STAGES } from '../types';
import clsx from 'clsx';

interface FactoryConveyorProps {
  video: VideoItem | null;
}

export default function FactoryConveyor({ video }: FactoryConveyorProps) {
  const stages = PIPELINE_STAGES;
  const currentStageIndex = video
    ? stages.findIndex((s) => s.id === video.current_stage)
    : -1;

  return (
    <div className="dark-card p-6 overflow-x-auto">
      <div className="flex items-center gap-2 mb-6">
        <h2 className="text-lg font-bold text-white">Esteira de Produção</h2>
        {video && (
          <span
            className={clsx(
              'px-2 py-0.5 rounded-full text-xs font-mono',
              video.status === 'error'
                ? 'bg-accent-red/20 text-accent-red'
                : video.status === 'ready' || video.status === 'uploaded'
                  ? 'bg-accent-green/20 text-accent-green'
                  : 'bg-accent-yellow/20 text-accent-yellow',
            )}
          >
            {video.ticker}
          </span>
        )}
      </div>

      {/* Esteira visual */}
      <div className="relative">
        {/* Linha da esteira (background) */}
        <div className="conveyor-belt h-2 rounded-full mb-4 opacity-60" />

        {/* Cards dos estágios */}
        <div className="flex gap-4 pb-4">
          {stages.map((stage, index) => {
            const stageInfo = video?.stages[index];
            const isActive = index === currentStageIndex && video?.status === 'processing';

            return (
              <div key={stage.id} className="flex items-center gap-4">
                {/* Card do estágio */}
                <StageCard
                  stageIndex={index}
                  stageInfo={stageInfo}
                  isActive={isActive}
                  videoStatus={video?.status ?? 'queued'}
                />

                {/* Seta de conexão entre estágios */}
                {index < stages.length - 1 && (
                  <div className="flex-shrink-0">
                    {isActive ? (
                      // Seta animada quando esta em processamento
                      <div className="animate-bounce-small">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                          <path d="M5 12h14M13 6l6 6-6 6" stroke="#ffd60a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                    ) : (
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path
                          d="M5 12h14M13 6l6 6-6 6"
                          stroke="#4a4a66"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Estado vazio */}
        {!video && (
          <div className="text-center py-12">
            <div className="text-5xl mb-4 opacity-30">🏭</div>
            <p className="text-dark-300 text-sm">
              A fábrica está parada. Crie um vídeo para iniciar a esteira de produção.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
