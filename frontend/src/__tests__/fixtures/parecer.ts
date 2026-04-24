import type { ParecerListResponse, ParecerRequestDetail } from '../../types/parecer'

export const parecerFixture: ParecerRequestDetail = {
  id: 'parecer-1',
  numero_parecer: '001/2026',
  municipio_id: 'municipio-1',
  municipio_nome: 'São Paulo',
  assigned_to: null,
  subject: 'Consulta sobre pregão eletrônico',
  sender_email: 'prefeitura@municipio.sp.gov.br',
  sent_to_email: null,
  status: 'pendente',
  tema: null,
  created_at: '2026-04-01T10:00:00Z',
  updated_at: '2026-04-01T10:00:00Z',
  extracted_text: 'Solicitamos parecer sobre pregão eletrônico 001/2026.',
  attachments: [],
  versions: [],
}

export const parecerClassificadoFixture: ParecerRequestDetail = {
  ...parecerFixture,
  id: 'parecer-2',
  status: 'classificado',
  tema: 'licitacao',
}

export const parecerListFixture: ParecerListResponse = {
  items: [parecerFixture, parecerClassificadoFixture],
  total: 2,
  limit: 100,
  offset: 0,
}
