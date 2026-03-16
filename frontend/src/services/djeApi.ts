import api from './api'
import type {
  Movement,
  MovementListResponse,
  MovementMetrics,
  MovementFiltersState,
} from '../types/movement'

export async function fetchMovements(
  filters: MovementFiltersState,
  limit = 50,
  offset = 0
): Promise<MovementListResponse> {
  const params: Record<string, string | number> = { limit, offset }
  if (filters.movement_type) params.movement_type = filters.movement_type
  if (filters.is_read !== '') params.is_read = filters.is_read
  if (filters.search) params.search = filters.search
  const { data } = await api.get<MovementListResponse>('/api/movements', { params })
  return data
}

export async function fetchMovement(id: string): Promise<Movement> {
  const { data } = await api.get<Movement>(`/api/movements/${id}`)
  return data
}

export async function markMovementRead(id: string): Promise<Movement> {
  const { data } = await api.patch<Movement>(`/api/movements/${id}/mark-read`)
  return data
}

export async function fetchMovementMetrics(): Promise<MovementMetrics> {
  const { data } = await api.get<MovementMetrics>('/api/movements/metrics')
  return data
}

export async function fetchUnreadMovements(): Promise<Movement[]> {
  const { data } = await api.get<MovementListResponse>('/api/movements', {
    params: { is_read: 'false', limit: 20, offset: 0 },
  })
  return data.items
}
