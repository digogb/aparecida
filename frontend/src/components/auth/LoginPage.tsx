import { useState, FormEvent } from 'react'
import api from '../../services/api'
import type { TokenResponse } from '../../types'

type Mode = 'login' | 'forgot' | 'reset'
const MIN = 8

const inputStyle = {
  background: '#FAF8F5',
  border: '1.5px solid #E0D9CE',
  color: '#0A1120',
  '--tw-ring-color': '#C9A94E',
} as React.CSSProperties

const inputClass = 'w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2'

export default function LoginPage() {
  // Se a URL trouxer ?reset_token=... (link do email), já entra no modo de redefinição.
  const resetToken = new URLSearchParams(window.location.search).get('reset_token') || ''
  const [mode, setMode] = useState<Mode>(resetToken ? 'reset' : 'login')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirm, setConfirm] = useState('')

  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [loading, setLoading] = useState(false)

  const resetMessages = () => {
    setError('')
    setInfo('')
  }

  const switchMode = (m: Mode) => {
    resetMessages()
    setMode(m)
  }

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault()
    resetMessages()
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

  const handleForgot = async (e: FormEvent) => {
    e.preventDefault()
    resetMessages()
    setLoading(true)
    try {
      await api.post('/api/auth/forgot-password', { email })
      setInfo('Se houver uma conta com esse email, enviamos um link de redefinição. Verifique sua caixa de entrada.')
    } catch {
      setError('Não foi possível enviar o email. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async (e: FormEvent) => {
    e.preventDefault()
    resetMessages()
    if (newPassword.length < MIN) {
      setError(`A nova senha deve ter ao menos ${MIN} caracteres`)
      return
    }
    if (newPassword !== confirm) {
      setError('A confirmação não confere com a nova senha')
      return
    }
    setLoading(true)
    try {
      await api.post('/api/auth/reset-password', { token: resetToken, new_password: newPassword })
      setInfo('Senha redefinida com sucesso. Você já pode entrar com a nova senha.')
      setMode('login')
      // Limpa o token da URL
      window.history.replaceState({}, '', '/login')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Link inválido ou expirado. Solicite um novo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(180deg, #0A1020 0%, #142038 60%, #1a2847 100%)' }}>
      <div className="rounded-xl shadow-sm p-8 w-full max-w-sm" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
        <h1 className="font-display mb-1" style={{ fontSize: 28, fontWeight: 500, color: '#C9A94E', lineHeight: 1.2 }}>Ione Advogados</h1>
        <p className="text-xs mb-1" style={{ color: '#C9A94E99', letterSpacing: '0.04em' }}>&amp; Associados</p>
        <p className="text-base mb-6" style={{ color: '#A69B8D' }}>
          {mode === 'login' && 'Faça login para continuar'}
          {mode === 'forgot' && 'Recuperar acesso'}
          {mode === 'reset' && 'Defina uma nova senha'}
        </p>

        {/* LOGIN */}
        {mode === 'login' && (
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Email</label>
              <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} style={inputStyle} placeholder="seu@email.com" />
            </div>
            <div>
              <label htmlFor="senha" className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Senha</label>
              <input id="senha" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className={inputClass} style={inputStyle} placeholder="••••••" />
            </div>
            {info && <p className="text-sm" style={{ color: '#1F7A4D' }}>{info}</p>}
            {error && <p role="alert" className="text-sm" style={{ color: '#8B2332' }}>{error}</p>}
            <button type="submit" disabled={loading} className="py-2.5 rounded-xl text-base font-medium disabled:opacity-50 transition-all duration-150 hover:brightness-[0.95] cursor-pointer" style={{ background: '#142038', color: '#FAF8F5' }}>
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
            <button type="button" onClick={() => switchMode('forgot')} className="text-sm text-center cursor-pointer hover:underline" style={{ color: '#6B6860' }}>
              Esqueci minha senha
            </button>
          </form>
        )}

        {/* FORGOT */}
        {mode === 'forgot' && (
          <form onSubmit={handleForgot} className="flex flex-col gap-4">
            <div>
              <label htmlFor="email-forgot" className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Email</label>
              <input id="email-forgot" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} style={inputStyle} placeholder="seu@email.com" />
            </div>
            {info && <p className="text-sm" style={{ color: '#1F7A4D' }}>{info}</p>}
            {error && <p role="alert" className="text-sm" style={{ color: '#8B2332' }}>{error}</p>}
            <button type="submit" disabled={loading} className="py-2.5 rounded-xl text-base font-medium disabled:opacity-50 transition-all duration-150 hover:brightness-[0.95] cursor-pointer" style={{ background: '#142038', color: '#FAF8F5' }}>
              {loading ? 'Enviando...' : 'Enviar link de redefinição'}
            </button>
            <button type="button" onClick={() => switchMode('login')} className="text-sm text-center cursor-pointer hover:underline" style={{ color: '#6B6860' }}>
              Voltar ao login
            </button>
          </form>
        )}

        {/* RESET */}
        {mode === 'reset' && (
          <form onSubmit={handleReset} className="flex flex-col gap-4">
            <div>
              <label htmlFor="nova" className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Nova senha</label>
              <input id="nova" type="password" required value={newPassword} onChange={(e) => setNewPassword(e.target.value)} className={inputClass} style={inputStyle} placeholder={`mínimo ${MIN} caracteres`} />
            </div>
            <div>
              <label htmlFor="confirma" className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Confirmar nova senha</label>
              <input id="confirma" type="password" required value={confirm} onChange={(e) => setConfirm(e.target.value)} className={inputClass} style={inputStyle} placeholder="••••••" />
            </div>
            {error && <p role="alert" className="text-sm" style={{ color: '#8B2332' }}>{error}</p>}
            <button type="submit" disabled={loading} className="py-2.5 rounded-xl text-base font-medium disabled:opacity-50 transition-all duration-150 hover:brightness-[0.95] cursor-pointer" style={{ background: '#142038', color: '#FAF8F5' }}>
              {loading ? 'Salvando...' : 'Redefinir senha'}
            </button>
            <button type="button" onClick={() => switchMode('login')} className="text-sm text-center cursor-pointer hover:underline" style={{ color: '#6B6860' }}>
              Voltar ao login
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
