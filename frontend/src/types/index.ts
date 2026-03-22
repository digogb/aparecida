export type UserRole = 'advogado' | 'secretaria' | 'admin'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export type ParecerStatus =
  | 'pendente'
  | 'classificado'
  | 'gerado'
  | 'em_correcao'
  | 'em_revisao'
  | 'devolvido'
  | 'aprovado'
  | 'enviado'

export type ParecerTema =
  | 'administrativo'
  | 'licitacao'

export type MovementType =
  | 'intimacao'
  | 'sentenca'
  | 'despacho'
  | 'acordao'
  | 'publicacao'
  | 'distribuicao'
  | 'outros'

export type TaskPriority = 'high' | 'medium' | 'low'
export type TaskCategory = 'judicial' | 'administrativa' | 'parecer' | 'publicacao_dje' | 'prazo'

export interface Task {
  id: string
  column_id: string
  title: string
  description?: string
  category?: TaskCategory
  priority: TaskPriority
  assigned_to?: string
  due_date?: string
  position: number
  created_at: string
  updated_at: string
}

export interface Column {
  id: string
  board_id: string
  name: string
  position: number
  wip_limit?: number
  tasks: Task[]
}

export interface Board {
  id: string
  name: string
  columns: Column[]
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
