import { useState, useRef, useEffect } from 'react'
import { Bell } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useNotifications } from '../../hooks/useNotifications'
import { useMovementWebSocket } from '../../hooks/useMovementWebSocket'
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
  sentenca:     '#1B2838',
  despacho:     '#6B6860',
  acordao:      '#5B7553',
  publicacao:   '#C4953A',
  distribuicao: '#A69B8D',
  outros:       '#6B6860',
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const { notifications, count } = useNotifications()

  useMovementWebSocket()

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

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-lg transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
        aria-label="Notificações"
      >
        <Bell size={18} />
        {count > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center leading-none"
            style={{ background: '#8B2332', color: '#FAF8F5' }}>
            {count > 99 ? '99+' : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 rounded-xl z-50 overflow-hidden"
          style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2', boxShadow: '0 12px 40px rgba(27,40,56,0.12)' }}>
          <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: '1px solid #EBE8E2' }}>
            <span className="text-sm font-medium" style={{ color: '#2D2D3A' }}>
              Não lidas {count > 0 && `(${count})`}
            </span>
            <button
              onClick={handleViewAll}
              className="text-sm cursor-pointer"
              style={{ color: '#C4953A' }}
            >
              Ver todas
            </button>
          </div>

          <ul className="max-h-80 overflow-y-auto" style={{ borderColor: '#EBE8E2' }}>
            {notifications.length === 0 ? (
              <li className="px-4 py-6 text-center text-sm" style={{ color: '#A69B8D' }}>
                Nenhuma movimentação não lida
              </li>
            ) : (
              notifications.slice(0, 10).map((n) => {
                const color = TYPE_COLORS[n.type] ?? '#6B6860'
                return (
                  <li key={n.id} style={{ borderBottom: '1px solid #EBE8E2' }}>
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
                      <p className="text-sm font-medium truncate" style={{ color: '#2D2D3A' }}>
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

          {notifications.length > 10 && (
            <div className="px-4 py-2 text-center" style={{ borderTop: '1px solid #EBE8E2' }}>
              <button
                onClick={handleViewAll}
                className="text-sm cursor-pointer"
                style={{ color: '#C4953A' }}
              >
                +{notifications.length - 10} mais — ver todas
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
