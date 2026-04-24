import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../services/api'
import { fetchPareceresOverview } from '../../services/dashboardApi'
import type { User } from '../../types'
import type { OldestParecer, PipelineStage } from '../../types/dashboard'

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

function usePareceresOverview() {
  return useQuery({
    queryKey: ['dashboard', 'pareceres-overview'],
    queryFn: fetchPareceresOverview,
    staleTime: 60_000,
    refetchInterval: 2 * 60_000,
  })
}

const PIPELINE_ORDER = ['pendente', 'classificado', 'gerado', 'em_correcao', 'em_revisao', 'devolvido', 'aprovado', 'enviado']
const PIPELINE_COLOR: Record<string, string> = {
  pendente:     '#C9A94E',
  classificado: '#C9A94E',
  gerado:       '#A69B8D',
  em_correcao:  '#D97706',
  em_revisao:   '#6B6860',
  devolvido:    '#8B2332',
  aprovado:     '#5B7553',
  enviado:      '#142038',
  erro:         '#8B2332',
}

const STATUS_LABEL: Record<string, string> = {
  pendente:     'Pendente',
  classificado: 'Classificado',
  gerado:       'Gerado',
  em_correcao:  'Em correção',
  em_revisao:   'Em revisão',
  devolvido:    'Devolvido',
  aprovado:     'Aprovado',
  enviado:      'Enviado',
  erro:         'Erro',
}

