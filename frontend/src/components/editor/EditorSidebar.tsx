import { useMemo, useState } from 'react'
import type { ParecerRequestDetail, ParecerVersion } from '../../types/parecer'
import type { ReviewFlowStep } from '../../types/editor'
import { restoreVersion, fetchPeerReviews } from '../../services/editorApi'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import PeerReviewPanel from './PeerReviewPanel'

function getCurrentUserId(): string {
  try {
    const token = localStorage.getItem('token')
    if (!token) return ''
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub ?? ''
  } catch {
    return ''
  }
}

interface Props {
  parecer: ParecerRequestDetail
  activeVersion: ParecerVersion | null
  onVersionSelect: (version: ParecerVersion) => void
  onVersionRestored: (version: ParecerVersion) => void
}

const statusLabels: Record<string, string> = {
  pendente: 'Pendente',
  classificado: 'Pendente',
  gerado: 'Aguardando revisão',
  em_correcao: 'Em correção',
  em_revisao: 'Aguardando revisão',
  devolvido: 'Devolvido',
  aprovado: 'Aprovado',
  enviado: 'Enviado',
}

function getReviewFlow(status: string, hasPeerReview: boolean): ReviewFlowStep[] {
  if (status === 'devolvido') {
    return [
      { label: 'Recebido', status: 'done' },
      { label: 'IA processando', status: 'done' },
      { label: 'Devolvido', status: 'current' },
    ]
  }
  if (status === 'erro') {
    return [
      { label: 'Recebido', status: 'done' },
      { label: 'IA processando', status: 'current' },
      { label: 'Erro no processamento', status: 'pending' },
    ]
  }

  const base: ReviewFlowStep[] = [
    { label: 'Recebido', status: 'done' },
    { label: 'IA processando', status: 'pending' },
    { label: 'Aguardando revisão', status: 'pending' },
    { label: 'Em correção', status: 'pending' },
  ]

  if (hasPeerReview) {
    base.push({ label: 'Revisão colega', status: 'pending' })
  }

  base.push({ label: 'Aprovado', status: 'pending' })
  base.push({ label: 'Enviado', status: 'pending' })

  const peerIdx = hasPeerReview ? 4 : -1
  const approvedIdx = hasPeerReview ? 5 : 4
  const enviadoIdx = hasPeerReview ? 6 : 5

  const statusToStep: Record<string, number> = {
    pendente: 0, classificado: 1, gerado: 2, em_correcao: 3,
    em_revisao: peerIdx !== -1 ? peerIdx : 3,
    aprovado: approvedIdx, enviado: enviadoIdx,
  }

  const idx = statusToStep[status] ?? -1
  for (let i = 0; i <= idx && i < base.length; i++) {
    base[i].status = i === idx ? 'current' : 'done'
  }
  return base
}

