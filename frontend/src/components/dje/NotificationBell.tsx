import { useState, useRef, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useNotifications } from '../../hooks/useNotifications'
import { useMovementWebSocket } from '../../hooks/useMovementWebSocket'
import { useParecerWebSocket } from '../../hooks/useParecerWebSocket'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchAppNotifications,
  fetchUnreadNotificationCount,
  markNotificationRead,
} from '../../services/editorApi'
import type { AppNotification } from '../../services/editorApi'
import type { MovementType } from '../../types/movement'

const TYPE_LABELS: Record<MovementType, string> = {
  intimacao: 'Intimação',
  sentenca: 'Sentença',
  despacho: 'Despacho',
  acordao: 'Acórdão',
  publicacao: 'Publicação',
  distribuicao: 'Distribuição',
  outros: 'Outros',
}

const TYPE_COLORS: Record<MovementType, string> = {
  intimacao:    '#8B2332',
  sentenca:     '#142038',
  despacho:     '#6B6860',
  acordao:      '#5B7553',
  publicacao:   '#C9A94E',
  distribuicao: '#A69B8D',
  outros:       '#6B6860',
}

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return 'agora'
  if (mins < 60) return `${mins}min`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h`
  const days = Math.floor(hours / 24)
  return `${days}d`
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { notifications: movementNotifs, count: movementCount } = useNotifications()

  useMovementWebSocket()
  useParecerWebSocket()

  // Notificações genéricas (peer review, etc.)
  const { data: appNotifs = [] } = useQuery({
    queryKey: ['app-notifications'],
    queryFn: () => fetchAppNotifications(20, 0),
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

  const { data: appUnreadCount = 0 } = useQuery({
    queryKey: ['app-notifications-count'],
    queryFn: fetchUnreadNotificationCount,
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

  // Filtrar apenas notificações não lidas de peer review
  const peerReviewNotifs = appNotifs.filter(
    (n) => n.metadata_?.type === 'peer_review' && n.status !== 'read'
  )

  const totalCount = movementCount + peerReviewNotifs.length

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  function handleViewAll() {
    setOpen(false)
    navigate('/movimentacoes')
  }

  async function handlePeerReviewClick(notif: AppNotification) {
    setOpen(false)
    // Marcar como lida
    if (notif.status !== 'read') {
      try {
        await markNotificationRead(notif.id)
        queryClient.invalidateQueries({ queryKey: ['app-notifications'] })
        queryClient.invalidateQueries({ queryKey: ['app-notifications-count'] })
      } catch (err) {
        console.error('Mark read failed:', err)
      }
    }
    // Navegar para o parecer
    if (notif.link) {
      navigate(notif.link)
    }
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-lg transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
        aria-label="Notificações"
      >
        <Bell size={18} />
        {totalCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center leading-none"
            style={{ background: '#8B2332', color: '#FAF8F5' }}>
            {totalCount > 99 ? '99+' : totalCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 rounded-xl z-50 overflow-hidden"
          style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', boxShadow: '0 12px 40px rgba(27,40,56,0.12)' }}>
          <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: '1px solid #EDE8DF' }}>
            <span className="text-sm font-medium" style={{ color: '#0A1120' }}>
              Não lidas {totalCount > 0 && `(${totalCount})`}
            </span>
            <button
              onClick={handleViewAll}
              className="text-sm cursor-pointer"
              style={{ color: '#C9A94E' }}
            >
              Ver todas
            </button>
          </div>

          <ul className="max-h-80 overflow-y-auto" style={{ borderColor: '#EDE8DF' }}>
            {/* Notificações de peer review */}
            {peerReviewNotifs.map((n) => (
              <li key={n.id} style={{ borderBottom: '1px solid #EDE8DF' }}>
                <button
                  className="w-full text-left px-4 py-3 transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
                  onClick={() => handlePeerReviewClick(n)}
                >
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-xs font-medium px-2 py-0.5 rounded-lg"
                      style={{ background: '#14203818', color: '#142038' }}>
                      Revisão
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#142038' }} />
                    <span className="text-xs ml-auto" style={{ color: '#A69B8D' }}>
                      {formatTimeAgo(n.created_at)}
                    </span>
                  </div>
                  <p className="text-sm font-medium truncate" style={{ color: '#0A1120' }}>
                    {n.title}
                  </p>
                  {n.body && (
                    <p className="text-sm truncate mt-0.5" style={{ color: '#A69B8D' }}>{n.body}</p>
                  )}
                </button>
              </li>
            ))}

            {/* Notificações de movimentações */}
            {movementNotifs.length === 0 && peerReviewNotifs.length === 0 ? (
              <li className="px-4 py-6 text-center text-sm" style={{ color: '#A69B8D' }}>
                Nenhuma notificação não lida
              </li>
            ) : (
              movementNotifs.slice(0, 10).map((n) => {
                const color = TYPE_COLORS[n.type] ?? '#6B6860'
                return (
                  <li key={n.id} style={{ borderBottom: '1px solid #EDE8DF' }}>
                    <button
                      className="w-full text-left px-4 py-3 transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
                      onClick={() => {
                        setOpen(false)
                        navigate('/movimentacoes')
                      }}
                    >
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-xs font-medium px-2 py-0.5 rounded-lg"
                          style={{ background: `${color}18`, color }}>
                          {TYPE_LABELS[n.type]}
                        </span>
                        <span className="w-1.5 h-1.5 rounded-full" style={{ background: color }} />
                      </div>
                      <p className="text-sm font-medium truncate" style={{ color: '#0A1120' }}>
                        {n.process?.number ?? '—'}
                      </p>
                      <p className="text-sm truncate mt-0.5" style={{ color: '#A69B8D' }}>{n.content}</p>
                      <p className="text-sm mt-0.5" style={{ color: '#A69B8D' }}>
                        {n.published_at ? new Date(n.published_at).toLocaleDateString('pt-BR') : '—'}
                      </p>
                    </button>
                  </li>
                )
              })
            )}
          </ul>

          {(movementNotifs.length > 10 || peerReviewNotifs.length > 0) && (
            <div className="px-4 py-2 text-center" style={{ borderTop: '1px solid #EDE8DF' }}>
              <button
                onClick={handleViewAll}
                className="text-sm cursor-pointer"
                style={{ color: '#C9A94E' }}
              >
                Ver todas
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
