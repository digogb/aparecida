import { useState } from 'react'
import { useMovements, useMovementMetrics, useDjeSync } from '../../hooks/useMovements'
import { useMovementWebSocket } from '../../hooks/useMovementWebSocket'
import MovementCard from './MovementCard'
import MovementFilters from './MovementFilters'
import MovementDetail from './MovementDetail'
import type { Movement, MovementFiltersState } from '../../types/movement'

const DEFAULT_FILTERS: MovementFiltersState = { type: '', is_read: '', search: '' }

function SyncModal({ onClose }: { onClose: () => void }) {
  const sync = useDjeSync()
  const [form, setForm] = useState({ nome_advogado: '', numero_oab: '', sigla_tribunal: '', data_inicio: '', data_fim: '' })
  const [queued, setQueued] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: Record<string, string> = {}
    if (form.nome_advogado) payload.nome_advogado = form.nome_advogado
    if (form.numero_oab) payload.numero_oab = form.numero_oab
    if (form.sigla_tribunal) payload.sigla_tribunal = form.sigla_tribunal
    if (form.data_inicio) payload.data_inicio = form.data_inicio
    if (form.data_fim) payload.data_fim = form.data_fim
    sync.mutate(payload, { onSuccess: () => setQueued(true) })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl p-6 w-full max-w-md" style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display" style={{ fontSize: 22, fontWeight: 500, color: '#142038' }}>Sincronizar DJE</h2>
          <button onClick={onClose} style={{ color: '#A69B8D' }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {queued ? (
          <div className="text-center py-6">
            <svg className="mx-auto mb-3 opacity-60" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#5B7553" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
            </svg>
            <p className="font-medium text-base mb-1" style={{ color: '#0A1120' }}>Busca iniciada</p>
            <p className="text-sm" style={{ color: '#A69B8D' }}>O worker está buscando no DJE em segundo plano.<br/>As movimentações aparecem automaticamente quando chegarem.</p>
            <button onClick={onClose} className="mt-6 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer" style={{ background: '#142038', color: '#F5F0E8' }}>
              Fechar
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Nome do advogado</label>
              <input
                type="text" placeholder="Ex: JOSE ANTONIO SOUZA"
                value={form.nome_advogado} onChange={e => setForm(f => ({ ...f, nome_advogado: e.target.value }))}
                className="w-full px-3 py-2.5 rounded-xl text-base outline-none focus:ring-2"
                style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              />
            </div>
            <div>
              <label className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Número OAB</label>
              <input
                type="text" placeholder="Ex: 12345/SP"
                value={form.numero_oab} onChange={e => setForm(f => ({ ...f, numero_oab: e.target.value }))}
                className="w-full px-3 py-2.5 rounded-xl text-base outline-none focus:ring-2"
                style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Tribunal</label>
                <input
                  type="text" placeholder="Ex: TJSP"
                  value={form.sigla_tribunal} onChange={e => setForm(f => ({ ...f, sigla_tribunal: e.target.value }))}
                  className="w-full px-3 py-2.5 rounded-xl text-base outline-none focus:ring-2"
                  style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Data início</label>
                <input
                  type="date" value={form.data_inicio} onChange={e => setForm(f => ({ ...f, data_inicio: e.target.value }))}
                  className="w-full px-3 py-2.5 rounded-xl text-base outline-none focus:ring-2"
                  style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                />
              </div>
              <div>
                <label className="text-sm font-medium uppercase tracking-widest block mb-1" style={{ color: '#A69B8D' }}>Data fim</label>
                <input
                  type="date" value={form.data_fim} onChange={e => setForm(f => ({ ...f, data_fim: e.target.value }))}
                  className="w-full px-3 py-2.5 rounded-xl text-base outline-none focus:ring-2"
                  style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', color: '#0A1120', '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                />
              </div>
            </div>
            {sync.isError && (
              <p className="text-sm px-3 py-2 rounded-xl" style={{ background: '#8B233218', color: '#8B2332' }}>
                Erro ao buscar. Verifique os parâmetros.
              </p>
            )}
            <div className="flex gap-2 pt-2">
              <button type="button" onClick={onClose} className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
                style={{ background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}>
                Cancelar
              </button>
              <button type="submit" disabled={sync.isPending} className="flex-1 px-4 py-2.5 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
                style={{ background: '#142038', color: '#F5F0E8', opacity: sync.isPending ? 0.7 : 1 }}>
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
  { key: 'total',  label: 'Total',     tone: '#0A1120' },
  { key: 'unread', label: 'Não lidas', tone: '#C9A94E' },
]

export default function MovementList() {
  const [filters, setFilters] = useState<MovementFiltersState>(DEFAULT_FILTERS)
  const [selected, setSelected] = useState<Movement | null>(null)
  const [syncOpen, setSyncOpen] = useState(false)
  useMovementWebSocket()

  const { data, isLoading, isError } = useMovements(filters)
  const { data: metrics } = useMovementMetrics()

  const movements = data?.items ?? []
  const relatedMovements = selected ? movements.filter(m => m.process_id === selected.process_id) : []
  const metricValues = [metrics?.total, metrics?.unread]

  return (
    <div className="min-h-full px-6 py-8 space-y-8" style={{ background: '#F5F0E8' }}>

        {/* Header */}
        <div className="animate-fade-up flex items-end justify-between">
          <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: '#142038', letterSpacing: '-0.02em' }}>
            Movimentações DJE
          </h1>
          <button
            onClick={() => setSyncOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
            style={{ background: '#142038', color: '#F5F0E8' }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/>
            </svg>
            Sincronizar
          </button>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {METRICS.map((m, i) => (
            <div key={m.key} className="animate-count rounded-xl overflow-hidden"
              style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', animationDelay: `${i * 50}ms` }}>
              <div className="h-1" style={{ background: m.tone }} />
              <div className="px-5 py-4">
                <span className="font-display leading-none block"
                  style={{ fontSize: 38, fontWeight: 500, color: m.tone, letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums' }}>
                  {metricValues[i] ?? '—'}
                </span>
                <span className="text-sm font-medium" style={{ color: '#6B6860' }}>{m.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="animate-fade-up" style={{ animationDelay: '180ms' }}>
          <MovementFilters filters={filters} onChange={setFilters} />
        </div>

        {/* List */}
        <div className="space-y-2 animate-fade-up" style={{ animationDelay: '240ms' }}>
          {isLoading && Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-xl h-20 animate-pulse" style={{ background: '#EDE8DF' }} />
          ))}
          {isError && (
            <div className="rounded-xl px-5 py-4 text-base" style={{ background: '#8B233218', color: '#8B2332', border: '1.5px solid #8B233222' }}>
              Erro ao carregar movimentações.
            </div>
          )}
          {!isLoading && !isError && movements.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16">
              <p className="text-base" style={{ color: '#A69B8D' }}>Nenhuma movimentação encontrada</p>
            </div>
          )}
          {movements.map((m, i) => (
            <div key={m.id} style={{ animationDelay: `${240 + i * 40}ms` }}>
              <MovementCard movement={m} onClick={setSelected} />
            </div>
          ))}
        </div>

        {data && data.total > movements.length && (
          <p className="text-sm text-center" style={{ color: '#A69B8D' }}>
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
