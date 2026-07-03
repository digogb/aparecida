import api from './api'
import type { Annotation } from '../types/parecer'

export async function fetchAnnotations(parecerId: string): Promise<Annotation[]> {
  const { data } = await api.get<Annotation[]>(`/api/parecer-requests/${parecerId}/annotations`)
  return data
}

export async function createAnnotation(
  parecerId: string,
  trecho_texto: string,
  questionamento: string,
): Promise<Annotation> {
  const { data } = await api.post<Annotation>(
    `/api/parecer-requests/${parecerId}/annotations`,
    { trecho_texto, questionamento },
  )
  return data
}

export async function deleteAnnotation(annotationId: string): Promise<void> {
  await api.delete(`/api/annotations/${annotationId}`)
}
