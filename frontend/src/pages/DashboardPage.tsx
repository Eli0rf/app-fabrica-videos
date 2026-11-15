import { useState, useEffect, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, PieChart, Pie, Cell, Legend,
} from 'recharts';
import {
  Activity, DollarSign, Eye, Film, TrendingUp, AlertCircle,
  CheckCircle, XCircle, Cpu, HardDrive, Youtube,
} from 'lucide-react';
import { getDashboardMetrics, getSystemHealth } from '../services/api';
import type { DashboardMetrics, SystemHealth } from '../types';
import clsx from 'clsx';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [m, h] = await Promise.all([
        getDashboardMetrics(),
        getSystemHealth(),
      ]);
      setMetrics(m);
      setHealth(h);
    } catch (err) {
      console.error('Erro ao carregar dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading || !metrics || !health) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-dark-300">Carregando dashboard...</div>
      </div>
    );
  }

  // Dados para graficos
  const trendingData = metrics.trending_topics.map((t) => ({
    name: t.ticker,
    score: t.trend_score,
    change: t.change_percent,
    direction: t.direction,
  }));

  const statusData = [
    { name: 'Concluidos', value: metrics.completed_videos, color: '#00ff9d' },
    { name: 'Processando', value: metrics.processing_videos, color: '#ffd60a' },
    { name: 'Falhas', value: metrics.failed_videos, color: '#ff3366' },
  ].filter((d) => d.value > 0);

  // Dados mockados para grafico de views (ultimos 7 dias)
  const viewsData = Array.from({ length: 7 }, (_, i) => ({
    day: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'][i],
    views: Math.floor(Math.random() * 2000) + 500,
  }));

  const uptimeStr = formatUptime(metrics.uptime_seconds);

  return (
    <div className="space-y-6">
      {/* Cabecalho */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-dark-300 mt-1">
          Metricas, topicos em alta e saude do sistema
        </p>
      </div>

      {/* Cards de metricas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={<Film className="w-5 h-5" />}
          label="Total de Videos"
          value={metrics.total_videos.toString()}
          color="purple"
        />
        <MetricCard
          icon={<Eye className="w-5 h-5" />}
          label="Total de Views"
          value={metrics.total_views.toLocaleString('pt-BR')}
          color="blue"
        />
        <MetricCard
          icon={<DollarSign className="w-5 h-5" />}
          label={`AdSense (${metrics.adsense_currency})`}
          value={`R$ ${metrics.adsense_revenue.toFixed(2)}`}
          color="green"
        />
        <MetricCard
          icon={<Activity className="w-5 h-5" />}
          label="Uptime"
          value={uptimeStr}
          color="orange"
        />
      </div>

      {/* Grid principal: 2 colunas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Topicos em alta (2 colunas) */}
        <div className="lg:col-span-2 dark-card p-6">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-accent-green" />
            Topicos em Alta
          </h2>

          {trendingData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trendingData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a32" />
                <XAxis dataKey="name" stroke="#6e6e8c" fontSize={12} />
                <YAxis stroke="#6e6e8c" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0e0e20',
                    border: '1px solid #2a2a44',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="score" name="Trend Score" radius={[4, 4, 0, 0]}>
                  {trendingData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.direction === 'alta' ? '#00ff9d' : '#ff3366'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-dark-300 text-sm">
              Nenhum topico em alta disponivel. Verifique a conexao com o backend.
            </div>
          )}
        </div>

        {/* Status dos videos (1 coluna) */}
        <div className="dark-card p-6">
          <h2 className="text-lg font-bold text-white mb-4">Status dos Videos</h2>

          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0e0e20',
                    border: '1px solid #2a2a44',
                    borderRadius: '8px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-dark-300 text-sm">
              Nenhum video criado ainda.
            </div>
          )}

          {/* Resumo */}
          <div className="mt-4 space-y-2">
            <StatusRow label="Concluidos" value={metrics.completed_videos} color="green" />
            <StatusRow label="Processando" value={metrics.processing_videos} color="yellow" />
            <StatusRow label="Falhas" value={metrics.failed_videos} color="red" />
          </div>
        </div>
      </div>

      {/* Views dos ultimos 7 dias */}
      <div className="dark-card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Eye className="w-5 h-5 text-accent-blue" />
          Views - Ultimos 7 dias
        </h2>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={viewsData}>
            <defs>
              <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a32" />
            <XAxis dataKey="day" stroke="#6e6e8c" fontSize={12} />
            <YAxis stroke="#6e6e8c" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0e0e20',
                border: '1px solid #2a2a44',
                borderRadius: '8px',
              }}
            />
            <Area
              type="monotone"
              dataKey="views"
              stroke="#00d4ff"
              fillOpacity={1}
              fill="url(#colorViews)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Saude do sistema */}
      <div className="dark-card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-accent-purple" />
          Saude do Sistema
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <HealthIndicator
            label="ffmpeg"
            ok={health.ffmpeg_available}
            icon={<Film className="w-4 h-4" />}
          />
          <HealthIndicator
            label="edge-tts"
            ok={health.edge_tts_available}
            icon={<Activity className="w-4 h-4" />}
          />
          <HealthIndicator
            label="yfinance"
            ok={health.yfinance_available}
            icon={<TrendingUp className="w-4 h-4" />}
          />
          <HealthIndicator
            label="YouTube API"
            ok={health.youtube_authenticated}
            icon={<Youtube className="w-4 h-4" />}
          />
          <HealthIndicator
            label="Espaco em Disco"
            ok={health.disk_space_mb > 1000}
            icon={<HardDrive className="w-4 h-4" />}
            value={`${(health.disk_space_mb / 1024).toFixed(1)} GB`}
          />
          <HealthIndicator
            label="Jobs Ativos"
            ok={health.active_jobs >= 0}
            icon={<Cpu className="w-4 h-4" />}
            value={health.active_jobs.toString()}
          />
        </div>

        {/* Status geral */}
        <div className="mt-4 flex items-center gap-2">
          {health.status === 'healthy' ? (
            <>
              <CheckCircle className="w-5 h-5 text-accent-green" />
              <span className="text-accent-green font-semibold">Sistema saudavel</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-accent-yellow" />
              <span className="text-accent-yellow font-semibold">Sistema degradado - algumas dependencias nao estao disponiveis</span>
            </>
          )}
        </div>
      </div>

      {/* AdSense */}
      <div className="dark-card p-6">
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-accent-green" />
          Status do AdSense
        </h2>
        <div className="flex items-center justify-between p-4 bg-dark-900/60 rounded-lg">
          <div>
            <p className="text-sm text-dark-300">
              Dados do AdSense sao simulados (mocked).
            </p>
            <p className="text-xs text-dark-400 mt-1">
              Para dados reais, integre a YouTube Analytics API.
            </p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-accent-green">
              R$ {metrics.adsense_revenue.toFixed(2)}
            </p>
            <p className="text-xs text-dark-400">{metrics.adsense_currency} - Estimado</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// === Componentes auxiliares ===

