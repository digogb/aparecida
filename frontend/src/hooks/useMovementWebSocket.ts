import { useEffect, useRef, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'

interface WSMessage {
  type?: 'new_movement' | 'movement_updated' | 'ping'
  event?: 'movement.created' | 'peer_review.requested' | 'peer_review.completed'
  data?: unknown
}

export function useMovementWebSocket() {
  const queryClient = useQueryClient()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const shouldReconnect = useRef(true)

  const connect = useCallback(() => {
    const token = localStorage.getItem('token')
    if (!token) return

    const baseUrl = (import.meta.env.VITE_API_URL || window.location.origin)
      .replace(/^http/, 'ws')
    const url = `${baseUrl}/ws/movements?token=${encodeURIComponent(token)}`

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data)

          if (msg.type === 'new_movement' || msg.type === 'movement_updated' || msg.event === 'movement.created') {
            queryClient.invalidateQueries({ queryKey: ['movements'] })
            queryClient.invalidateQueries({ queryKey: ['movement-metrics'] })
            queryClient.invalidateQueries({ queryKey: ['notifications'] })
          }

          if (msg.event === 'peer_review.requested' || msg.event === 'peer_review.completed') {
            queryClient.invalidateQueries({ queryKey: ['app-notifications'] })
            queryClient.invalidateQueries({ queryKey: ['app-notifications-count'] })
            queryClient.invalidateQueries({ queryKey: ['dashboard', 'alerts'] })
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
