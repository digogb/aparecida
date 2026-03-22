import api from './api'
import type { ParecerVersion } from '../types/parecer'

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

