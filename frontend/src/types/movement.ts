import type { MovementType } from './index'

export type { MovementType }

export interface Movement {
  id: string
  process_number: string
  movement_type: MovementType
  publication_date: string
  deadline_date: string | null
  summary: string
  full_text: string
  is_read: boolean
  municipio_id: string | null
  municipio_nome: string | null
  created_at: string
  updated_at: string
}

export interface MovementListResponse {
  items: Movement[]
  total: number
  limit: number
  offset: number
}

export interface MovementMetrics {
  total: number
  nao_lidas: number
  com_prazo_hoje: number
  com_prazo_semana: number
}

export interface MovementFiltersState {
  movement_type: MovementType | ''
  is_read: 'true' | 'false' | ''
  search: string
}

export interface Notification {
  id: string
  movement_id: string
  process_number: string
  movement_type: MovementType
  summary: string
  publication_date: string
  is_read: boolean
}
