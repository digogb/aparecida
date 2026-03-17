import { useNavigate } from 'react-router-dom'
import type { DashboardAlert } from '../../types/dashboard'

const TYPE_CONFIG: Record<string, { label: string; color: string; dot: string }> = {
  parecer_atrasado: { label: 'Parecer Atrasado', color: '#DC2626', dot: '#EF4444' },
  intimacao_nao_lida: { label: 'Intimação',       color: '#DC2626', dot: '#EF4444' },
  prazo_proximo:      { label: 'Prazo',            color: '#D97706', dot: '#F59E0B' },
}

export default function AlertsList({ alerts }: { alerts: DashboardAlert[] }) {
  const navigate = useNavigate()

  if (alerts.length === 0) {
    return (
      <div className="flex items-center gap-4 rounded-2xl px-5 py-4 animate-fade-up"
        style={{ background: '#F0FDF9', border: '1px solid #6EE7B744' }}>
        <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
          style={{ background: '#D1FAE5' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div>
          <p className="font-semibold text-sm" style={{ color: '#065F46' }}>Tudo em dia</p>
          <p className="text-xs" style={{ color: '#059669' }}>Nenhum alerta crítico no momento.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {alerts.map((alert, i) => {
        const cfg = TYPE_CONFIG[alert.type] ?? { label: alert.type, color: '#6B7280', dot: '#9CA3AF' }
        return (
          <div key={alert.id} onClick={() => alert.ref_path && navigate(alert.ref_path)}
            className="animate-fade-up flex items-center gap-4 rounded-2xl px-5 py-3.5 transition-all"
            style={{
              animationDelay: `${i * 50}ms`,
              background: '#fff',
              border: `1px solid ${cfg.color}22`,
              borderLeft: `4px solid ${cfg.color}`,
              cursor: alert.ref_path ? 'pointer' : 'default',
            }}>
            <div className="w-2 h-2 rounded-full shrink-0" style={{ background: cfg.dot }} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wide" style={{ color: cfg.color }}>{cfg.label}</span>
                <span className="text-sm font-medium text-gray-800 truncate">{alert.title}</span>
              </div>
              <p className="text-xs text-gray-500 truncate mt-0.5">{alert.description}</p>
            </div>
            {alert.ref_path && (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            )}
          </div>
        )
      })}
    </div>
  )
}
