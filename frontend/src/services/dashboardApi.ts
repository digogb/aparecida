import api from './api'
import type { PareceresOverview } from '../types/dashboard'

export async function fetchPareceresOverview(): Promise<PareceresOverview> {
  const { data } = await api.get<PareceresOverview>('/api/dashboard/pareceres-overview')
  return data
}
