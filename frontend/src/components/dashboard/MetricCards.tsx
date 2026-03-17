import { useNavigate } from 'react-router-dom'
import type { DashboardStats } from '../../types/dashboard'

interface CardDef {
  label: string; value: number; sub: string; path?: string
  accent: string; bg: string; textColor: string
}

export default function MetricCards({ stats }: { stats: DashboardStats }) {
  const navigate = useNavigate()
  const cards: CardDef[] = [
    { label: 'Pendentes',   value: stats.pareceres_pendentes,    sub: 'aguardando análise',   path: '/pareceres',     accent: '#D97706', bg: '#FFFBF0', textColor: '#92400E' },
    { label: 'Em Revisão',  value: stats.em_revisao,             sub: 'para revisar',          path: '/pareceres',     accent: '#4F46E5', bg: '#F5F3FF', textColor: '#3730A3' },
    { label: 'Não Lidas',   value: stats.movimentacoes_nao_lidas,sub: 'movimentações DJE',     path: '/movimentacoes', accent: '#DC2626', bg: '#FFF5F5', textColor: '#991B1B' },
    { label: 'Urgentes',    value: stats.tarefas_urgentes,       sub: 'tarefas prioritárias',  path: '/tarefas',       accent: '#DB2777', bg: '#FFF0F7', textColor: '#9D174D' },
    { label: 'Concluídos',  value: stats.concluidas_semana,      sub: 'esta semana',                                   accent: '#059669', bg: '#F0FDF9', textColor: '#065F46' },
    { label: 'Enviados',    value: stats.enviados_total,          sub: 'total histórico',       path: '/pareceres',     accent: '#0369A1', bg: '#F0F9FF', textColor: '#0C4A6E' },
  ]
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((card, i) => (
        <div key={card.label} onClick={() => card.path && navigate(card.path)}
          className="animate-count rounded-2xl overflow-hidden flex flex-col transition-transform hover:scale-[1.02]"
          style={{ background: card.bg, animationDelay: `${i * 60}ms`, cursor: card.path ? 'pointer' : 'default', border: `1px solid ${card.accent}33` }}>
          <div style={{ height: 3, background: card.accent }} />
          <div className="p-4 flex flex-col gap-1">
            <span className="font-display leading-none" style={{ fontSize: 42, fontWeight: 600, color: card.accent, letterSpacing: '-0.03em' }}>{card.value}</span>
            <span className="text-sm font-semibold" style={{ color: card.textColor }}>{card.label}</span>
            <span className="text-xs" style={{ color: card.textColor, opacity: 0.6 }}>{card.sub}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
