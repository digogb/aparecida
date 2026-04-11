import { useEffect, useState } from 'react'

export interface ToastMessage {
  id: number
  message: string
  type?: 'success' | 'info' | 'error'
}

type Listener = (msg: ToastMessage) => void
const listeners: Listener[] = []
let counter = 0

export function showToast(message: string, type: ToastMessage['type'] = 'info') {
  const toast: ToastMessage = { id: ++counter, message, type }
  listeners.forEach(fn => fn(toast))
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  useEffect(() => {
    const handler = (msg: ToastMessage) => {
      setToasts(prev => [...prev, msg])
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== msg.id)), 5000)
    }
    listeners.push(handler)
    return () => { const i = listeners.indexOf(handler); if (i >= 0) listeners.splice(i, 1) }
  }, [])

  if (toasts.length === 0) return null

  const bg: Record<string, string> = {
    success: '#2D5A27',
    info: '#142038',
    error: '#8B2332',
  }

  return (
    <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 pointer-events-none">
      {toasts.map(t => (
        <div
          key={t.id}
          className="px-4 py-3 rounded-xl text-sm font-medium shadow-lg pointer-events-auto"
          style={{ background: bg[t.type ?? 'info'], color: '#F5F0E8', maxWidth: 320 }}
        >
          {t.message}
        </div>
      ))}
    </div>
  )
}
