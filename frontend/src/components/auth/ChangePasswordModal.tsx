import { useState, FormEvent } from 'react'
import { X } from 'lucide-react'
import api from '../../services/api'

interface Props {
  onClose: () => void
}

const MIN = 8

export default function ChangePasswordModal({ onClose }: Props) {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const inputStyle = {
    background: '#FAF8F5',
    border: '1.5px solid #E0D9CE',
    color: '#0A1120',
    '--tw-ring-color': '#C9A94E',
  } as React.CSSProperties

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (next.length < MIN) {
      setError(`A nova senha deve ter ao menos ${MIN} caracteres`)
      return
    }
    if (next !== confirm) {
      setError('A confirmação não confere com a nova senha')
      return
    }
    setLoading(true)
    try {
      await api.post('/api/auth/change-password', {
        current_password: current,
        new_password: next,
      })
      setSuccess(true)
      setTimeout(onClose, 1500)
    } catch (err: any) {
      // 400 = senha atual incorreta / política — NÃO desloga (só 401 deslogaria)
      setError(err?.response?.data?.detail || 'Não foi possível trocar a senha')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(10, 16, 32, 0.55)' }}
      onClick={onClose}
    >
      <div
        className="rounded-xl shadow-lg p-6 w-full max-w-sm relative"
        style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          aria-label="Fechar"
          className="absolute top-3 right-3 p-1 rounded-lg cursor-pointer transition-all hover:brightness-95"
          style={{ color: '#6B6860' }}
        >
          <X size={18} />
        </button>
        <h2 className="font-display mb-4" style={{ fontSize: 20, fontWeight: 500, color: '#142038' }}>
          Trocar senha
        </h2>

        {success ? (
          <p className="text-sm" style={{ color: '#1F7A4D' }}>
            Senha alterada com sucesso.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Senha atual</label>
              <input
                type="password"
                required
                value={current}
                onChange={(e) => setCurrent(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={inputStyle}
                placeholder="••••••"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Nova senha</label>
              <input
                type="password"
                required
                value={next}
                onChange={(e) => setNext(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={inputStyle}
                placeholder={`mínimo ${MIN} caracteres`}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Confirmar nova senha</label>
              <input
                type="password"
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={inputStyle}
                placeholder="••••••"
              />
            </div>
            {error && <p role="alert" className="text-sm" style={{ color: '#8B2332' }}>{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="py-2.5 rounded-xl text-base font-medium disabled:opacity-50 transition-all duration-150 hover:brightness-[0.95] cursor-pointer mt-1"
              style={{ background: '#142038', color: '#FAF8F5' }}
            >
              {loading ? 'Salvando...' : 'Salvar nova senha'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
