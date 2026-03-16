import type { ParecerRequestDetail, ParecerVersion } from '../../types/parecer'
import type { ReviewFlowStep } from '../../types/editor'

interface Props {
  parecer: ParecerRequestDetail
  activeVersion: ParecerVersion | null
  onVersionSelect: (version: ParecerVersion) => void
}

const statusLabels: Record<string, string> = {
  pendente: 'Pendente',
  classificado: 'Classificado',
  gerado: 'Gerado',
  em_revisao: 'Em Revisão',
  devolvido: 'Devolvido',
  aprovado: 'Aprovado',
  enviado: 'Enviado',
}

function getReviewFlow(status: string): ReviewFlowStep[] {
  const steps: ReviewFlowStep[] = [
    { label: 'Recebido', status: 'done' },
    { label: 'Classificado', status: 'pending' },
    { label: 'IA Gerou', status: 'pending' },
    { label: 'Em Revisão', status: 'pending' },
    { label: 'Aprovado', status: 'pending' },
    { label: 'Enviado', status: 'pending' },
  ]
  const order = ['pendente', 'classificado', 'gerado', 'em_revisao', 'aprovado', 'enviado']
  const idx = order.indexOf(status)
  for (let i = 0; i <= idx && i < steps.length; i++) {
    steps[i].status = i === idx ? 'current' : 'done'
  }
  return steps
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

export default function EditorSidebar({
  parecer,
  activeVersion,
  onVersionSelect,
}: Props) {
  const flow = getReviewFlow(parecer.status)
  const sortedVersions = [...parecer.versions].sort(
    (a, b) => b.version_number - a.version_number
  )

  return (
    <aside className="w-[220px] border-l border-gray-200 bg-gray-50 overflow-y-auto flex-shrink-0">
      {/* Info */}
      <div className="p-3 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
          Informações
        </h3>
        <dl className="space-y-1 text-sm">
          <div>
            <dt className="text-gray-500 text-xs">Remetente</dt>
            <dd className="text-gray-900 truncate">{parecer.sender_email || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">Data</dt>
            <dd className="text-gray-900">{formatDate(parecer.created_at)}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">Município</dt>
            <dd className="text-gray-900">{parecer.municipio_nome || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">Tema</dt>
            <dd className="text-gray-900 capitalize">{parecer.tema || '—'}</dd>
          </div>
          <div>
            <dt className="text-gray-500 text-xs">Status</dt>
            <dd className="text-gray-900">
              {statusLabels[parecer.status] || parecer.status}
            </dd>
          </div>
        </dl>
      </div>

      {/* Attachments */}
      {parecer.attachments.length > 0 && (
        <div className="p-3 border-b border-gray-200">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
            Anexos
          </h3>
          <ul className="space-y-1">
            {parecer.attachments.map((att) => (
              <li key={att.id}>
                <a
                  href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/attachments/${att.id}/download`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:underline truncate block"
                  title={att.filename}
                >
                  {att.filename}
                </a>
                <span className="text-xs text-gray-400">
                  {formatBytes(att.size_bytes)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Review Flow */}
      <div className="p-3 border-b border-gray-200">
        <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
          Fluxo de Revisão
        </h3>
        <ol className="space-y-1">
          {flow.map((step, i) => (
            <li key={i} className="flex items-center gap-2 text-xs">
              <span
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  step.status === 'done'
                    ? 'bg-green-500'
                    : step.status === 'current'
                      ? 'bg-indigo-500'
                      : 'bg-gray-300'
                }`}
              />
              <span
                className={
                  step.status === 'current'
                    ? 'text-indigo-700 font-medium'
                    : step.status === 'done'
                      ? 'text-gray-600'
                      : 'text-gray-400'
                }
              >
                {step.label}
              </span>
            </li>
          ))}
        </ol>
      </div>

      {/* Versions */}
      <div className="p-3">
        <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
          Versões
        </h3>
        <ul className="space-y-1">
          {sortedVersions.map((v) => (
            <li key={v.id}>
              <button
                onClick={() => onVersionSelect(v)}
                className={`w-full text-left px-2 py-1 rounded text-xs transition-colors ${
                  activeVersion?.id === v.id
                    ? 'bg-indigo-100 text-indigo-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <div>v{v.version_number} — {v.source}</div>
                <div className="text-gray-400">{formatDate(v.created_at)}</div>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  )
}
