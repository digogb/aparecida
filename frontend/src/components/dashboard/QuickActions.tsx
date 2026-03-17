import { useNavigate } from 'react-router-dom'
import type { DashboardRecent } from '../../types/dashboard'

function ActionBtn({ icon, label, sub, onClick, primary }: {
  icon: React.ReactNode; label: string; sub: string; onClick: () => void; primary?: boolean
}) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-3 px-4 py-3 rounded-2xl text-left transition-all hover:scale-[1.01] flex-1 min-w-0"
      style={primary
        ? { background: '#1C1C2E', color: '#fff', border: '1px solid transparent' }
        : { background: '#fff', color: '#1C1C2E', border: '1px solid #E5E3DC' }
      }>
      <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
        style={{ background: primary ? 'rgba(255,255,255,0.1)' : '#F5F3EE' }}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-sm font-semibold truncate">{label}</p>
        <p className="text-xs truncate" style={{ opacity: 0.55 }}>{sub}</p>
      </div>
    </button>
  )
}

export default function QuickActions({ recent }: { recent: DashboardRecent | undefined }) {
  const navigate = useNavigate()
  const oldest = recent?.pareceres.slice().sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())[0]
  const recentMov = recent?.movimentacoes[0]

  return (
    <div className="flex flex-wrap gap-3">
      <ActionBtn primary
        icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>}
        label={oldest ? (oldest.subject?.slice(0, 28) ?? 'Parecer pendente') : 'Ver pareceres'}
        sub="Parecer mais antigo"
        onClick={() => oldest ? navigate(`/pareceres/${oldest.id}`) : navigate('/pareceres')}
      />
      <ActionBtn
        icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>}
        label={recentMov ? `Processo ${recentMov.process_number}` : 'Ver movimentações'}
        sub="Movimentação recente"
        onClick={() => navigate('/movimentacoes')}
      />
      <ActionBtn
        icon={<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>}
        label="Nova tarefa"
        sub="Adicionar ao kanban"
        onClick={() => navigate('/tarefas')}
      />
    </div>
  )
}
