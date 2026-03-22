import { useNavigate } from 'react-router-dom'
import type { ParecerRequest, ParecerStatus, ParecerTema } from '../../types/parecer'

const STATUS: Record<ParecerStatus, { label: string; color: string }> = {
  pendente:     { label: 'Pendente',           color: '#C4953A' },
  classificado: { label: 'Pendente',           color: '#C4953A' },
  gerado:       { label: 'Aguardando revisão', color: '#A69B8D' },
  em_correcao:  { label: 'Em correção',        color: '#D97706' },
  em_revisao:   { label: 'Aguardando revisão', color: '#A69B8D' },
  devolvido:    { label: 'Devolvido',          color: '#8B2332' },
  aprovado:     { label: 'Aprovado',           color: '#5B7553' },
  enviado:      { label: 'Enviado',            color: '#8C8A82' },
}

const TEMA: Record<NonNullable<ParecerTema>, { label: string; color: string }> = {
  licitacao:      { label: 'Licitação',            color: '#C4953A' },
  administrativo: { label: 'Administrativo geral', color: '#6B6860' },
}

export default function ParecerCard({ parecer }: { parecer: ParecerRequest }) {
  const navigate = useNavigate()
  const s = STATUS[parecer.status]
  const t = parecer.tema ? TEMA[parecer.tema] : null
  const date = new Date(parecer.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
  const enviadoEm = parecer.status === 'enviado' && parecer.updated_at
    ? new Date(parecer.updated_at).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    : null

  return (
    <div onClick={() => navigate(`/pareceres/${parecer.id}`)}
      className="animate-fade-up rounded-xl px-5 py-4 cursor-pointer transition-all duration-150 hover:brightness-[0.97]"
      style={{ background: '#FAF8F5', border: '1.5px solid #DDD9D2' }}>
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
          <p className="text-base font-medium truncate" style={{ color: '#2D2D3A' }}>
            {parecer.subject || '(sem assunto)'}
          </p>
          <p className="text-sm mt-1" style={{ color: '#A69B8D' }}>
            {parecer.sender_email || '—'}
            {parecer.municipio_nome && <span className="ml-1">· {parecer.municipio_nome}</span>}
          </p>
          {enviadoEm && (
            <p className="text-sm mt-1" style={{ color: '#5B7553' }}>
              Enviado em {enviadoEm}{parecer.sent_to_email && <span style={{ color: '#A69B8D' }}> · para {parecer.sent_to_email}</span>}
            </p>
          )}
        </div>
        <span className="text-sm shrink-0" style={{ color: '#A69B8D' }}>{date}</span>
      </div>
    </div>
  )
}
