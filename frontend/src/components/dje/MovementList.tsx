import { useState } from 'react'
import { useMovements, useMovementMetrics } from '../../hooks/useMovements'
import { useMovementWebSocket } from '../../hooks/useMovementWebSocket'
import MovementCard from './MovementCard'
import MovementFilters from './MovementFilters'
import MovementDetail from './MovementDetail'
import type { Movement, MovementFiltersState } from '../../types/movement'

const DEFAULT_FILTERS: MovementFiltersState = { movement_type: '', is_read: '', search: '' }

const METRICS = [
  { key: 'total',           label: 'Total',          accent: '#1C1C2E', bg: '#F5F3EE', textColor: '#1C1C2E' },
  { key: 'nao_lidas',       label: 'Não lidas',      accent: '#DC2626', bg: '#FFF5F5', textColor: '#991B1B' },
  { key: 'com_prazo_hoje',  label: 'Prazo hoje',     accent: '#D97706', bg: '#FFFBF0', textColor: '#92400E' },
  { key: 'com_prazo_semana',label: 'Prazo na semana',accent: '#4F46E5', bg: '#F5F3FF', textColor: '#3730A3' },
]

export default function MovementList() {
  const [filters, setFilters] = useState<MovementFiltersState>(DEFAULT_FILTERS)
  const [selected, setSelected] = useState<Movement | null>(null)
  useMovementWebSocket()

  const { data, isLoading, isError } = useMovements(filters)
  const { data: metrics } = useMovementMetrics()

  const movements = data?.items ?? []
  const relatedMovements = selected ? movements.filter(m => m.process_number === selected.process_number) : []
  const metricValues = [metrics?.total, metrics?.nao_lidas, metrics?.com_prazo_hoje, metrics?.com_prazo_semana]

  return (
    <div className="min-h-full px-6 py-7 space-y-7" style={{ background: '#F5F3EE' }}>

        {/* Header */}
        <div className="animate-fade-up">
          <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: '#9CA3AF' }}>Módulo</p>
          <h1 className="font-display" style={{ fontSize: 40, fontWeight: 500, color: '#1C1C2E', letterSpacing: '-0.02em', lineHeight: 1 }}>
            Movimentações DJE
          </h1>
          <p className="text-sm mt-2" style={{ color: '#6B7280' }}>
            Acompanhamento de publicações do Diário de Justiça Eletrônico
          </p>
        </div>

        <div style={{ height: 1, background: 'linear-gradient(to right, #1C1C2E22, transparent)' }} />

        {/* Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {METRICS.map((m, i) => (
            <div key={m.key} className="animate-count rounded-2xl overflow-hidden"
              style={{ background: m.bg, border: `1px solid ${m.accent}22`, animationDelay: `${i * 60}ms` }}>
              <div style={{ height: 3, background: m.accent }} />
              <div className="p-4">
                <span className="font-display leading-none block"
                  style={{ fontSize: 38, fontWeight: 600, color: m.accent, letterSpacing: '-0.03em' }}>
                  {metricValues[i] ?? '—'}
                </span>
                <span className="text-xs font-semibold" style={{ color: m.textColor }}>{m.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="animate-fade-up rounded-2xl px-5 py-4" style={{ background: '#fff', border: '1px solid #E5E3DC', animationDelay: '180ms' }}>
          <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Filtros</p>
          <MovementFilters filters={filters} onChange={setFilters} />
        </div>

        {/* List */}
        <div className="space-y-2 animate-fade-up" style={{ animationDelay: '240ms' }}>
          {isLoading && Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-2xl h-20 animate-pulse" style={{ background: '#E9E7E0' }} />
          ))}
          {isError && (
            <div className="rounded-2xl px-5 py-4 text-sm" style={{ background: '#FEE2E2', color: '#991B1B', border: '1px solid #FCA5A522' }}>
              Erro ao carregar movimentações.
            </div>
          )}
          {!isLoading && !isError && movements.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16" style={{ color: '#9CA3AF' }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="mb-3 opacity-40">
                <path d="M18 8h1a4 4 0 0 1 0 8h-1"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/>
              </svg>
              <p className="text-sm">Nenhuma movimentação encontrada</p>
            </div>
          )}
          {movements.map((m, i) => (
            <div key={m.id} style={{ animationDelay: `${240 + i * 40}ms` }}>
              <MovementCard movement={m} onClick={setSelected} />
            </div>
          ))}
        </div>

        {data && data.total > movements.length && (
          <p className="text-xs text-center" style={{ color: '#9CA3AF' }}>
            Mostrando {movements.length} de {data.total} movimentações
          </p>
        )}

        {selected && (
          <MovementDetail
            movement={selected}
            relatedMovements={relatedMovements}
            onClose={() => setSelected(null)}
            onSelectRelated={setSelected}
          />
        )}
      </div>
  )
}
