import api from './api'
import type { ParecerVersion } from '../types/parecer'

export async function generateParecer(parecerId: string): Promise<ParecerVersion> {
  const { data } = await api.post<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/generate`
  )
  return data
}

export async function saveVersion(
  parecerId: string,
  versionId: string,
  contentHtml: string
): Promise<ParecerVersion> {
  const { data } = await api.put<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/versions/${versionId}`,
    { content_html: contentHtml }
  )
  return data
}

export async function returnToAI(
  parecerId: string,
  instructions: string
): Promise<ParecerVersion> {
  const { data } = await api.post<ParecerVersion>(
    `/api/parecer-requests/${parecerId}/reprocess`,
    { observacoes: instructions }
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

export async function requestCorrection(parecerId: string): Promise<void> {
  await api.post(`/api/parecer-requests/${parecerId}/return`, {
    observacoes: 'Solicitação de correção manual',
  })
}