function MetricCard({
  icon, label, value, color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: 'purple' | 'blue' | 'green' | 'orange';
}) {
  const colorMap = {
    purple: 'from-accent-purple/20 to-accent-purple/5 text-accent-purple',
    blue: 'from-accent-blue/20 to-accent-blue/5 text-accent-blue',
    green: 'from-accent-green/20 to-accent-green/5 text-accent-green',
    orange: 'from-accent-orange/20 to-accent-orange/5 text-accent-orange',
  };

  return (
    <div className={clsx('dark-card p-4 bg-gradient-to-br', colorMap[color])}>
      <div className="flex items-center justify-between">
        <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
          {icon}
        </div>
      </div>
      <p className="text-2xl font-bold text-white mt-3">{value}</p>
      <p className="text-xs text-dark-300 mt-1">{label}</p>
    </div>
  );
}

function StatusRow({
  label, value, color,
}: {
  label: string;
  value: number;
  color: 'green' | 'yellow' | 'red';
}) {
  const colorMap = {
    green: 'text-accent-green',
    yellow: 'text-accent-yellow',
    red: 'text-accent-red',
  };

  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-dark-300">{label}</span>
      <span className={clsx('font-bold', colorMap[color])}>{value}</span>
    </div>
  );
}

function HealthIndicator({
  label, ok, icon, value,
}: {
  label: string;
  ok: boolean;
  icon: React.ReactNode;
  value?: string;
}) {
  return (
    <div className="flex flex-col items-center gap-1 p-3 rounded-lg bg-dark-900/40 border border-dark-600/30">
      <div className={clsx('w-8 h-8 rounded-full flex items-center justify-center', ok ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red')}>
        {ok ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
      </div>
      <span className="text-xs text-dark-200 font-medium">{label}</span>
      {value && <span className="text-xs text-dark-400 font-mono">{value}</span>}
    </div>
  );
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}
