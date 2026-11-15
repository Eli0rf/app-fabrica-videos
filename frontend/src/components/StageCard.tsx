import clsx from 'clsx';
import type { StageInfo } from '../types';
import { PIPELINE_STAGES } from '../types';

interface StageCardProps {
  stageIndex: number;
  stageInfo?: StageInfo;
  isActive: boolean;
  videoStatus: string;
}

export default function StageCard({
  stageIndex,
  stageInfo,
  isActive,
  videoStatus,
}: StageCardProps) {
  const stage = PIPELINE_STAGES[stageIndex];
  if (!stage) return null;

  const isCompleted = stageInfo?.progress === 1.0;
  const isError = stageInfo?.error !== null && stageInfo?.error !== undefined;
  const isProcessing = isActive && !isCompleted && !isError;

  // Cor do card baseada no estado
  const borderColor = isError
    ? 'border-accent-red/60'
    : isCompleted
      ? 'border-accent-green/50'
      : isProcessing
        ? 'border-accent-yellow/50'
        : 'border-dark-600/30';

  const bgColor = isError
    ? 'bg-accent-red/5'
    : isCompleted
      ? 'bg-accent-green/5'
      : isProcessing
        ? 'bg-accent-yellow/5'
        : 'bg-dark-800/40';

  return (
    <div
      className={clsx(
        'relative rounded-xl border p-4 transition-all duration-300 min-w-[180px]',
        borderColor,
        bgColor,
        isProcessing && 'animate-pulse-glow',
      )}
    >
      {/* Ícone do estágio */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">{stage.icon}</span>
        <div className="flex-1">
          <p className="text-xs text-dark-300 uppercase tracking-wide">
            Estágio {stageIndex + 1}
          </p>
          <h3 className="text-sm font-bold text-white">{stage.label}</h3>
        </div>
      </div>

      {/* Indicador de progresso */}
      <div className="space-y-2">
        <div className="h-1.5 bg-dark-700 rounded-full overflow-hidden">
          <div
            className={clsx(
              'h-full rounded-full transition-all duration-500',
              isError
                ? 'bg-accent-red'
                : isCompleted
                  ? 'bg-accent-green'
                  : 'bg-accent-yellow',
            )}
            style={{ width: `${(stageInfo?.progress ?? 0) * 100}%` }}
          />
        </div>

        {/* Estado do estágio */}
        <div className="flex items-center justify-between text-xs">
          {isProcessing && (
            <span className="text-accent-yellow flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-yellow animate-pulse" />
              Processando...
            </span>
          )}
          {isCompleted && (
            <span className="text-accent-green flex items-center gap-1">
              ✓ Concluído
            </span>
          )}
          {isError && (
            <span className="text-accent-red flex items-center gap-1">
              ✗ Erro
            </span>
          )}
          {!isProcessing && !isCompleted && !isError && (
            <span className="text-dark-400">Aguardando</span>
          )}

          {stageInfo?.progress !== undefined && stageInfo.progress > 0 && stageInfo.progress < 1 && (
            <span className="text-dark-300 font-mono">
              {Math.round(stageInfo.progress * 100)}%
            </span>
          )}
        </div>

        {/* Mensagem de erro */}
        {isError && stageInfo?.error && (
          <p className="text-xs text-accent-red/80 mt-2 line-clamp-2 break-words">
            {stageInfo.error}
          </p>
        )}
      </div>
    </div>
  );
}
