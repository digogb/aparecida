import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../services/api'
import type { User } from '../../types'
import { useDashboardStats, useDashboardAlerts, useDashboardRecent } from '../../hooks/useDashboard'
import MetricCards from './MetricCards'
import AlertsList from './AlertsList'

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
}

function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => { const { data } = await api.get<User>('/api/auth/me'); return data },
    staleTime: 5 * 60_000,
  })
}

const STATUS_TONE: Record<string, { label: string; color: string }> = {
  pendente:     { label: 'Pendente',           color: '#C9A94E' },
  classificado: { label: 'Pendente',           color: '#C9A94E' },
  gerado:       { label: 'Aguardando revisão', color: '#A69B8D' },
  em_correcao:  { label: 'Em correção',        color: '#D97706' },
  em_revisao:   { label: 'Aguardando revisão', color: '#A69B8D' },
  devolvido:    { label: 'Devolvido',          color: '#8B2332' },
  aprovado:     { label: 'Aprovado',           color: '#5B7553' },
  enviado:      { label: 'Enviado',            color: '#8C8A82' },
}

const MOV_TYPE: Record<string, string> = {
  intimacao: 'Intimação', sentenca: 'Sentença', despacho: 'Despacho',
  acordao: 'Acórdão', publicacao: 'Publicação', distribuicao: 'Distribuição', outros: 'Outros',
}

