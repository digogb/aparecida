import { useState } from 'react'
import { FileText, Bell, Clock, AlertCircle } from 'lucide-react'
import { useMovements, useMovementMetrics } from '../../hooks/useMovements'
import { useMovementWebSocket } from '../../hooks/useMovementWebSocket'
import MovementCard from './MovementCard'
import MovementFilters from './MovementFilters'
import MovementDetail from './MovementDetail'
import type { Movement, MovementFiltersState } from '../../types/movement'

const DEFAULT_FILTERS: MovementFiltersState = {
  movement_type: '',
  is_read: '',
  search: '',
}

interface MetricCardProps {
  label: string
  value: number | undefined
  icon: React.ReactNode
  color: string
}

function MetricCard({ label, value, icon, color }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4">
      <div className={`p-2.5 rounded-lg ${color}`}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value ?? '—'}</p>
        <p className="text-xs text-gray-500 mt-0.5">{label}</p>
      </div>
    </div>
  )
}

export default function MovementList() {
  const [filters, setFilters] = useState<MovementFiltersState>(DEFAULT_FILTERS)
  const [selected, setSelected] = useState<Movement | null>(null)

  useMovementWebSocket()

  const { data, isLoading, isError } = useMovements(filters)
  const { data: metrics } = useMovementMetrics()

  const movements = data?.items ?? []

  // Movements with same process number for timeline
  const relatedMovements = selected
    ? movements.filter((m) => m.process_number === selected.process_number)
    : []

  function handleSelect(m: Movement) {
    setSelected(m)
  }

  function handleClose() {
    setSelected(null)
  }

  function handleSelectRelated(m: Movement) {
    setSelected(m)
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Movimentações DJE</h1>
        <p className="text-sm text-gray-500 mt-1">
          Acompanhamento de publicações do Diário de Justiça Eletrônico
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          label="Total"
          value={metrics?.total}
          icon={<FileText size={18} className="text-gray-600" />}
          color="bg-gray-100"
        />
        <MetricCard
          label="Não lidas"
          value={metrics?.nao_lidas}
          icon={<Bell size={18} className="text-blue-600" />}
          color="bg-blue-50"
        />
        <MetricCard
          label="Prazo hoje"
          value={metrics?.com_prazo_hoje}
          icon={<AlertCircle size={18} className="text-red-500" />}
          color="bg-red-50"
        />
        <MetricCard
          label="Prazo na semana"
          value={metrics?.com_prazo_semana}
          icon={<Clock size={18} className="text-orange-500" />}
          color="bg-orange-50"
        />
      </div>

      {/* Filters */}
      <MovementFilters filters={filters} onChange={setFilters} />

      {/* List */}
      <div className="space-y-2">
        {isLoading && (
          <p className="text-sm text-gray-400 py-8 text-center">Carregando...</p>
        )}
        {isError && (
          <p className="text-sm text-red-500 py-8 text-center">
            Erro ao carregar movimentações.
          </p>
        )}
        {!isLoading && !isError && movements.length === 0 && (
          <p className="text-sm text-gray-400 py-12 text-center">
            Nenhuma movimentação encontrada.
          </p>
        )}
        {movements.map((m) => (
          <MovementCard key={m.id} movement={m} onClick={handleSelect} />
        ))}
      </div>

      {data && data.total > movements.length && (
        <p className="text-xs text-gray-400 text-center">
          Mostrando {movements.length} de {data.total} movimentações
        </p>
      )}

      {selected && (
        <MovementDetail
          movement={selected}
          relatedMovements={relatedMovements}
          onClose={handleClose}
          onSelectRelated={handleSelectRelated}
        />
      )}
    </div>
  )
}
