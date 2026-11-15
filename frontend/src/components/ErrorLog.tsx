import { AlertTriangle, X, ScrollText } from 'lucide-react';
import { useState } from 'react';
import clsx from 'clsx';

interface ErrorLogProps {
  errors: string[];
  onClose?: () => void;
}

export default function ErrorLog({ errors, onClose }: ErrorLogProps) {
  const [expanded, setExpanded] = useState(true);

  if (errors.length === 0) return null;

  return (
    <div className="dark-card border-accent-red/40 bg-accent-red/5 p-4 animate-fade-in">
      {/* Cabecalho */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-accent-red animate-pulse" />
          <h3 className="text-sm font-bold text-accent-red">
            Log de Erros ({errors.length})
          </h3>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-dark-300 hover:text-white"
          >
            {expanded ? 'Recolher' : 'Expandir'}
          </button>
          {onClose && (
            <button onClick={onClose} className="text-dark-300 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Lista de erros */}
      {expanded && (
        <div className="space-y-2 max-h-[200px] overflow-y-auto">
          {errors.map((error, index) => (
            <div
              key={index}
              className={clsx(
                'flex items-start gap-2 p-2 rounded bg-dark-900/60 border border-accent-red/20',
              )}
            >
              <ScrollText className="w-3.5 h-3.5 text-accent-red flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-red-200/80 break-words font-mono">
                  <span className="text-dark-400">[{new Date().toLocaleTimeString('pt-BR')}]</span>{' '}
                  {error}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
