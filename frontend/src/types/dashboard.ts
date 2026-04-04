export interface DashboardStats {
  aguardando_revisao: number
  em_revisao: number
  movimentacoes_nao_lidas: number
  tarefas_urgentes: number
  concluidas_semana: number
  enviados_total: number
}

export type AlertType = 'parecer_atrasado' | 'intimacao_nao_lida' | 'prazo_proximo' | 'revisao_solicitada'
export type AlertUrgency = 'high' | 'medium'

export interface DashboardAlert {
  id: string
  type: AlertType
  urgency: AlertUrgency
  title: string
  description: string
  ref_id?: string
  ref_path?: string
}

export interface DashboardAlertsResponse {
  alerts: DashboardAlert[]
}

export interface RecentParecer {
  id: string
  subject: string | null
  status: string
  municipio_nome: string | null
  created_at: string
}

export interface RecentMovement {
  id: string
  process_number: string
  type: string
  tipo_documento: string | null
  published_at: string | null
  created_at: string
  is_read: boolean
}

export interface DashboardRecent {
  pareceres: RecentParecer[]
  movimentacoes: RecentMovement[]
}

// --- Pareceres Overview ---

export interface PipelineStage {
  status: string
  label: string
  count: number
}

export interface MunicipioItem {
  municipio_id: string | null
  municipio_nome: string
  count: number
}

export interface AdvogadoItem {
  user_id: string | null
  user_name: string
  count: number
}

export interface OldestParecer {
  id: string
  subject: string | null
  status: string
  municipio_nome: string | null
  created_at: string
  dias_aberto: number
}

export interface PareceresOverview {
  pipeline: PipelineStage[]
  por_municipio: MunicipioItem[]
  por_advogado: AdvogadoItem[]
  mais_antigos: OldestParecer[]
  total_abertos: number
  concluidos_semana: number
}
