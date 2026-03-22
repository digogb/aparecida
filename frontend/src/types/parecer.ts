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

export interface ParecerRequest {
  id: string
  numero_parecer: string | null
  municipio_id: string | null
  municipio_nome?: string | null
  assigned_to: string | null
  subject: string | null
  sender_email: string | null
  sent_to_email: string | null
  status: ParecerStatus
  tema: ParecerTema | null
  created_at: string
  updated_at: string
}

export interface ParecerRequestDetail extends ParecerRequest {
  extracted_text: string | null
  attachments: Attachment[]
  versions: ParecerVersion[]
}

export interface Attachment {
  id: string
  filename: string
  content_type: string | null
  size_bytes: number | null
  extraction_status: string | null
  created_at: string
}

export interface ParecerVersion {
  id: string
  version_number: number
  source: string
  content_tiptap: Record<string, unknown> | null
  content_html: string | null
  created_at: string
  updated_at: string
}

export interface ParecerListResponse {
  items: ParecerRequest[]
  total: number
  limit: number
  offset: number
}

export interface ParecerFiltersState {
  status: ParecerStatus | ''
  tema: ParecerTema | ''
  remetente: string
}

export interface ParecerMetrics {
  total: number
  pendentes: number
  em_revisao: number
  enviados_semana: number
}