function PipelineBar({ stages }: { stages: PipelineStage[] }) {
  const ordered = PIPELINE_ORDER
    .map((s) => stages.find((st) => st.status === s))
    .filter(Boolean) as PipelineStage[]
  const total = ordered.reduce((acc, s) => acc + s.count, 0)

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
      {/* Barra visual */}
      {total > 0 && (
        <div className="flex h-2 overflow-hidden">
          {ordered.filter((s) => s.count > 0).map((s) => (
            <div
              key={s.status}
              title={`${s.label}: ${s.count}`}
              style={{
                width: `${(s.count / total) * 100}%`,
                background: PIPELINE_COLOR[s.status] ?? '#A69B8D',
                minWidth: s.count > 0 ? 4 : 0,
              }}
            />
          ))}
        </div>
      )}
      {/* Etapas */}
      <div className="grid grid-cols-2 xs:grid-cols-4 sm:grid-cols-8 divide-x" style={{ borderColor: '#E0D9CE' }}>
        {ordered.map((s) => (
          <div key={s.status} className="px-3 py-3 text-center" style={{ borderRight: '1px solid #E0D9CE' }}>
            <span
              className="block font-display leading-none"
              style={{
                fontSize: 28,
                fontWeight: 500,
                color: s.count > 0 ? (PIPELINE_COLOR[s.status] ?? '#A69B8D') : '#D0C9BE',
                letterSpacing: '-0.03em',
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {s.count}
            </span>
            <span className="block text-xs mt-1 leading-tight" style={{ color: '#A69B8D' }}>
              {s.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function OldestList({ items }: { items: OldestParecer[] }) {
  const navigate = useNavigate()

  if (!items.length) {
    return (
      <div className="rounded-xl px-5 py-5" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
        <p className="text-base" style={{ color: '#5B7553' }}>Nenhum parecer em aberto.</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
      {items.map((p, i) => (
        <div
          key={p.id}
          onClick={() => navigate(`/pareceres/${p.id}`)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') navigate(`/pareceres/${p.id}`) }}
          className="flex items-center gap-3 px-5 py-3.5 cursor-pointer hover:brightness-[0.97] transition-all duration-150"
          style={{ borderBottom: i < items.length - 1 ? '1px solid #EDE8DF' : 'none' }}
        >
          {/* Dias */}
          <span
            className="shrink-0 text-center font-display leading-none"
            style={{
              fontSize: 22,
              fontWeight: 500,
              color: p.dias_aberto >= 5 ? '#8B2332' : p.dias_aberto >= 2 ? '#D97706' : '#A69B8D',
              letterSpacing: '-0.03em',
              fontVariantNumeric: 'tabular-nums',
              minWidth: 36,
            }}
          >
            {p.dias_aberto}d
          </span>

          {/* Info */}
          <div className="min-w-0 flex-1">
            <p className="text-base truncate" style={{ color: '#0A1120' }}>{p.subject ?? 'Sem assunto'}</p>
            {p.municipio_nome && (
              <p className="text-sm mt-0.5 truncate" style={{ color: '#A69B8D' }}>{p.municipio_nome}</p>
            )}
          </div>

          {/* Status badge */}
          <span
            className="text-xs font-semibold px-2.5 py-1 rounded-lg shrink-0"
            style={{
              color: PIPELINE_COLOR[p.status] ?? '#6B6860',
              background: `${PIPELINE_COLOR[p.status] ?? '#6B6860'}18`,
            }}
          >
            {STATUS_LABEL[p.status] ?? p.status}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function DashboardPareceresPage() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const { data: overview, isLoading } = usePareceresOverview()

  const firstName = user?.name?.split(' ')[0] ?? 'Advogado'
  const isAdvogado = user?.role === 'advogado' || user?.role === 'admin'
  const today = new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })

  return (
    <div className="min-h-full px-4 md:px-6 py-6 md:py-8 space-y-6 md:space-y-8" style={{ background: '#FAF8F5' }}>

      {/* Header */}
      <header className="animate-fade-up">
        <p className="text-sm font-medium uppercase tracking-widest mb-0.5" style={{ color: '#A69B8D' }}>
          {getGreeting()}
        </p>
        <div className="flex items-baseline justify-between gap-2">
          <h1 className="font-display" style={{ fontSize: 28, fontWeight: 400, color: '#142038', letterSpacing: '-0.02em' }}>
            {isAdvogado ? `Dr. ${firstName}` : firstName}
          </h1>
          <p className="text-sm capitalize hidden xs:block" style={{ color: '#A69B8D' }}>{today}</p>
        </div>
      </header>

      {/* Resumo geral */}
      <section className="grid grid-cols-2 gap-3 animate-fade-up" style={{ animationDelay: '60ms' }}>
        {isLoading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="rounded-xl px-5 py-4" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
              <div className="w-12 h-8 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
              <div className="w-24 h-4 rounded mt-2 animate-pulse" style={{ background: '#EDE8DF' }} />
            </div>
          ))
        ) : (
          <>
            <div
              onClick={() => navigate('/pareceres')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') navigate('/pareceres') }}
              className="rounded-xl overflow-hidden cursor-pointer hover:brightness-[0.97] transition-all duration-150"
              style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}
            >
              <div className="h-1" style={{ background: '#C9A94E' }} />
              <div className="px-5 py-4">
                <span className="block font-display leading-none" style={{ fontSize: 44, fontWeight: 500, color: '#C9A94E', letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums' }}>
                  {overview?.total_abertos ?? 0}
                </span>
                <span className="text-sm font-medium mt-1.5 block" style={{ color: '#6B6860' }}>Pareceres em aberto</span>
              </div>
            </div>

            <div
              className="rounded-xl overflow-hidden"
              style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}
            >
              <div className="h-1" style={{ background: '#5B7553' }} />
              <div className="px-5 py-4">
                <span className="block font-display leading-none" style={{ fontSize: 44, fontWeight: 500, color: '#5B7553', letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums' }}>
                  {overview?.concluidos_semana ?? 0}
                </span>
                <span className="text-sm font-medium mt-1.5 block" style={{ color: '#6B6860' }}>Concluídos esta semana</span>
              </div>
            </div>
          </>
        )}
      </section>

      {/* Pipeline */}
      <section className="animate-fade-up" style={{ animationDelay: '100ms' }}>
        <p className="text-sm font-medium uppercase tracking-widest mb-2.5" style={{ color: '#A69B8D' }}>
          Pareceres por etapa
        </p>
        {isLoading ? (
          <div className="rounded-xl px-5 py-4 h-20 animate-pulse" style={{ background: '#EDE8DF', border: '1.5px solid #E0D9CE' }} />
        ) : overview ? (
          <PipelineBar stages={overview.pipeline} />
        ) : null}
      </section>

      {/* Município + Advogado */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-up" style={{ animationDelay: '140ms' }}>

        {/* Por município */}
        <div>
          <p className="text-sm font-medium uppercase tracking-widest mb-2.5" style={{ color: '#A69B8D' }}>
            Pareceres abertos por município
          </p>
          <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
            {isLoading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="px-5 py-3 flex justify-between" style={{ borderBottom: '1px solid #EDE8DF' }}>
                  <div className="w-1/2 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                  <div className="w-8 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                </div>
              ))
            ) : !overview?.por_municipio.length ? (
              <div className="px-5 py-5">
                <p className="text-base" style={{ color: '#A69B8D' }}>Nenhum dado disponível.</p>
              </div>
            ) : overview.por_municipio.map((m, i) => {
              const max = overview.por_municipio[0].count
              return (
                <div
                  key={m.municipio_id ?? i}
                  className="px-5 py-3 flex items-center gap-3"
                  style={{ borderBottom: i < overview.por_municipio.length - 1 ? '1px solid #EDE8DF' : 'none' }}
                >
                  <span className="text-base flex-1 truncate" style={{ color: '#0A1120' }}>{m.municipio_nome}</span>
                  <div className="flex items-center gap-2 shrink-0">
                    <div className="w-20 h-1.5 rounded-full overflow-hidden" style={{ background: '#E0D9CE' }}>
                      <div className="h-full rounded-full" style={{ width: `${(m.count / max) * 100}%`, background: '#C9A94E' }} />
                    </div>
                    <span className="text-sm font-semibold w-5 text-right" style={{ color: '#C9A94E' }}>{m.count}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Por advogado */}
        <div>
          <p className="text-sm font-medium uppercase tracking-widest mb-2.5" style={{ color: '#A69B8D' }}>
            Pareceres abertos por advogado
          </p>
          <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="px-5 py-3 flex justify-between" style={{ borderBottom: '1px solid #EDE8DF' }}>
                  <div className="w-1/2 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                  <div className="w-8 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                </div>
              ))
            ) : !overview?.por_advogado.length ? (
              <div className="px-5 py-5">
                <p className="text-base" style={{ color: '#A69B8D' }}>Nenhum dado disponível.</p>
              </div>
            ) : overview.por_advogado.map((a, i) => {
              const max = overview.por_advogado[0].count
              return (
                <div
                  key={a.user_id ?? i}
                  className="px-5 py-3 flex items-center gap-3"
                  style={{ borderBottom: i < overview.por_advogado.length - 1 ? '1px solid #EDE8DF' : 'none' }}
                >
                  <span className="text-base flex-1 truncate" style={{ color: '#0A1120' }}>{a.user_name}</span>
                  <div className="flex items-center gap-2 shrink-0">
                    <div className="w-20 h-1.5 rounded-full overflow-hidden" style={{ background: '#E0D9CE' }}>
                      <div className="h-full rounded-full" style={{ width: `${(a.count / max) * 100}%`, background: '#142038' }} />
                    </div>
                    <span className="text-sm font-semibold w-5 text-right" style={{ color: '#142038' }}>{a.count}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Mais antigos */}
      <section className="animate-fade-up" style={{ animationDelay: '180ms' }}>
        <div className="flex items-baseline justify-between mb-2.5">
          <p className="text-sm font-medium uppercase tracking-widest" style={{ color: '#A69B8D' }}>
            Mais antigos em aberto
          </p>
          <button onClick={() => navigate('/pareceres')} className="text-sm font-medium cursor-pointer hover:underline" style={{ color: '#C9A94E' }}>
            Ver todos &rarr;
          </button>
        </div>
        {isLoading ? (
          <div className="rounded-xl overflow-hidden" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="px-5 py-3.5 flex gap-3" style={{ borderBottom: '1px solid #EDE8DF' }}>
                <div className="w-8 h-6 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
                <div className="flex-1 h-4 rounded animate-pulse" style={{ background: '#EDE8DF' }} />
              </div>
            ))}
          </div>
        ) : (
          <OldestList items={overview?.mais_antigos ?? []} />
        )}
      </section>

    </div>
  )
}
