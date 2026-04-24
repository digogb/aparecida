import { useNavigate } from 'react-router-dom'
import type { DashboardRecent } from '../../types/dashboard'

export default function QuickActions({ recent }: { recent: DashboardRecent | undefined }) {
  const navigate = useNavigate()
  const oldest = recent?.pareceres
    .slice()
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())[0]
  const recentMov = recent?.movimentacoes[0]

  const actions = [
    {
      label: oldest ? (oldest.subject?.slice(0, 32) ?? 'Parecer pendente') : 'Ver pareceres',
      sub: 'Parecer mais antigo',
      onClick: () => (oldest ? navigate(`/pareceres/${oldest.id}`) : navigate('/pareceres')),
      dark: true,
    },
    {
      label: recentMov ? `Processo ${recentMov.process_number}` : 'Ver movimentações',
      sub: 'Movimentação recente',
      onClick: () => navigate('/movimentacoes'),
    },
    {
      label: 'Nova tarefa',
      sub: 'Adicionar ao kanban',
      onClick: () => navigate('/tarefas'),
    },
  ]

  return (
    <div className="flex flex-wrap gap-3">
      {actions.map((a) => (
        <button
          key={a.sub}
          type="button"
          onClick={a.onClick}
          className="rounded-xl px-5 py-3 text-left transition-all duration-150 hover:brightness-[0.95] active:scale-[0.98] cursor-pointer"
          style={
            a.dark
              ? { background: '#142038', color: '#FAF8F5' }
              : { background: '#FAF8F5', color: '#0A1120', border: '1.5px solid #E0D9CE' }
          }
        >
          <span className="text-base font-medium block truncate max-w-[240px]">{a.label}</span>
          <span className="text-sm block mt-0.5" style={{ opacity: 0.5 }}>{a.sub}</span>
        </button>
      ))}
    </div>
  )
}
