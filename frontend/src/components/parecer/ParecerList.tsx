import { useState } from 'react'
import { usePareceres } from '../../hooks/useParecer'
import type { ParecerFiltersState } from '../../types/parecer'
import ParecerCard from './ParecerCard'
import ParecerFilters from './ParecerFilters'

const EMPTY_FILTERS: ParecerFiltersState = { status: '', tema: '', remetente: '' }

function MetricCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  )
}

export default function ParecerList() {
  const [filters, setFilters] = useState<ParecerFiltersState>(EMPTY_FILTERS)
  const { data, isLoading, isError } = usePareceres(filters)

  const items = data?.items ?? []
  const total = data?.total ?? 0

  const pendentes = items.filter((p) => p.status === 'pendente').length
  const emRevisao = items.filter((p) => p.status === 'em_revisao').length

  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  const enviadosSemana = items.filter(
    (p) => p.status === 'enviado' && new Date(p.created_at) >= oneWeekAgo
  ).length

  const sorted = [...items].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  )

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Pareceres</h1>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Total" value={total} color="text-gray-900" />
        <MetricCard label="Pendentes" value={pendentes} color="text-yellow-600" />
        <MetricCard label="Em Revisão" value={emRevisao} color="text-orange-600" />
        <MetricCard label="Enviados (semana)" value={enviadosSemana} color="text-teal-600" />
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <ParecerFilters filters={filters} onChange={setFilters} />
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-16 text-gray-400">
          Carregando...
        </div>
      )}

      {isError && (
        <div className="flex items-center justify-center py-16 text-red-500">
          Erro ao carregar pareceres.
        </div>
      )}

      {!isLoading && !isError && sorted.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
          <svg className="w-12 h-12 mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">Nenhum parecer encontrado</p>
        </div>
      )}

      {!isLoading && !isError && sorted.length > 0 && (
        <div className="space-y-2">
          {sorted.map((parecer) => (
            <ParecerCard key={parecer.id} parecer={parecer} />
          ))}
        </div>
      )}
    </div>
  )
}
