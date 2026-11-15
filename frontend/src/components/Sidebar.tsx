import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  Factory,
  LayoutDashboard,
  Film,
  Settings,
  AlertCircle,
} from 'lucide-react';
import ToggleSwitch from './ToggleSwitch';
import { getOperationMode, setOperationMode } from '../services/api';
import type { OperationMode } from '../types';
import clsx from 'clsx';

export default function Sidebar() {
  const [mode, setMode] = useState<OperationMode>('manual');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getOperationMode()
      .then(setMode)
      .catch(() => {});
  }, []);

  const handleToggleMode = async (newMode: OperationMode) => {
    setLoading(true);
    try {
      await setOperationMode(newMode);
      setMode(newMode);
    } catch (err) {
      console.error('Erro ao alterar modo:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-dark-900 border-r border-dark-700/50 flex flex-col z-50">
      {/* Logo / Titulo */}
      <div className="p-6 border-b border-dark-700/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center">
            <Factory className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Fabrica Dark</h1>
            <p className="text-xs text-dark-300">Videos de Financas</p>
          </div>
        </div>
      </div>

      {/* Navegacao */}
      <nav className="flex-1 p-4 space-y-2">
        <NavItem to="/" icon={<Film className="w-5 h-5" />} label="Fabrica de Videos" />
        <NavItem to="/dashboard" icon={<LayoutDashboard className="w-5 h-5" />} label="Dashboard" />
        <NavItem to="/" icon={<Settings className="w-5 h-5" />} label="Configuracoes" disabled />
      </nav>

      {/* Toggle de Modo de Operacao */}
      <div className="p-4 border-t border-dark-700/50 space-y-4">
        <div>
          <p className="text-xs font-semibold text-dark-200 uppercase tracking-wider mb-3">
            Modo de Operacao
          </p>

          <div className="bg-dark-800/60 rounded-lg p-3 border border-dark-600/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-300">
                {mode === 'manual' ? 'Aprovacao Manual' : 'Postagem Autonoma'}
              </span>
            </div>
            <ToggleSwitch
              checked={mode === 'autonomous'}
              onChange={(checked) => handleToggleMode(checked ? 'autonomous' : 'manual')}
              disabled={loading}
              labelOn="Autonomo"
              labelOff="Manual"
            />
            {mode === 'autonomous' && (
              <div className="mt-2 flex items-center gap-2 text-xs text-accent-orange">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Uploads automaticos ativos</span>
              </div>
            )}
          </div>
        </div>

        <div className="text-xs text-dark-400 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
          <span>Sistema online</span>
        </div>
      </div>
    </aside>
  );
}

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  disabled?: boolean;
}

function NavItem({ to, icon, label, disabled }: NavItemProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-sm',
          isActive
            ? 'bg-accent-purple/20 text-white border-l-2 border-accent-purple'
            : 'text-dark-200 hover:bg-dark-700/50 hover:text-white',
          disabled && 'opacity-40 cursor-not-allowed pointer-events-none',
        )
      }
    >
      {icon}
      <span className="font-medium">{label}</span>
    </NavLink>
  );
}
