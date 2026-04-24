import { useQuery } from '@tanstack/react-query'
import { AlertTriangle } from 'lucide-react'
import NotificationBell from '../dje/NotificationBell'
import api from '../../services/api'

interface Props {
  onMenuToggle: () => void
}

export function Topbar({ onMenuToggle }: Props) {
  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  const { data: gmailStatus } = useQuery({
    queryKey: ['gmail-auth-status'],
    queryFn: async () => {
      const { data } = await api.get<{ status: string }>('/api/gmail/status')
      return data.status
    },
    staleTime: 60_000,
    refetchInterval: 5 * 60_000,
  })

  return (
    <>
    <header
      className="h-12 flex items-center px-4 flex-shrink-0 gap-2"
      style={{ background: '#EDE8DF', borderBottom: '1px solid #E0D9CE' }}
    >
      {/* Hamburger — só visível em mobile */}
      <button
        onClick={onMenuToggle}
        aria-label="Abrir menu de navegação"
        className="md:hidden p-1.5 rounded-lg transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>

      {/* Logo centralizada em mobile */}
      <span
        className="md:hidden flex-1 text-center font-display text-sm font-medium"
        style={{ color: '#142038' }}
      >
        Ione Advogados
      </span>

      {/* Spacer em desktop */}
      <div className="hidden md:block flex-1" />

      {/* Ações — sempre à direita */}
      <NotificationBell />
      <button
        onClick={handleLogout}
        className="text-sm transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
      >
        Sair
      </button>
    </header>
    {gmailStatus === 'token_revoked' && (
      <div
        className="flex items-center gap-2 px-6 py-2 text-sm flex-shrink-0"
        style={{ background: '#FEF3C7', borderBottom: '1px solid #D97706', color: '#92400E' }}
      >
        <AlertTriangle size={14} />
        <span>
          Conexão com Gmail expirada — o recebimento automático de e-mails está pausado.
          Reconecte nas configurações.
        </span>
      </div>
    )}
    </>
  )
}
