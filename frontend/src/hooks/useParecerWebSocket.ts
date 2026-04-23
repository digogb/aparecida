import { useCallback, useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'

interface WSMessage {
  event?:
    | 'parecer.created'
    | 'parecer.classified'
    | 'parecer.generated'
    | 'parecer.devolvido'
    | 'parecer.error'
  data?: { id?: string; status?: string }
}

export function useParecerWebSocket() {
  const queryClient = useQueryClient()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const shouldReconnect = useRef(true)

  const connect = useCallback(() => {
    const token = localStorage.getItem('token')
    if (!token) return

    const baseUrl = (import.meta.env.VITE_API_URL || window.location.origin)
      .replace(/^http/, 'ws')
    const url = `${baseUrl}/ws/pareceres?token=${encodeURIComponent(token)}`

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data)
          if (!msg.event) return

          queryClient.invalidateQueries({ queryKey: ['pareceres'] })
          queryClient.invalidateQueries({ queryKey: ['pareceres-metrics'] })
          queryClient.invalidateQueries({ queryKey: ['dashboard', 'pareceres-overview'] })

          if (msg.data?.id) {
            queryClient.invalidateQueries({ queryKey: ['parecer', msg.data.id] })
          }
        } catch {
          // ignore parse errors
        }
      }

      ws.onclose = () => {
        wsRef.current = null
        if (shouldReconnect.current) {
          reconnectTimer.current = setTimeout(connect, 5_000)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    } catch {
      // WebSocket not available, skip
    }
  }, [queryClient])

  useEffect(() => {
    shouldReconnect.current = true
    connect()

    return () => {
      shouldReconnect.current = false
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])
}
