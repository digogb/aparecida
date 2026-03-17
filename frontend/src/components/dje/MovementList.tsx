import { useState } from 'react'
import { useMovements, useMovementMetrics, useDjeSync } from '../../hooks/useMovements'
import { useMovementWebSocket } from '../../hooks/useMovementWebSocket'
import MovementCard from './MovementCard'
import MovementFilters from './MovementFilters'
import MovementDetail from './MovementDetail'
import type { Movement, MovementFiltersState } from '../../types/movement'

const DEFAULT_FILTERS: MovementFiltersState = { movement_type: '', is_read: '', search: '' }

function SyncModal({ onClose }: { onClose: () => void }) {
  const sync = useDjeSync()
  const [form, setForm] = useState({ nome_advogado: '', numero_oab: '', sigla_tribunal: '', data_inicio: '', data_fim: '' })
  const [result, setResult] = useState<{ found: number; ingested: number } | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: Record<string, string> = {}
    if (form.nome_advogado) payload.nome_advogado = form.nome_advogado
    if (form.numero_oab) payload.numero_oab = form.numero_oab
    if (form.sigla_tribunal) payload.sigla_tribunal = form.sigla_tribunal
    if (form.data_inicio) payload.data_inicio = form.data_inicio
    if (form.data_fim) payload.data_fim = form.data_fim
    sync.mutate(payload, { onSuccess: (data) => setResult({ found: data.found, ingested: data.ingested }) })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(28,28,46,0.5)' }}>
      <div className="rounded-2xl p-6 w-full max-w-md shadow-2xl" style={{ background: '#fff', border: '1px solid #E5E3DC' }}>
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display" style={{ fontSize: 22, fontWeight: 500, color: '#1C1C2E' }}>Sincronizar DJE</h2>
          <button onClick={onClose} style={{ color: '#9CA3AF' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {result ? (
          <div className="text-center py-6">
            <div className="font-display mb-1" style={{ fontSize: 48, fontWeight: 600, color: '#1C1C2E' }}>{result.ingested}</div>
            <p className="text-sm mb-1" style={{ color: '#6B7280' }}>novas movimentações importadas</p>
            <p className="text-xs" style={{ color: '#9CA3AF' }}>{result.found} encontradas no DJE</p>
            <button onClick={onClose} className="mt-6 px-5 py-2 rounded-xl text-sm font-semibold" style={{ background: '#1C1C2E', color: '#fff' }}>
              Fechar
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Nome do advogado</label>
              <input
                type="text" placeholder="Ex: JOSE ANTONIO SOUZA"
                value={form.nome_advogado} onChange={e => setForm(f => ({ ...f, nome_advogado: e.target.value }))}
                className="w-full px-3 py-2 rounded-xl text-sm outline-none"
                style={{ background: '#F5F3EE', border: '1px solid #E5E3DC', color: '#1C1C2E' }}
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Número OAB</label>
              <input
                type="text" placeholder="Ex: 12345/SP"
                value={form.numero_oab} onChange={e => setForm(f => ({ ...f, numero_oab: e.target.value }))}
                className="w-full px-3 py-2 rounded-xl text-sm outline-none"
                style={{ background: '#F5F3EE', border: '1px solid #E5E3DC', color: '#1C1C2E' }}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Tribunal</label>
                <input
                  type="text" placeholder="Ex: TJSP"
                  value={form.sigla_tribunal} onChange={e => setForm(f => ({ ...f, sigla_tribunal: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl text-sm outline-none"
                  style={{ background: '#F5F3EE', border: '1px solid #E5E3DC', color: '#1C1C2E' }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Data início</label>
                <input
                  type="date" value={form.data_inicio} onChange={e => setForm(f => ({ ...f, data_inicio: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl text-sm outline-none"
                  style={{ background: '#F5F3EE', border: '1px solid #E5E3DC', color: '#1C1C2E' }}
                />
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-widest block mb-1" style={{ color: '#9CA3AF' }}>Data fim</label>
                <input
                  type="date" value={form.data_fim} onChange={e => setForm(f => ({ ...f, data_fim: e.target.value }))}
                  className="w-full px-3 py-2 rounded-xl text-sm outline-none"
                  style={{ background: '#F5F3EE', border: '1px solid #E5E3DC', color: '#1C1C2E' }}
                />
              </div>
            </div>
            {sync.isError && (
              <p className="text-xs px-3 py-2 rounded-xl" style={{ background: '#FEE2E2', color: '#991B1B' }}>
                Erro ao buscar. Verifique os parâmetros.
              </p>
            )}
            <div className="flex gap-2 pt-2">
              <button type="button" onClick={onClose} className="flex-1 px-4 py-2 rounded-xl text-sm font-semibold"
                style={{ background: '#F5F3EE', color: '#1C1C2E', border: '1px solid #E5E3DC' }}>
                Cancelar
              </button>
              <button type="submit" disabled={sync.isPending} className="flex-1 px-4 py-2 rounded-xl text-sm font-semibold flex items-center justify-center gap-2"
                style={{ background: '#1C1C2E', color: '#fff', opacity: sync.isPending ? 0.7 : 1 }}>
                {sync.isPending ? (
                  <>
                    <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                    </svg>
                    Buscando...
                  </>
                ) : 'Sincronizar agora'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

const METRICS = [
  { key: 'total',           label: 'Total',          accent: '#1C1C2E', bg: '#F5F3EE', textColor: '#1C1C2E' },
  { key: 'nao_lidas',       label: 'Não lidas',      accent: '#DC2626', bg: '#FFF5F5', textColor: '#991B1B' },
  { key: 'com_prazo_hoje',  label: 'Prazo hoje',     accent: '#D97706', bg: '#FFFBF0', textColor: '#92400E' },
  { key: 'com_prazo_semana',label: 'Prazo na semana',accent: '#4F46E5', bg: '#F5F3FF', textColor: '#3730A3' },
]

export default function MovementList() {
  const [filters, setFilters] = useState<MovementFiltersState>(DEFAULT_FILTERS)
  const [selected, setSelected] = useState<Movement | null>(null)
  const [syncOpen, setSyncOpen] = useState(false)
  useMovementWebSocket()

  const { data, isLoading, isError } = useMovements(filters)
  const { data: metrics } = useMovementMetrics()

  const movements = data?.items ?? []
  const relatedMovements = selected ? movements.filter(m => m.process_number === selected.process_number) : []
  const metricValues = [metrics?.total, metrics?.nao_lidas, metrics?.com_prazo_hoje, metrics?.com_prazo_semana]

  return (
    <div className="min-h-full px-6 py-7 space-y-7" style={{ background: '#F5F3EE' }}>

        {/* Header */}
        <div className="animate-fade-up flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: '#9CA3AF' }}>Módulo</p>
            <h1 className="font-display" style={{ fontSize: 40, fontWeight: 500, color: '#1C1C2E', letterSpacing: '-0.02em', lineHeight: 1 }}>
              Movimentações DJE
            </h1>
            <p className="text-sm mt-2" style={{ color: '#6B7280' }}>
              Acompanhamento de publicações do Diário de Justiça Eletrônico
            </p>
          </div>
          <button
            onClick={() => setSyncOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold mt-1 shrink-0"
            style={{ background: '#1C1C2E', color: '#fff' }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
            </svg>
            Sincronizar
          </button>
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

        {syncOpen && <SyncModal onClose={() => setSyncOpen(false)} />}

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
