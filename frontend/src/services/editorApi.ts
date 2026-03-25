import api from './api'
import type { Lawyer, ParecerVersion, PeerReview, PeerReviewListItem } from '../types/parecer'

export interface TrechoRevisado {
  original: string
  revisado: string
  secao: string
}

export interface CorrectionPreview {
  secoes_alteradas: string[]
  revisado: Record<string, string>
  trechos: TrechoRevisado[]
  notas_revisor: string[]
  citacoes_verificar: unknown[]
}

export async function generateParecer(parecerId: string): Promise<ParecerVersion> {
  const { data } = await api.post<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/generate`
  )
  return data
}

export async function saveVersion(
  parecerId: string,
  versionId: string,
  contentHtml: string,
  contentTiptap?: Record<string, unknown>
): Promise<ParecerVersion> {
  const { data } = await api.put<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/versions/${versionId}`,
    { content_html: contentHtml, content_tiptap: contentTiptap }
  )
  return data
}

export async function previewCorrection(
  parecerId: string,
  instructions: string
): Promise<CorrectionPreview> {
  const { data } = await api.post<CorrectionPreview>(
    `/api/parecer-requests/${parecerId}/preview-correction`,
    { observacoes: instructions }
  )
  return data
}

export async function applyCorrection(
  parecerId: string,
  secoes_aprovadas: Record<string, string>,
  observacoes: string,
  notas_revisor: string[],
  citacoes_verificar: unknown[]
): Promise<ParecerVersion> {
  const { data } = await api.post<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/apply-correction`,
    { secoes_aprovadas, observacoes, notas_revisor, citacoes_verificar }
  )
  return data
}

export async function restoreVersion(
  parecerId: string,
  versionId: string
): Promise<ParecerVersion> {
  const { data } = await api.post<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/versions/${versionId}/restore`
  )
  return data
}

export async function approveParecer(
  parecerId: string,
  sendEmail: boolean
): Promise<void> {
  const endpoint = sendEmail
    ? `/api/parecer-requests/${parecerId}/approve-and-send`
    : `/api/parecer-requests/${parecerId}/approve`
  await api.post(endpoint)
}

export async function exportParecer(
  parecerId: string,
  format: 'docx' | 'pdf'
): Promise<Blob> {
  const { data } = await api.post(
    `/api/parecer-requests/${parecerId}/export/${format}`,
    {},
    { responseType: 'blob' }
  )
  return data
}

// ── Peer Review ──────────────────────────────────────────────────────────────

export async function fetchLawyers(): Promise<Lawyer[]> {
  const { data } = await api.get<Lawyer[]>('/api/users/lawyers')
  return data
}

export interface PeerReviewCreatePayload {
  reviewer_id: string
  trechos_marcados: Array<{ texto: string; instrucao: string }>
  observacoes: string
}

export async function createPeerReview(
  parecerId: string,
  payload: PeerReviewCreatePayload
): Promise<PeerReview> {
  const { data } = await api.post<PeerReview>(
    `/api/parecer-requests/${parecerId}/peer-review`,
    payload
  )
  return data
}

export async function fetchPeerReviews(
  parecerId: string
): Promise<PeerReviewListItem[]> {
  const { data } = await api.get<PeerReviewListItem[]>(
    `/api/parecer-requests/${parecerId}/peer-reviews`
  )
  return data
}

export async function fetchPendingReviews(): Promise<PeerReview[]> {
  const { data } = await api.get<PeerReview[]>('/api/peer-reviews/pending')
  return data
}

export interface PeerReviewRespondPayload {
  resposta_geral: string
  resposta_trechos: Array<{ original: string; sugestao: string; comentario: string }>
}

export async function respondToPeerReview(
  reviewId: string,
  payload: PeerReviewRespondPayload
): Promise<PeerReview> {
  const { data } = await api.post<PeerReview>(
    `/api/peer-reviews/${reviewId}/respond`,
    payload
  )
  return data
}

export async function cancelPeerReview(reviewId: string): Promise<PeerReview> {
  const { data } = await api.post<PeerReview>(
    `/api/peer-reviews/${reviewId}/cancel`
  )
  return data
}

// ── Notificações genéricas ───────────────────────────────────────────────────

export interface AppNotification {
  id: string
  user_id: string
  channel: string
  status: string
  title: string
  body: string | null
  link: string | null
  metadata_: Record<string, unknown> | null
  read_at: string | null
  created_at: string
}

export async function fetchAppNotifications(
  limit = 20,
  offset = 0
): Promise<AppNotification[]> {
  const { data } = await api.get<AppNotification[]>('/api/notifications', {
    params: { limit, offset },
  })
  return data
}

export async function fetchUnreadNotificationCount(): Promise<number> {
  const { data } = await api.get<{ count: number }>('/api/notifications/unread-count')
  return data.count
}

export async function markNotificationRead(notificationId: string): Promise<void> {
  await api.patch(`/api/notifications/${notificationId}/read`)
}

