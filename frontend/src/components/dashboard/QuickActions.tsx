import { useNavigate } from 'react-router-dom'
import type { DashboardRecent } from '../../types/dashboard'

interface QuickActionsProps {
  recent: DashboardRecent | undefined
}

export default function QuickActions({ recent }: QuickActionsProps) {
  const navigate = useNavigate()

  const oldestParecer = recent?.pareceres
    .slice()
    .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())[0]

  const recentMovement = recent?.movimentacoes[0]

  return (
    <div className="flex flex-wrap gap-3">
      <button
        onClick={() => oldestParecer ? navigate(`/pareceres/${oldestParecer.id}`) : navigate('/pareceres')}
        className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
      >
        <span>📄</span>
        <span>
          {oldestParecer
            ? `Parecer mais antigo${oldestParecer.subject ? ` — ${oldestParecer.subject.slice(0, 30)}` : ''}`
            : 'Ver pareceres'}
        </span>
      </button>

      <button
        onClick={() => navigate('/movimentacoes')}
        className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
      >
        <span>⚖️</span>
        <span>
          {recentMovement
            ? `Processo ${recentMovement.process_number}`
            : 'Ver movimentações'}
        </span>
      </button>

      <button
        onClick={() => navigate('/tarefas')}
        className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
      >
        <span>＋</span>
        <span>Criar tarefa</span>
      </button>
    </div>
  )
}
