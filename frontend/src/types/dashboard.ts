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
