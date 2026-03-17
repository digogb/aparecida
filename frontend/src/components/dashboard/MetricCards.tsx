import { useNavigate } from 'react-router-dom'
import type { DashboardStats } from '../../types/dashboard'

interface MetricCardProps {
  label: string
  value: number
  color: string
  path?: string
  subtitle?: string
}

function MetricCard({ label, value, color, path, subtitle }: MetricCardProps) {
  const navigate = useNavigate()
  return (
    <div
      onClick={() => path && navigate(path)}
      className={`bg-white rounded-xl border border-gray-100 p-5 shadow-sm flex flex-col gap-1 ${path ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
    >
      <span className="text-sm text-gray-500 font-medium">{label}</span>
      <span className={`text-3xl font-bold ${color}`}>{value}</span>
      {subtitle && <span className="text-xs text-gray-400">{subtitle}</span>}
    </div>
  )
}

interface MetricCardsProps {
  stats: DashboardStats
}

export default function MetricCards({ stats }: MetricCardsProps) {
  const cards: MetricCardProps[] = [
    {
      label: 'Pendentes',
      value: stats.pareceres_pendentes,
      color: 'text-amber-600',
      path: '/pareceres',
      subtitle: 'aguardando análise',
    },
    {
      label: 'Em Revisão',
      value: stats.em_revisao,
      color: 'text-blue-600',
      path: '/pareceres',
      subtitle: 'pareceres para revisar',
    },
    {
      label: 'Não Lidas',
      value: stats.movimentacoes_nao_lidas,
      color: 'text-red-600',
      path: '/movimentacoes',
      subtitle: 'movimentações DJE',
    },
    {
      label: 'Urgentes',
      value: stats.tarefas_urgentes,
      color: 'text-rose-600',
      path: '/tarefas',
      subtitle: 'tarefas prioritárias',
    },
    {
      label: 'Concluídos',
      value: stats.concluidas_semana,
      color: 'text-green-600',
      subtitle: 'esta semana',
    },
    {
      label: 'Enviados',
      value: stats.enviados_total,
      color: 'text-gray-600',
      path: '/pareceres',
      subtitle: 'total',
    },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card) => (
        <MetricCard key={card.label} {...card} />
      ))}
    </div>
  )
}
