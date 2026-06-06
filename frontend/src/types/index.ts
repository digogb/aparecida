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

export interface TokenResponse {
  access_token: string
  token_type: string
}
