import { useNavigate } from 'react-router-dom'
import type { DashboardStats } from '../../types/dashboard'

interface CardDef {
  label: string
  value: number
  path: string
  tone: string
}

export default function MetricCards({ stats }: { stats: DashboardStats }) {
  const navigate = useNavigate()

  const cards: CardDef[] = [
    { label: 'Pareceres aguardando revisão', value: stats.aguardando_revisao, path: '/pareceres', tone: '#C9A94E' },
    { label: 'Movimentações não lidas', value: stats.movimentacoes_nao_lidas, path: '/movimentacoes', tone: '#6B6860' },
    { label: 'Tarefas urgentes',        value: stats.tarefas_urgentes,        path: '/tarefas',       tone: '#8B2332' },
  ]

  return (
    <div className="grid grid-cols-3 gap-3">
      {cards.map((card, i) => (
        <div
          key={card.label}
          onClick={() => navigate(card.path)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') navigate(card.path) }}
          className="animate-count rounded-xl overflow-hidden flex flex-col cursor-pointer hover:brightness-[0.97] transition-all duration-150"
          style={{
            animationDelay: `${i * 50}ms`,
            background: '#F5F0E8',
            border: '1.5px solid #E0D9CE',
          }}
        >
          <div className="h-1" style={{ background: card.tone }} />
          <div className="px-5 py-4 flex flex-col gap-1.5">
          <span
            className="font-display leading-none"
            style={{
              fontSize: 38,
              fontWeight: 500,
              color: card.tone,
              letterSpacing: '-0.03em',
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {card.value}
          </span>
          <span className="text-sm font-medium" style={{ color: '#6B6860' }}>{card.label}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
