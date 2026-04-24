import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import type { ParecerRequest, ParecerStatus, ParecerTema } from '../../types/parecer'
import { deleteParecer } from '../../services/parecerApi'

const STATUS: Record<ParecerStatus, { label: string; color: string }> = {
  pendente:     { label: 'Pendente',           color: '#C9A94E' },
  classificado: { label: 'Pendente',           color: '#C9A94E' },
  gerado:       { label: 'Aguardando revisão', color: '#A69B8D' },
  em_correcao:  { label: 'Em correção',        color: '#D97706' },
  em_revisao:   { label: 'Aguardando revisão', color: '#A69B8D' },
  devolvido:    { label: 'Devolvido',          color: '#8B2332' },
  aprovado:     { label: 'Aprovado',           color: '#5B7553' },
  enviado:      { label: 'Enviado',            color: '#8C8A82' },
  erro:         { label: 'Erro',               color: '#8B2332' },
}

const TEMA: Record<NonNullable<ParecerTema>, { label: string; color: string }> = {
  licitacao:      { label: 'Licitação',            color: '#C9A94E' },
  administrativo: { label: 'Administrativo geral', color: '#6B6860' },
}

const DELETABLE_STATUSES: ParecerStatus[] = ['devolvido', 'erro']

export default function ParecerCard({ parecer }: { parecer: ParecerRequest }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [deleting, setDeleting] = useState(false)
  const s = STATUS[parecer.status]
  const t = parecer.tema ? TEMA[parecer.tema] : null
  const date = new Date(parecer.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  const enviadoEm = parecer.status === 'enviado' && parecer.updated_at
    ? new Date(parecer.updated_at).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    : null

  async function handleDelete(e: React.MouseEvent) {
    e.stopPropagation()
    if (!confirm('Excluir este email permanentemente?')) return
    setDeleting(true)
    try {
      await deleteParecer(parecer.id)
      await queryClient.invalidateQueries({ queryKey: ['pareceres'] })
      await queryClient.invalidateQueries({ queryKey: ['pareceres-metrics'] })
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div onClick={() => navigate(`/pareceres/${parecer.id}`)}
      className="animate-fade-up rounded-xl px-5 py-4 cursor-pointer transition-all duration-150 hover:brightness-[0.97]"
      style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE' }}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center flex-wrap gap-1.5 mb-2">
            {parecer.numero_parecer && (
              <span className="font-mono text-xs font-medium" style={{ color: '#A69B8D' }}>
                {parecer.numero_parecer}
              </span>
            )}
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-lg"
              style={{ background: `${s.color}18`, color: s.color }}>{s.label}</span>
            {t && (
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-lg"
                style={{ background: `${t.color}18`, color: t.color }}>{t.label}</span>
            )}
          </div>
          <p className="text-base font-medium truncate" style={{ color: '#0A1120' }}>
            {parecer.subject || '(sem assunto)'}
          </p>
          <p className="text-sm mt-1 flex flex-wrap gap-x-1 gap-y-0.5" style={{ color: '#A69B8D' }}>
            <span className="truncate max-w-[200px] xs:max-w-none">{parecer.sender_email || '—'}</span>
            {parecer.municipio_nome && <span>· {parecer.municipio_nome}</span>}
          </p>
          {enviadoEm && (
            <p className="text-sm mt-1" style={{ color: '#5B7553' }}>
              Enviado em {enviadoEm}{parecer.sent_to_email && <span style={{ color: '#A69B8D' }}> · para {parecer.sent_to_email}</span>}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0 mt-0.5">
          <span className="text-xs xs:text-sm" style={{ color: '#A69B8D' }}>{date}</span>
          {DELETABLE_STATUSES.includes(parecer.status) && (
            <button
              onClick={handleDelete}
              disabled={deleting}
              title="Excluir"
              className="p-1.5 rounded-lg transition-all duration-150 hover:brightness-[0.92] disabled:opacity-50 cursor-pointer"
              style={{ background: '#8B233218', color: '#8B2332' }}
            >
              {deleting ? (
                <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
