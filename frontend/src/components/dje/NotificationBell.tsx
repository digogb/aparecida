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
        className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
        aria-label="Notificações"
      >
        <Bell size={18} />
        {count > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center leading-none">
            {count > 99 ? '99+' : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b">
            <span className="text-sm font-semibold text-gray-800">
              Não lidas {count > 0 && `(${count})`}
            </span>
            <button
              onClick={handleViewAll}
              className="text-xs text-blue-600 hover:underline"
            >
              Ver todas
            </button>
          </div>

          <ul className="max-h-80 overflow-y-auto divide-y divide-gray-100">
            {notifications.length === 0 ? (
              <li className="px-4 py-6 text-center text-sm text-gray-400">
                Nenhuma movimentação não lida
              </li>
            ) : (
              notifications.slice(0, 10).map((n) => (
                <li key={n.id}>
                  <button
                    className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
                    onClick={() => {
                      setOpen(false)
                      navigate('/movimentacoes')
                    }}
                  >
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-xs font-medium text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">
                        {TYPE_LABELS[n.type]}
                      </span>
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    </div>
                    <p className="text-xs font-medium text-gray-800 truncate">
                      {n.process?.number ?? '—'}
                    </p>
                    <p className="text-xs text-gray-500 truncate mt-0.5">{n.content}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {n.published_at ? new Date(n.published_at).toLocaleDateString('pt-BR') : '—'}
                    </p>
                  </button>
                </li>
              ))
            )}
          </ul>

          {notifications.length > 10 && (
            <div className="px-4 py-2 border-t text-center">
              <button
                onClick={handleViewAll}
                className="text-xs text-blue-600 hover:underline"
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
