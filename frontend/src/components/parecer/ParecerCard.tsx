import { useNavigate } from 'react-router-dom'
import type { ParecerRequest, ParecerStatus, ParecerTema } from '../../types/parecer'

const STATUS_STYLES: Record<ParecerStatus, string> = {
  pendente: 'bg-yellow-100 text-yellow-800',
  classificado: 'bg-blue-100 text-blue-800',
  gerado: 'bg-purple-100 text-purple-800',
  em_revisao: 'bg-orange-100 text-orange-800',
  devolvido: 'bg-red-100 text-red-800',
  aprovado: 'bg-green-100 text-green-800',
  enviado: 'bg-teal-100 text-teal-800',
}

const STATUS_LABELS: Record<ParecerStatus, string> = {
  pendente: 'Pendente',
  classificado: 'Classificado',
  gerado: 'Gerado',
  em_revisao: 'Em Revisão',
  devolvido: 'Devolvido',
  aprovado: 'Aprovado',
  enviado: 'Enviado',
}

const TEMA_STYLES: Record<NonNullable<ParecerTema>, string> = {
  administrativo: 'bg-indigo-100 text-indigo-800',
  tributario: 'bg-amber-100 text-amber-800',
  financeiro: 'bg-cyan-100 text-cyan-800',
  previdenciario: 'bg-pink-100 text-pink-800',
  licitacao: 'bg-lime-100 text-lime-800',
}

const TEMA_LABELS: Record<NonNullable<ParecerTema>, string> = {
  administrativo: 'Administrativo',
  tributario: 'Tributário',
  financeiro: 'Financeiro',
  previdenciario: 'Previdenciário',
  licitacao: 'Licitação',
}

interface ParecerCardProps {
  parecer: ParecerRequest
}

export default function ParecerCard({ parecer }: ParecerCardProps) {
  const navigate = useNavigate()

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  }

  return (
    <div
      onClick={() => navigate(`/pareceres/${parecer.id}`)}
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-indigo-300 cursor-pointer transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {parecer.numero_parecer && (
              <span className="text-xs font-mono font-semibold text-gray-500">
                #{parecer.numero_parecer}
              </span>
            )}
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[parecer.status]}`}>
              {STATUS_LABELS[parecer.status]}
            </span>
            {parecer.tema && (
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${TEMA_STYLES[parecer.tema]}`}>
                {TEMA_LABELS[parecer.tema]}
              </span>
            )}
          </div>
          <p className="text-sm font-medium text-gray-900 truncate">
            {parecer.subject || '(sem assunto)'}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {parecer.sender_email || '—'}
            {parecer.municipio_nome && (
              <span className="ml-1 text-gray-400">· {parecer.municipio_nome}</span>
            )}
          </p>
        </div>
        <span className="text-xs text-gray-400 whitespace-nowrap shrink-0">
          {formatDate(parecer.created_at)}
        </span>
      </div>
    </div>
  )
}
