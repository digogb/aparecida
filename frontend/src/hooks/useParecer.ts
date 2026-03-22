import { useQuery } from '@tanstack/react-query'
import { fetchParecer, fetchPareceres } from '../services/parecerApi'
import type { ParecerFiltersState } from '../types/parecer'

const PROCESSING = new Set(['pendente', 'classificado'])

export function usePareceres(filters: ParecerFiltersState) {
  return useQuery({
    queryKey: ['pareceres', filters],
    queryFn: () => fetchPareceres(filters),
    staleTime: 30_000,
    refetchInterval: (query) => {
      const items = query.state.data?.items ?? []
      return items.some(p => PROCESSING.has(p.status)) ? 3000 : false
    },
  })
}

const EMPTY_FILTERS: ParecerFiltersState = { status: '', tema: '', remetente: '' }

export function useParecerMetrics() {
  return useQuery({
    queryKey: ['pareceres-metrics'],
    queryFn: () => fetchPareceres(EMPTY_FILTERS),
    staleTime: 30_000,
    refetchInterval: (query) => {
      const items = query.state.data?.items ?? []
      return items.some(p => PROCESSING.has(p.status)) ? 3000 : false
    },
  })
}

export function useParecer(id: string | undefined) {
  return useQuery({
    queryKey: ['parecer', id],
    queryFn: () => fetchParecer(id!),
    enabled: !!id,
    staleTime: 30_000,
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return false
      // Poll while pipeline is still processing (classified but no versions yet)
      const isProcessing =
        (data.status === 'classificado' || data.status === 'pendente') &&
        (!data.versions || data.versions.length === 0)
      return isProcessing ? 2000 : false
    },
  })
}
