import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchMovements,
  fetchMovement,
  fetchMovementMetrics,
  markMovementRead,
  triggerDjeSearch,
} from '../services/djeApi'
import type { MovementFiltersState } from '../types/movement'

const PAGE_SIZE = 50

export function useMovements(filters: MovementFiltersState, page = 0) {
  return useQuery({
    queryKey: ['movements', filters, page],
    queryFn: () => fetchMovements(filters, PAGE_SIZE, page * PAGE_SIZE),
    staleTime: 30_000,
    placeholderData: (prev) => prev,
  })
}

export { PAGE_SIZE }

export function useMovement(id: string | undefined) {
  return useQuery({
    queryKey: ['movement', id],
    queryFn: () => fetchMovement(id!),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useMovementMetrics() {
  return useQuery({
    queryKey: ['movement-metrics'],
    queryFn: fetchMovementMetrics,
    staleTime: 60_000,
  })
}

export function useMarkMovementRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: markMovementRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['movements'] })
      queryClient.invalidateQueries({ queryKey: ['movement-metrics'] })
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useDjeSync() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: triggerDjeSearch,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['movements'] })
      queryClient.invalidateQueries({ queryKey: ['movement-metrics'] })
    },
  })
}
