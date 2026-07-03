import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../../services/api'
import { usePareceres, PARECERES_PAGE_SIZE } from '../../hooks/useParecer'
import { fetchPareceresOverview } from '../../services/dashboardApi'
import type { ParecerFiltersState } from '../../types/parecer'
import ParecerCard from './ParecerCard'
import ParecerFilters from './ParecerFilters'

const EMPTY: ParecerFiltersState = { status: '', tema: '', municipio: '', enviado_por: '', remetente: '' }

const METRICS = [
  { key: 'total', label: 'Total',              tone: '#0A1120' },
  { key: 'rev',   label: 'Aguardando revisão', tone: '#A69B8D' },
  { key: 'corr',  label: 'Em correção',        tone: '#D97706' },
  { key: 'sent',  label: 'Enviados na semana', tone: '#5B7553' },
]

export default function ParecerList() {
  const [filters, setFilters] = useState<ParecerFiltersState>(EMPTY)
  const [page, setPage] = useState(0)
  const [importing, setImporting] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data, isLoading, isError } = usePareceres(filters, page)

  // Trocar de filtro volta para a primeira página (o offset antigo não faz sentido no novo recorte).
  function handleFiltersChange(next: ParecerFiltersState) {
    setFilters(next)
    setPage(0)
  }
  // Métricas vêm do mesmo endpoint server-side do dashboard (base inteira, não a página) —
  // mesma queryKey, então compartilha cache e fica consistente com a tela de Dashboard.
  const { data: overview } = useQuery({
    queryKey: ['dashboard', 'pareceres-overview'],
    queryFn: fetchPareceresOverview,
    staleTime: 60_000,
    refetchInterval: 2 * 60_000,
  })

  async function handleEmlUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    setImportError(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const { data } = await api.post('/api/parecer-requests/ingest-eml', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      await queryClient.invalidateQueries({ queryKey: ['pareceres'] })
      await queryClient.invalidateQueries({ queryKey: ['dashboard', 'pareceres-overview'] })
      navigate(`/pareceres/${data.id}`)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setImportError(msg || (err instanceof Error ? err.message : 'Erro ao importar'))
    } finally {
      setImporting(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const items = data?.items ?? []
  const pipeline = overview?.pipeline ?? []
  const countOf = (...statuses: string[]) =>
    pipeline.filter(s => statuses.includes(s.status)).reduce((sum, s) => sum + s.count, 0)
  const total = pipeline.reduce((sum, s) => sum + s.count, 0)
  const aguardando = countOf('gerado', 'em_revisao')
  const emCorrecao = countOf('em_correcao')
  const enviadosSemana = overview?.enviados_semana ?? 0
  const values = [total, aguardando, emCorrecao, enviadosSemana]

  const sorted = [...items].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

  // Agrupa por thread (só quando não-nula) para anotar a rodada N/M de cada irmão.
  // A rodada é a posição do request na thread ordenada por created_at asc.
  const roundInfo = new Map<string, { rodada: number; total: number }>()
  const byThread = new Map<string, typeof items>()
  for (const p of items) {
    if (!p.gmail_thread_id) continue
    const arr = byThread.get(p.gmail_thread_id) ?? []
    arr.push(p)
    byThread.set(p.gmail_thread_id, arr)
  }
  for (const arr of byThread.values()) {
    if (arr.length < 2) continue
    const asc = [...arr].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    asc.forEach((p, i) => roundInfo.set(p.id, { rodada: i + 1, total: asc.length }))
  }

  return (
    <div className="min-h-full px-4 md:px-6 py-6 md:py-8 space-y-6 md:space-y-8" style={{ background: '#FAF8F5' }}>

      {/* Header */}
      <div className="animate-fade-up flex items-end justify-between">
        <h1 className="font-display" style={{ fontSize: 32, fontWeight: 400, color: '#142038', letterSpacing: '-0.02em' }}>
          Pareceres
        </h1>
        <div className="flex flex-col items-end gap-1">
          <input ref={fileInputRef} type="file" accept=".eml" className="hidden" onChange={handleEmlUpload} />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={importing}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
            style={{ background: '#142038', color: '#FAF8F5', opacity: importing ? 0.6 : 1 }}
          >
            {importing ? (
              <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            ) : (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            )}
            {importing ? 'Importando...' : 'Importar Consulta'}
          </button>
          {importError && <p className="text-sm" style={{ color: '#8B2332' }}>{importError}</p>}
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {METRICS.map((m, i) => (
          <div key={m.key} className="animate-count rounded-xl overflow-hidden"
            style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', animationDelay: `${i * 50}ms` }}>
            <div className="h-1" style={{ background: m.tone }} />
            <div className="px-5 py-4">
              <span className="font-display leading-none block"
                style={{ fontSize: 38, fontWeight: 500, color: m.tone, letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums' }}>
                {values[i]}
              </span>
              <span className="text-sm font-medium" style={{ color: '#6B6860' }}>{m.label}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="animate-fade-up" style={{ animationDelay: '180ms' }}>
        <ParecerFilters filters={filters} onChange={handleFiltersChange} />
      </div>

      {/* List */}
      <div className="space-y-2 animate-fade-up" style={{ animationDelay: '240ms' }}>
        {isLoading && Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-xl h-20 animate-pulse" style={{ background: '#EDE8DF' }} />
        ))}
        {isError && (
          <div className="rounded-xl px-5 py-4 text-base" style={{ background: '#8B233218', color: '#8B2332', border: '1.5px solid #8B233222' }}>
            Erro ao carregar pareceres.
          </div>
        )}
        {!isLoading && !isError && sorted.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16">
            <p className="text-base" style={{ color: '#A69B8D' }}>Nenhum parecer encontrado</p>
          </div>
        )}
        {!isLoading && !isError && sorted.map((p, i) => (
          <div key={p.id} style={{ animationDelay: `${240 + i * 40}ms` }}>
            <ParecerCard parecer={p} rodada={roundInfo.get(p.id)} />
          </div>
        ))}
      </div>

      {/* Paginação — backend devolve total; PAGE_SIZE por página (Checklist item 16). */}
      {!isError && (data?.total ?? 0) > PARECERES_PAGE_SIZE && (
        <div className="flex items-center justify-between pt-1">
          <span className="text-sm" style={{ color: '#A69B8D' }}>
            {`${page * PARECERES_PAGE_SIZE + 1}–${Math.min((page + 1) * PARECERES_PAGE_SIZE, data?.total ?? 0)} de ${data?.total ?? 0}`}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1.5 text-sm font-medium rounded-lg transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', color: '#6B6860' }}
            >
              Anterior
            </button>
            <span className="text-sm tabular-nums" style={{ color: '#6B6860' }}>
              {`${page + 1} / ${Math.max(1, Math.ceil((data?.total ?? 0) / PARECERES_PAGE_SIZE))}`}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={(page + 1) * PARECERES_PAGE_SIZE >= (data?.total ?? 0)}
              className="px-3 py-1.5 text-sm font-medium rounded-lg transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', color: '#6B6860' }}
            >
              Próxima
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
