import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../services/api'
import type { User } from '../../types'
import { useDashboardStats, useDashboardAlerts, useDashboardRecent } from '../../hooks/useDashboard'
import MetricCards from './MetricCards'
import AlertsList from './AlertsList'
import QuickActions from './QuickActions'

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

const STATUS_BADGE: Record<string, { label: string; color: string; bg: string }> = {
  pendente:     { label: 'Pendente',    color: '#92400E', bg: '#FEF3C7' },
  classificado: { label: 'Classificado',color: '#1E40AF', bg: '#DBEAFE' },
  gerado:       { label: 'Gerado',      color: '#3730A3', bg: '#E0E7FF' },
  em_revisao:   { label: 'Em Revisão',  color: '#5B21B6', bg: '#EDE9FE' },
  devolvido:    { label: 'Devolvido',   color: '#991B1B', bg: '#FEE2E2' },
  aprovado:     { label: 'Aprovado',    color: '#065F46', bg: '#D1FAE5' },
  enviado:      { label: 'Enviado',     color: '#374151', bg: '#F3F4F6' },
}

const MOV_TYPE: Record<string, string> = {
  intimacao:'Intimação', sentenca:'Sentença', despacho:'Despacho',
  acordao:'Acórdão', publicacao:'Publicação', distribuicao:'Distribuição', outros:'Outros',
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const { data: stats, isLoading: statsLoading } = useDashboardStats()
  const { data: alertsData, isLoading: alertsLoading } = useDashboardAlerts()
  const { data: recent } = useDashboardRecent()

  const firstName = user?.name?.split(' ')[0] ?? 'Advogado'
  const isAdvogado = user?.role === 'advogado' || user?.role === 'admin'
  const today = new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

  return (
    <div className="min-h-full px-6 py-7 space-y-6" style={{ background: '#F5F3EE' }}>

      {/* Header */}
      <div className="animate-fade-up flex items-end justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: '#9CA3AF' }}>{getGreeting()}</p>
          <h1 className="font-display leading-none" style={{ fontSize: 44, fontWeight: 500, color: '#1C1C2E', letterSpacing: '-0.02em' }}>
            {isAdvogado ? `Dr. ${firstName}` : firstName}
          </h1>
          <p className="mt-1.5 text-sm capitalize" style={{ color: '#6B7280' }}>{today}</p>
        </div>
        <div className="hidden md:flex items-center gap-2 rounded-2xl px-4 py-2.5"
          style={{ background: '#fff', border: '1px solid #E5E3DC' }}>
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs font-medium" style={{ color: '#374151' }}>Sistema operacional</span>
        </div>
      </div>

      <div style={{ height: 1, background: 'linear-gradient(to right, #1C1C2E22, transparent)' }} />

      {/* Metrics */}
      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-2xl h-24 animate-pulse" style={{ background: '#E9E7E0' }} />
          ))}
        </div>
      ) : stats ? <MetricCards stats={stats} /> : null}

      {/* Quick Actions */}
      <div className="animate-fade-up" style={{ animationDelay: '150ms' }}>
        <p className="text-xs font-semibold uppercase tracking-widest mb-2.5" style={{ color: '#9CA3AF' }}>Ações rápidas</p>
        <QuickActions recent={recent} />
      </div>

      {/* Alerts */}
      <div className="animate-fade-up" style={{ animationDelay: '200ms' }}>
        <div className="flex items-center gap-2 mb-2.5">
          <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#9CA3AF' }}>Alertas</p>
          {alertsData && alertsData.alerts.length > 0 && (
            <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: '#FEE2E2', color: '#DC2626' }}>
              {alertsData.alerts.length}
            </span>
          )}
        </div>
        {alertsLoading
          ? <div className="rounded-2xl h-12 animate-pulse" style={{ background: '#E9E7E0' }} />
          : <AlertsList alerts={alertsData?.alerts ?? []} />}
      </div>

      {/* Recent — full width two columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-fade-up" style={{ animationDelay: '260ms' }}>

        <div className="rounded-2xl overflow-hidden" style={{ background: '#fff', border: '1px solid #E5E3DC' }}>
          <div className="flex items-center justify-between px-5 py-3.5" style={{ borderBottom: '1px solid #F0EDE6' }}>
            <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#9CA3AF' }}>Pareceres recentes</span>
            <button onClick={() => navigate('/pareceres')} className="text-xs font-medium hover:underline" style={{ color: '#4F46E5' }}>Ver todos →</button>
          </div>
          {!recent?.pareceres.length
            ? <p className="text-sm text-gray-400 px-5 py-4">Nenhum parecer encontrado.</p>
            : recent.pareceres.map((p, i) => {
                const badge = STATUS_BADGE[p.status]
                return (
                  <div key={p.id} onClick={() => navigate(`/pareceres/${p.id}`)}
                    className="flex items-center justify-between px-5 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
                    style={{ borderBottom: i < recent.pareceres.length - 1 ? '1px solid #F7F5F0' : 'none' }}>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate" style={{ color: '#1C1C2E' }}>{p.subject ?? 'Sem assunto'}</p>
                      {p.municipio_nome && <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>{p.municipio_nome}</p>}
                    </div>
                    {badge && (
                      <span className="ml-3 text-xs font-semibold px-2.5 py-0.5 rounded-full shrink-0"
                        style={{ background: badge.bg, color: badge.color }}>{badge.label}</span>
                    )}
                  </div>
                )
              })
          }
        </div>

        <div className="rounded-2xl overflow-hidden" style={{ background: '#fff', border: '1px solid #E5E3DC' }}>
          <div className="flex items-center justify-between px-5 py-3.5" style={{ borderBottom: '1px solid #F0EDE6' }}>
            <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#9CA3AF' }}>Movimentações recentes</span>
            <button onClick={() => navigate('/movimentacoes')} className="text-xs font-medium hover:underline" style={{ color: '#4F46E5' }}>Ver todas →</button>
          </div>
          {!recent?.movimentacoes.length
            ? <p className="text-sm text-gray-400 px-5 py-4">Nenhuma movimentação encontrada.</p>
            : recent.movimentacoes.map((m, i) => (
                <div key={m.id} onClick={() => navigate('/movimentacoes')}
                  className="flex items-center gap-3 px-5 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
                  style={{ borderBottom: i < recent.movimentacoes.length - 1 ? '1px solid #F7F5F0' : 'none' }}>
                  {!m.is_read && <div className="w-2 h-2 rounded-full shrink-0 bg-red-500" />}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium" style={{ color: '#1C1C2E' }}>Processo {m.process_number}</p>
                    <p className="text-xs mt-0.5" style={{ color: '#9CA3AF' }}>
                      {MOV_TYPE[m.type] ?? m.type}
                      {m.published_at && ` · ${new Date(m.published_at).toLocaleDateString('pt-BR')}`}
                    </p>
                  </div>
                </div>
              ))
          }
        </div>
      </div>
    </div>
  )
}