function formatBytes(bytes: number | null): string {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const VERSION_SOURCE_LABELS: Record<string, string> = {
  ia_gerado: 'IA',
  ia_reprocessado: 'Correção IA',
  manual_edit: 'Manual',
  restaurado: 'Restaurada',
  peer_review: 'Revisão colega',
}

export default function EditorSidebar({
  parecer,
  activeVersion,
  onVersionSelect,
  onVersionRestored,
}: Props) {
  const [isRestoring, setIsRestoring] = useState(false)
  const [showRestoreConfirm, setShowRestoreConfirm] = useState(false)
  const queryClient = useQueryClient()
  const currentUserId = useMemo(() => getCurrentUserId(), [])

  const { data: peerReviews = [] } = useQuery({
    queryKey: ['peer-reviews', parecer.id],
    queryFn: () => fetchPeerReviews(parecer.id),
    staleTime: 10_000,
  })
  const hasPeerReview = peerReviews.length > 0

  const flow = getReviewFlow(parecer.status, hasPeerReview)
  const sortedVersions = [...parecer.versions].sort(
    (a, b) => b.version_number - a.version_number
  )
  const latestVersionNumber = sortedVersions[0]?.version_number ?? 0
  const isViewingOld = activeVersion !== null && activeVersion.version_number < latestVersionNumber

  async function handleRestore() {
    if (!activeVersion) return
    setIsRestoring(true)
    try {
      const newVersion = await restoreVersion(parecer.id, activeVersion.id)
      queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
      onVersionRestored(newVersion)
    } catch (err) {
      console.error('Restore failed:', err)
    } finally {
      setIsRestoring(false)
      setShowRestoreConfirm(false)
    }
  }

  return (
    <aside className="w-[220px] overflow-y-auto flex-shrink-0" style={{ borderLeft: '1px solid #EDE8DF', background: '#EDE8DF' }}>
      {/* Info */}
      <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
        <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
          Informações
        </h3>
        <dl className="space-y-1 text-sm">
          <div>
            <dt className="text-sm" style={{ color: '#A69B8D' }}>Remetente</dt>
            <dd className="truncate" style={{ color: '#0A1120' }}>{parecer.sender_email || '—'}</dd>
          </div>
          <div>
            <dt className="text-sm" style={{ color: '#A69B8D' }}>Data</dt>
            <dd style={{ color: '#0A1120' }}>{formatDate(parecer.created_at)}</dd>
          </div>
          <div>
            <dt className="text-sm" style={{ color: '#A69B8D' }}>Município</dt>
            <dd style={{ color: '#0A1120' }}>{parecer.municipio_nome || '—'}</dd>
          </div>
          <div>
            <dt className="text-sm" style={{ color: '#A69B8D' }}>Tema</dt>
            <dd className="capitalize" style={{ color: '#0A1120' }}>{parecer.tema || '—'}</dd>
          </div>
          <div>
            <dt className="text-sm" style={{ color: '#A69B8D' }}>Status</dt>
            <dd style={{ color: '#0A1120' }}>
              {statusLabels[parecer.status] || parecer.status}
            </dd>
          </div>
        </dl>
      </div>

      {/* Attachments */}
      {parecer.attachments.length > 0 && (
        <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
          <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
            Anexos
          </h3>
          <ul className="space-y-1">
            {parecer.attachments.map((att) => (
              <li key={att.id}>
                <a
                  href={`/api/attachments/${att.id}/file`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm truncate block"
                  style={{ color: '#C9A94E' }}
                  title={att.filename}
                >
                  {att.filename}
                </a>
                <span className="text-sm" style={{ color: '#A69B8D' }}>
                  {formatBytes(att.size_bytes)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Review Flow */}
      <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
        <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
          Fluxo de Revisão
        </h3>
        <ol className="space-y-1">
          {flow.map((step, i) => (
            <li key={i} className="flex items-center gap-2 text-sm">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{
                  background:
                    step.status === 'done'
                      ? '#5B7553'
                      : step.status === 'current'
                        ? '#C9A94E'
                        : '#E0D9CE',
                }}
              />
              <span
                style={{
                  color:
                    step.status === 'current'
                      ? '#C9A94E'
                      : step.status === 'done'
                        ? '#6B6860'
                        : '#A69B8D',
                  fontWeight: step.status === 'current' ? 500 : 400,
                }}
              >
                {step.label}
              </span>
            </li>
          ))}
        </ol>
      </div>

      {/* Versions */}
      <div className="p-3">
        <h3 className="text-sm font-medium uppercase tracking-widest mb-2" style={{ color: '#A69B8D' }}>
          Versões
        </h3>
        {isViewingOld && !showRestoreConfirm && (
          <button
            onClick={() => setShowRestoreConfirm(true)}
            className="w-full mb-2 px-2 py-1.5 text-sm rounded-lg transition-all duration-150 cursor-pointer"
            style={{ background: '#C9A94E18', border: '1.5px solid #C9A94E44', color: '#C9A94E' }}
          >
            ↩ Restaurar v{activeVersion?.version_number}
          </button>
        )}
        {isViewingOld && showRestoreConfirm && (
          <div className="mb-2 p-2 rounded-lg text-sm space-y-2" style={{ background: '#C9A94E12', border: '1.5px solid #C9A94E44' }}>
            <p style={{ color: '#6B6860' }}>
              Restaurar a <strong style={{ color: '#0A1120' }}>v{activeVersion?.version_number}</strong> como nova versão?
            </p>
            <div className="flex gap-1.5">
              <button
                onClick={handleRestore}
                disabled={isRestoring}
                className="flex-1 px-2 py-1 text-sm font-medium rounded-lg cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: '#C9A94E', color: '#F5F0E8' }}
              >
                {isRestoring ? 'Restaurando...' : 'Confirmar'}
              </button>
              <button
                onClick={() => setShowRestoreConfirm(false)}
                disabled={isRestoring}
                className="flex-1 px-2 py-1 text-sm rounded-lg cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ color: '#6B6860', border: '1px solid #E0D9CE' }}
              >
                Cancelar
              </button>
            </div>
          </div>
        )}
        <ul className="space-y-1">
          {sortedVersions.map((v) => (
            <li key={v.id}>
              <button
                onClick={() => onVersionSelect(v)}
                className="w-full text-left px-2 py-1 rounded-lg text-sm transition-all duration-150 cursor-pointer"
                style={
                  activeVersion?.id === v.id
                    ? { background: '#C9A94E18', color: '#C9A94E', fontWeight: 500 }
                    : { color: '#6B6860' }
                }
              >
                <div className="flex items-center gap-1.5">
                  <span>v{v.version_number}</span>
                  <span
                    className="text-xs px-1.5 py-0.5 rounded"
                    style={
                      v.source === 'peer_review'
                        ? { background: '#14203818', color: '#142038' }
                        : { background: '#EDE8DF', color: '#A69B8D' }
                    }
                  >
                    {VERSION_SOURCE_LABELS[v.source] ?? v.source}
                  </span>
                </div>
                <div style={{ color: '#A69B8D' }}>{formatDate(v.created_at)}</div>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Peer Reviews */}
      <PeerReviewPanel parecerId={parecer.id} currentUserId={currentUserId} />
    </aside>
  )
}
