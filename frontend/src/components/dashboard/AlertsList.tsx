import { useNavigate } from 'react-router-dom'
import type { DashboardAlert } from '../../types/dashboard'

const TYPE_CONFIG: Record<string, { label: string; border: string; text: string }> = {
  parecer_atrasado:    { label: 'Atrasado', border: '#8B2332', text: '#8B2332' },
  prazo_proximo:       { label: 'Prazo',    border: '#C9A94E', text: '#A07A2E' },
  revisao_solicitada:  { label: 'Revisão',  border: '#142038', text: '#142038' },
}

const SUPPORTED_TYPES = new Set(Object.keys(TYPE_CONFIG))

export default function AlertsList({ alerts }: { alerts: DashboardAlert[] }) {
  const navigate = useNavigate()
  const filtered = alerts.filter((a) => SUPPORTED_TYPES.has(a.type))

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
            className={`rounded-xl flex items-center gap-4 px-5 py-3 overflow-hidden ${isClickable ? 'cursor-pointer hover:brightness-[0.97] transition-all duration-150' : ''}`}
            title={alert.description || alert.title}
            style={{
              background: '#FAF8F5',
              border: '1.5px solid #E0D9CE',
              borderLeft: `4px solid ${cfg.border}`,
            }}
          >
            <span className="text-sm font-semibold shrink-0" style={{ color: cfg.text, minWidth: 72 }}>
              {cfg.label}
            </span>
            <span className="text-base truncate flex-1 min-w-0" style={{ color: '#0A1120' }}>
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
