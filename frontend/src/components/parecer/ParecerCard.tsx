import { useState } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import type { ParecerRequest, ParecerStatus, ParecerTema } from '../../types/parecer'
import { deleteParecer, reprocessParecer } from '../../services/parecerApi'
import { useCurrentUser } from '../../hooks/useCurrentUser'

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

// devolvido/erro não geram versão — não abrem no editor (mostrariam doc vazio).
const NON_EDITABLE_STATUSES: ParecerStatus[] = ['devolvido', 'erro']

export default function ParecerCard({
  parecer,
  rodada,
}: {
  parecer: ParecerRequest
  rodada?: { rodada: number; total: number }
}) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: currentUser } = useCurrentUser()
  const [deleting, setDeleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [reprocessing, setReprocessing] = useState(false)
  const s = STATUS[parecer.status]
  const t = parecer.tema ? TEMA[parecer.tema] : null
  const openable = !NON_EDITABLE_STATUSES.includes(parecer.status)
  // Exclusão liberada ao ADMIN para qualquer parecer não enviado (auditoria — Erro 1).
  // A permissão também é validada no servidor (DELETE só passa com role admin).
  const canDelete = currentUser?.role === 'admin' && parecer.status !== 'enviado'
  const date = new Date(parecer.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  const enviadoEm = parecer.status === 'enviado' && parecer.updated_at
    ? new Date(parecer.updated_at).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    : null

  const rotuloParecer = parecer.numero_parecer || parecer.subject || 'este parecer'

  async function confirmDelete() {
    setDeleting(true)
    try {
      await deleteParecer(parecer.id)
      setShowDeleteConfirm(false)
      await queryClient.invalidateQueries({ queryKey: ['pareceres'] })
      await queryClient.invalidateQueries({ queryKey: ['dashboard', 'pareceres-overview'] })
    } finally {
      setDeleting(false)
    }
  }

  async function handleReprocess(e: React.MouseEvent) {
    e.stopPropagation()
    setReprocessing(true)
    try {
      await reprocessParecer(parecer.id)
      await queryClient.invalidateQueries({ queryKey: ['pareceres'] })
      await queryClient.invalidateQueries({ queryKey: ['dashboard', 'pareceres-overview'] })
    } catch {
      setReprocessing(false)
    }
  }

  return (
    <div onClick={openable ? () => navigate(`/pareceres/${parecer.id}`) : undefined}
      className={`animate-fade-up rounded-xl px-5 py-4 transition-all duration-150 ${openable ? 'cursor-pointer hover:brightness-[0.97]' : 'cursor-default'}`}
      style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}>
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
            {rodada && rodada.total > 1 && (
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-lg"
                title="Rodada desta consulta na mesma thread de e-mail"
                style={{ background: '#14203818', color: '#142038' }}>
                rodada {rodada.rodada}/{rodada.total}
              </span>
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
          {parecer.status === 'erro' && (
            <button
              onClick={handleReprocess}
              disabled={reprocessing}
              title="Reprocessar"
              className="p-1.5 rounded-lg transition-all duration-150 hover:brightness-[0.92] disabled:opacity-50 cursor-pointer"
              style={{ background: '#5B755318', color: '#5B7553' }}
            >
              {reprocessing ? (
                <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              )}
            </button>
          )}
          {canDelete && (
            <button
              onClick={(e) => { e.stopPropagation(); setShowDeleteConfirm(true) }}
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
      {parecer.motivo && (parecer.status === 'devolvido' || parecer.status === 'erro') && (
        <div
          className="mt-3 px-3 py-2 rounded-lg text-sm flex items-start gap-2"
          style={{ background: '#8B233210', color: '#8B2332', border: '1px solid #8B233233' }}
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mt-0.5 shrink-0"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span className="leading-snug">
            <span className="font-semibold">
              {parecer.status === 'devolvido' ? 'Não gerado: ' : 'Erro: '}
            </span>
            {parecer.motivo}
          </span>
        </div>
      )}

      {/* Confirmação de exclusão — padrão de modal do sistema (auditoria — Erro 1).
          Renderizado via portal no body: a lista tem ancestral com `transform`
          (animate-fade-up), o que prenderia um `position: fixed` ao card. */}
      {showDeleteConfirm && createPortal(
        <div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          style={{ background: 'rgba(27,40,56,0.5)' }}
          onClick={(e) => { e.stopPropagation(); if (!deleting) setShowDeleteConfirm(false) }}
        >
          <div
            className="rounded-2xl w-full max-w-md overflow-hidden cursor-default"
            style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4" style={{ borderBottom: '1px solid #EDE8DF' }}>
              <h3 className="text-base font-semibold" style={{ color: '#0A1120' }}>Excluir parecer</h3>
              <p className="text-sm mt-0.5" style={{ color: '#A69B8D' }}>Esta ação é permanente e não pode ser desfeita.</p>
            </div>
            <div className="px-6 py-4">
              <p className="text-sm" style={{ color: '#0A1120' }}>
                Tem certeza que deseja excluir <span className="font-semibold">{rotuloParecer}</span>?
              </p>
            </div>
            <div className="px-6 py-4 flex items-center justify-end gap-2" style={{ borderTop: '1px solid #EDE8DF' }}>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer disabled:opacity-50"
                style={{ background: '#EDE8DF', color: '#6B6860' }}
              >
                Cancelar
              </button>
              <button
                onClick={confirmDelete}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                style={{ background: '#8B2332', color: '#FAF8F5' }}
              >
                {deleting && <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
                {deleting ? 'Excluindo...' : 'Excluir'}
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  )
}
