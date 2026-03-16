import { useQuery } from '@tanstack/react-query'
import { fetchParecer, fetchPareceres } from '../services/parecerApi'
import type { ParecerFiltersState } from '../types/parecer'

export function usePareceres(filters: ParecerFiltersState) {
  return useQuery({
    queryKey: ['pareceres', filters],
    queryFn: () => fetchPareceres(filters),
    staleTime: 30_000,
  })
}

export function useParecer(id: string | undefined) {
  return useQuery({
    queryKey: ['parecer', id],
    queryFn: () => fetchParecer(id!),
    enabled: !!id,
    staleTime: 30_000,
  })
}
