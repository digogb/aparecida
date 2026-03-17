import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../services/api'
import type { User } from '../../types'
import { useDashboardStats, useDashboardAlerts, useDashboardRecent } from '../../hooks/useDashboard'
import MetricCards from './MetricCards'
import AlertsList from './AlertsList'
import QuickActions from './QuickActions'

function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bom dia'
  if (hour < 18) return 'Boa tarde'
  return 'Boa noite'
}

function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const { data } = await api.get<User>('/api/auth/me')
      return data
    },
    staleTime: 5 * 60_000,
  })
}

const STATUS_LABELS: Record<string, string> = {
  pendente: 'Pendente',
  classificado: 'Classificado',
  gerado: 'Gerado',
  em_revisao: 'Em Revisão',
  devolvido: 'Devolvido',
  aprovado: 'Aprovado',
  enviado: 'Enviado',
}

const STATUS_BADGE: Record<string, string> = {
  pendente: 'bg-amber-100 text-amber-700',
  classificado: 'bg-blue-100 text-blue-700',
  gerado: 'bg-indigo-100 text-indigo-700',
  em_revisao: 'bg-purple-100 text-purple-700',
  devolvido: 'bg-red-100 text-red-700',
  aprovado: 'bg-green-100 text-green-700',
  enviado: 'bg-gray-100 text-gray-600',
}

const MOV_TYPE_LABELS: Record<string, string> = {
  intimacao: 'Intimação',
  sentenca: 'Sentença',
  despacho: 'Despacho',
  acordao: 'Acórdão',
  publicacao: 'Publicação',
  distribuicao: 'Distribuição',
  outros: 'Outros',
}

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: user } = useCurrentUser()
  const { data: stats, isLoading: statsLoading } = useDashboardStats()
  const { data: alertsData, isLoading: alertsLoading } = useDashboardAlerts()
  const { data: recent } = useDashboardRecent()

  const firstName = user?.name?.split(' ')[0] ?? 'Advogado'
  const isAdvogado = user?.role === 'advogado' || user?.role === 'admin'

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          {getGreeting()}, {isAdvogado ? `Dr. ${firstName}` : firstName}
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          {new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Metric Cards */}
      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-gray-100 rounded-xl h-24 animate-pulse" />
          ))}
        </div>
      ) : stats ? (
        <MetricCards stats={stats} />
      ) : null}

      {/* Quick Actions */}
      <div>
        <h2 className="text-base font-semibold text-gray-700 mb-3">Ações Rápidas</h2>
        <QuickActions recent={recent} />
      </div>

      {/* Alerts */}
      <div>
        <h2 className="text-base font-semibold text-gray-700 mb-3">
          Alertas{alertsData && alertsData.alerts.length > 0 && (
            <span className="ml-2 bg-red-100 text-red-700 text-xs font-semibold px-2 py-0.5 rounded-full">
              {alertsData.alerts.length}
            </span>
          )}
        </h2>
        {alertsLoading ? (
          <div className="bg-gray-100 rounded-xl h-16 animate-pulse" />
        ) : (
          <AlertsList alerts={alertsData?.alerts ?? []} />
        )}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Pareceres */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-gray-700">Pareceres Recentes</h2>
            <button
              onClick={() => navigate('/pareceres')}
              className="text-xs text-indigo-600 hover:underline"
            >
              Ver todos
            </button>
          </div>
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm divide-y divide-gray-50">
            {recent?.pareceres.length === 0 && (
              <p className="text-sm text-gray-400 p-4">Nenhum parecer encontrado.</p>
            )}
            {recent?.pareceres.map((p) => (
              <div
                key={p.id}
                onClick={() => navigate(`/pareceres/${p.id}`)}
                className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {p.subject ?? 'Sem assunto'}
                  </p>
                  {p.municipio_nome && (
                    <p className="text-xs text-gray-500">{p.municipio_nome}</p>
                  )}
                </div>
                <span className={`ml-3 text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${STATUS_BADGE[p.status] ?? 'bg-gray-100 text-gray-600'}`}>
                  {STATUS_LABELS[p.status] ?? p.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Movements */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-gray-700">Movimentações Recentes</h2>
            <button
              onClick={() => navigate('/movimentacoes')}
              className="text-xs text-indigo-600 hover:underline"
            >
              Ver todas
            </button>
          </div>
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm divide-y divide-gray-50">
            {recent?.movimentacoes.length === 0 && (
              <p className="text-sm text-gray-400 p-4">Nenhuma movimentação encontrada.</p>
            )}
            {recent?.movimentacoes.map((m) => (
              <div
                key={m.id}
                onClick={() => navigate('/movimentacoes')}
                className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate flex items-center gap-1.5">
                    {!m.is_read && (
                      <span className="w-2 h-2 bg-red-500 rounded-full shrink-0 inline-block" />
                    )}
                    Processo {m.process_number}
                  </p>
                  <p className="text-xs text-gray-500">
                    {MOV_TYPE_LABELS[m.type] ?? m.type}
                    {m.published_at && ` · ${new Date(m.published_at).toLocaleDateString('pt-BR')}`}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
