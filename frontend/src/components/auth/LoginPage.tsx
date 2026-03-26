import { useState, FormEvent } from 'react'
import api from '../../services/api'
import type { TokenResponse } from '../../types'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post<TokenResponse>('/api/auth/login', { email, password })
      localStorage.setItem('token', data.access_token)
      window.location.replace('/')
    } catch {
      setError('Email ou senha inválidos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0A1020 0%, #142038 60%, #1a2847 100%)' }}>
      <div className="rounded-xl shadow-sm p-8 w-full max-w-sm" style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE' }}>
        <h1 className="font-display mb-1" style={{ fontSize: 28, fontWeight: 500, color: '#C9A94E', lineHeight: 1.2 }}>Ione Advogados</h1>
        <p className="text-xs mb-1" style={{ color: '#C9A94E99', letterSpacing: '0.04em' }}>&amp; Associados</p>
        <p className="text-base mb-6" style={{ color: '#A69B8D' }}>Faça login para continuar</p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
              style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Senha</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
              style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              placeholder="••••••"
            />
          </div>
          {error && <p className="text-sm" style={{ color: '#8B2332' }}>{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="py-2.5 rounded-xl text-base font-medium disabled:opacity-50 transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
            style={{ background: '#142038', color: '#F5F0E8' }}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}
