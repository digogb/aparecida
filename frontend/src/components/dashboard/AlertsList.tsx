import { useNavigate } from 'react-router-dom'
import type { DashboardAlert } from '../../types/dashboard'

const TYPE_CONFIG: Record<string, { label: string; border: string; text: string }> = {
  parecer_atrasado: { label: 'Atrasado', border: '#8B2332', text: '#8B2332' },
  prazo_proximo:    { label: 'Prazo',    border: '#C4953A', text: '#A07A2E' },
}

export default function AlertsList({ alerts }: { alerts: DashboardAlert[] }) {
  const navigate = useNavigate()
  const filtered = alerts.filter((a) => a.type === 'parecer_atrasado' || a.type === 'prazo_proximo')

  if (filtered.length === 0) {
    return (
      <p className="text-base py-1" style={{ color: '#5B7553' }}>
        Nenhum alerta no momento.
      </p>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {filtered.map((alert) => {
        const cfg = TYPE_CONFIG[alert.type] ?? { label: alert.type, border: '#A69B8D', text: '#8C8A82' }
        const isClickable = !!alert.ref_path

        return (
          <div
            key={alert.id}
            onClick={() => isClickable && navigate(alert.ref_path!)}
            role={isClickable ? 'button' : undefined}
            tabIndex={isClickable ? 0 : undefined}
            onKeyDown={(e) => { if (isClickable && (e.key === 'Enter' || e.key === ' ')) navigate(alert.ref_path!) }}
            className={`rounded-xl flex items-center gap-4 px-5 py-3 ${isClickable ? 'cursor-pointer hover:brightness-[0.97] transition-all duration-150' : ''}`}
            style={{
              background: '#FAF8F5',
              border: '1.5px solid #DDD9D2',
              borderLeft: `4px solid ${cfg.border}`,
            }}
          >
            <span className="text-sm font-semibold shrink-0" style={{ color: cfg.text, minWidth: 72 }}>
              {cfg.label}
            </span>
            <span className="text-base truncate" style={{ color: '#2D2D3A' }}>
              {alert.title}
            </span>
            {alert.description && (
              <span className="text-sm truncate hidden sm:block ml-auto shrink-0" style={{ color: '#A69B8D' }}>
                {alert.description}
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}