const MOV_COLOR: Record<string, string> = {
  intimacao: '#8B2332', sentenca: '#142038', despacho: '#6B6860',
  acordao: '#5B7553', publicacao: '#C9A94E', distribuicao: '#A69B8D', outros: '#6B6860',
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const { data: stats, isLoading: statsLoading } = useDashboardStats()
  const { data: alertsData, isLoading: alertsLoading } = useDashboardAlerts()
  const { data: recent, isLoading: recentLoading } = useDashboardRecent()

  const firstName = user?.name?.split(' ')[0] ?? 'Advogado'
  const isAdvogado = user?.role === 'advogado' || user?.role === 'admin'
  const today = new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })

  const VISIBLE_TYPES = new Set(['parecer_atrasado', 'prazo_proximo', 'revisao_solicitada'])
  const allAlerts = (alertsData?.alerts ?? []).filter((a) => VISIBLE_TYPES.has(a.type))
  const hasAlerts = !alertsLoading && allAlerts.length > 0

  return (
    <div className="min-h-full px-6 py-8 space-y-8" style={{ background: '#FAF8F5' }}>

      {/* Header */}
      <header className="animate-fade-up">
        <p className="text-sm font-medium uppercase tracking-widest mb-0.5" style={{ color: '#A69B8D' }}>
          {getGreeting()}
        </p>
        <div className="flex items-baseline justify-between">
          <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: '#142038', letterSpacing: '-0.02em' }}>
            {isAdvogado ? `Dr. ${firstName}` : firstName}
          </h1>
          <p className="text-base capitalize" style={{ color: '#A69B8D' }}>{today}</p>
        </div>
      </header>

      {/* Metrics — only actionable */}
      <section className="animate-fade-up" style={{ animationDelay: '60ms' }}>
        {statsLoading ? (
          <div className="grid grid-cols-3 gap-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-xl px-5 py-4" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
                <div className="w-12 h-8 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                <div className="w-16 h-4 rounded mt-2 animate-pulse" style={{ background: '#EDE8DF' }} />
              </div>
            ))}
          </div>
        ) : stats ? <MetricCards stats={stats} /> : null}
      </section>

      {/* Alertas + Movimentações side by side */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-up" style={{ animationDelay: '120ms' }}>

        {/* Alertas */}
        <div className="min-w-0">
          <p className="text-sm font-medium uppercase tracking-widest mb-2.5" style={{ color: '#A69B8D' }}>
            Alertas
            {hasAlerts && (
              <span className="ml-2 font-semibold" style={{ color: '#8B2332' }}>{allAlerts.length}</span>
            )}
          </p>
          {alertsLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-xl px-5 py-3 h-12" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
                  <div className="w-2/3 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                </div>
              ))}
            </div>
          ) : hasAlerts ? (
            <AlertsList alerts={allAlerts} />
          ) : (
            <div className="rounded-xl px-5 py-4" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
              <p className="text-base" style={{ color: '#5B7553' }}>Nenhum alerta no momento.</p>
            </div>
          )}
        </div>

        {/* Movimentações */}
        <div className="min-w-0">
          <div className="flex items-baseline justify-between mb-2.5">
            <p className="text-sm font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>Movimentações</p>
            <button onClick={() => navigate('/movimentacoes')} className="text-sm font-medium cursor-pointer hover:underline" style={{ color: '#C9A94E' }}>
              Ver todas &rarr;
            </button>
          </div>
          <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
            {recentLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="px-5 py-3.5" style={{ borderBottom: '1px solid #EDE8DF' }}>
                  <div className="w-2/3 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                </div>
              ))
            ) : !recent?.movimentacoes.length ? (
              <div className="px-5 py-6">
                <p className="text-base" style={{ color: '#A69B8D' }}>Nenhuma movimentação encontrada.</p>
              </div>
            ) : recent.movimentacoes.map((m, i) => (
              <div
                key={m.id}
                onClick={() => navigate('/movimentacoes')}
                className="flex items-center gap-3 px-5 py-3 cursor-pointer hover:brightness-[0.97] transition-all duration-150"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') navigate('/movimentacoes') }}
                style={{ borderBottom: i < recent.movimentacoes.length - 1 ? '1px solid #EDE8DF' : 'none' }}
              >
                {!m.is_read && (
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: MOV_COLOR[m.type] ?? '#6B6860' }} />
                )}
                <span className="text-sm font-semibold shrink-0" style={{ color: '#6B6860', minWidth: 72 }}>
                  {m.tipo_documento || MOV_TYPE[m.type] || m.type}
                </span>
                <span className="text-base truncate" style={{ color: '#0A1120' }}>{m.process_number}</span>
                {m.published_at && (
                  <span className="text-sm truncate hidden sm:block ml-auto shrink-0" style={{ color: '#A69B8D' }}>
                    {new Date(m.published_at).toLocaleDateString('pt-BR')}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pareceres — full width */}
      <section className="animate-fade-up" style={{ animationDelay: '180ms' }}>
        <div className="flex items-baseline justify-between mb-2.5">
          <p className="text-sm font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>Pareceres recentes</p>
          <button onClick={() => navigate('/pareceres')} className="text-sm font-medium cursor-pointer hover:underline" style={{ color: '#C9A94E' }}>
            Ver todos &rarr;
          </button>
        </div>
        <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
          {recentLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="px-5 py-3.5 flex justify-between" style={{ borderBottom: '1px solid #EDE8DF' }}>
                <div className="w-2/3 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                <div className="w-16 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
              </div>
            ))
          ) : !recent?.pareceres.length ? (
            <div className="px-5 py-6">
              <p className="text-base" style={{ color: '#A69B8D' }}>Nenhum parecer encontrado.</p>
            </div>
          ) : recent.pareceres.map((p, i) => {
            const st = STATUS_TONE[p.status]
            return (
              <div
                key={p.id}
                onClick={() => navigate(`/pareceres/${p.id}`)}
                className="flex items-center justify-between px-5 py-3.5 cursor-pointer hover:brightness-[0.97] transition-all duration-150"
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') navigate(`/pareceres/${p.id}`) }}
                style={{ borderBottom: i < recent.pareceres.length - 1 ? '1px solid #EDE8DF' : 'none' }}
              >
                <div className="min-w-0 flex-1 mr-3">
                  <p className="text-base truncate" style={{ color: '#0A1120' }}>{p.subject ?? 'Sem assunto'}</p>
                  {p.municipio_nome && <p className="text-sm mt-0.5" style={{ color: '#A69B8D' }}>{p.municipio_nome}</p>}
                </div>
                {st && (
                  <span
                    className="text-xs font-semibold px-2.5 py-1 rounded-lg shrink-0"
                    style={{ color: st.color, background: `${st.color}18` }}
                  >
                    {st.label}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </section>

    </div>
  )
}
