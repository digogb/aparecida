import { useState } from 'react'
import { usePareceres } from '../../hooks/useParecer'
import type { ParecerFiltersState } from '../../types/parecer'
import ParecerCard from './ParecerCard'
import ParecerFilters from './ParecerFilters'

const EMPTY: ParecerFiltersState = { status: '', tema: '', remetente: '' }

const METRICS = [
  { key: 'total',    label: 'Total',          accent: '#1C1C2E', bg: '#F5F3EE', textColor: '#1C1C2E' },
  { key: 'pend',     label: 'Pendentes',      accent: '#D97706', bg: '#FFFBF0', textColor: '#92400E' },
  { key: 'rev',      label: 'Em Revisão',     accent: '#4F46E5', bg: '#F5F3FF', textColor: '#3730A3' },
  { key: 'sent',     label: 'Enviados / sem.', accent: '#059669', bg: '#F0FDF9', textColor: '#065F46' },
]

export default function ParecerList() {
  const [filters, setFilters] = useState<ParecerFiltersState>(EMPTY)
  const { data, isLoading, isError } = usePareceres(filters)

  const items = data?.items ?? []
  const total = data?.total ?? 0
  const pendentes = items.filter(p => p.status === 'pendente').length
  const emRevisao = items.filter(p => p.status === 'em_revisao').length
  const oneWeekAgo = new Date(); oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  const enviadosSemana = items.filter(p => p.status === 'enviado' && new Date(p.created_at) >= oneWeekAgo).length
  const values = [total, pendentes, emRevisao, enviadosSemana]

  const sorted = [...items].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())

  return (
    <div className="min-h-full px-6 py-7 space-y-7" style={{ background: '#F5F3EE' }}>

        {/* Header */}
        <div className="animate-fade-up">
          <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: '#9CA3AF' }}>Módulo</p>
          <h1 className="font-display" style={{ fontSize: 40, fontWeight: 500, color: '#1C1C2E', letterSpacing: '-0.02em', lineHeight: 1 }}>
            Pareceres
          </h1>
        </div>

        <div style={{ height: 1, background: 'linear-gradient(to right, #1C1C2E22, transparent)' }} />

        {/* Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {METRICS.map((m, i) => (
            <div key={m.key} className="animate-count rounded-2xl overflow-hidden"
              style={{ background: m.bg, border: `1px solid ${m.accent}22`, animationDelay: `${i * 60}ms` }}>
              <div style={{ height: 3, background: m.accent }} />
              <div className="p-4">
                <span className="font-display leading-none block" style={{ fontSize: 38, fontWeight: 600, color: m.accent, letterSpacing: '-0.03em' }}>
                  {values[i]}
                </span>
                <span className="text-xs font-semibold" style={{ color: m.textColor }}>{m.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="animate-fade-up rounded-2xl px-5 py-4" style={{ background: '#fff', border: '1px solid #E5E3DC', animationDelay: '180ms' }}>
          <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#9CA3AF' }}>Filtros</p>
          <ParecerFilters filters={filters} onChange={setFilters} />
        </div>

        {/* List */}
        <div className="space-y-2 animate-fade-up" style={{ animationDelay: '240ms' }}>
          {isLoading && Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-2xl h-20 animate-pulse" style={{ background: '#E9E7E0' }} />
          ))}
          {isError && (
            <div className="rounded-2xl px-5 py-4 text-sm" style={{ background: '#FEE2E2', color: '#991B1B', border: '1px solid #FCA5A522' }}>
              Erro ao carregar pareceres.
            </div>
          )}
          {!isLoading && !isError && sorted.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16" style={{ color: '#9CA3AF' }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="mb-3 opacity-40">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
              </svg>
              <p className="text-sm">Nenhum parecer encontrado</p>
            </div>
          )}
          {!isLoading && !isError && sorted.map((p, i) => (
            <div key={p.id} style={{ animationDelay: `${240 + i * 40}ms` }}>
              <ParecerCard parecer={p} />
            </div>
          ))}
        </div>
      </div>
  )
}
