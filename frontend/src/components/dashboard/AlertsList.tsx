import { useNavigate } from 'react-router-dom'
import type { DashboardAlert } from '../../types/dashboard'

const URGENCY_STYLES: Record<string, string> = {
  high: 'border-red-400 bg-red-50',
  medium: 'border-amber-400 bg-amber-50',
}

const TYPE_LABELS: Record<string, string> = {
  parecer_atrasado: 'Parecer Atrasado',
  intimacao_nao_lida: 'Intimação',
  prazo_proximo: 'Prazo',
}

const TYPE_BADGE: Record<string, string> = {
  parecer_atrasado: 'bg-red-100 text-red-700',
  intimacao_nao_lida: 'bg-red-100 text-red-700',
  prazo_proximo: 'bg-amber-100 text-amber-700',
}

interface AlertsListProps {
  alerts: DashboardAlert[]
}

export default function AlertsList({ alerts }: AlertsListProps) {
  const navigate = useNavigate()

  if (alerts.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-5 flex items-center gap-3">
        <span className="text-2xl">✓</span>
        <div>
          <p className="font-semibold text-green-800">Tudo em dia!</p>
          <p className="text-sm text-green-600">Nenhum alerta crítico no momento.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          onClick={() => alert.ref_path && navigate(alert.ref_path)}
          className={`border-l-4 rounded-r-xl p-4 flex items-start justify-between gap-3 ${URGENCY_STYLES[alert.urgency] ?? 'border-gray-300 bg-gray-50'} ${alert.ref_path ? 'cursor-pointer hover:brightness-95 transition-all' : ''}`}
        >
          <div className="flex flex-col gap-0.5 min-w-0">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${TYPE_BADGE[alert.type] ?? 'bg-gray-100 text-gray-600'}`}>
                {TYPE_LABELS[alert.type] ?? alert.type}
              </span>
              <span className="font-medium text-gray-900 text-sm truncate">{alert.title}</span>
            </div>
            <p className="text-sm text-gray-600 truncate">{alert.description}</p>
          </div>
          {alert.ref_path && (
            <span className="text-gray-400 text-xs shrink-0 mt-0.5">→</span>
          )}
        </div>
      ))}
    </div>
  )
}
