import api from './api'
import type { ParecerFiltersState, ParecerListResponse, ParecerRequestDetail } from '../types/parecer'

export async function fetchPareceres(
  filters: ParecerFiltersState,
  limit = 100,
  offset = 0
): Promise<ParecerListResponse> {
  const params: Record<string, string | number> = { limit, offset }
  if (filters.status) params.status = filters.status
  if (filters.tema) params.tema = filters.tema
  if (filters.remetente) params.remetente = filters.remetente
  const { data } = await api.get<ParecerListResponse>('/api/parecer-requests', { params })
  return data
}

export async function fetchParecer(id: string): Promise<ParecerRequestDetail> {
  const { data } = await api.get<ParecerRequestDetail>(`/api/parecer-requests/${id}`)
  return data
}

export async function deleteParecer(id: string): Promise<void> {
  await api.delete(`/api/parecer-requests/${id}`)
}
