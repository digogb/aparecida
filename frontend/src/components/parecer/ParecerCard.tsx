import { useNavigate } from 'react-router-dom'
import type { ParecerRequest, ParecerStatus, ParecerTema } from '../../types/parecer'

const STATUS: Record<ParecerStatus, { label: string; color: string; bg: string }> = {
  pendente:     { label: 'Pendente',     color: '#92400E', bg: '#FEF3C7' },
  classificado: { label: 'Classificado', color: '#1E40AF', bg: '#DBEAFE' },
  gerado:       { label: 'Gerado',       color: '#3730A3', bg: '#E0E7FF' },
  em_revisao:   { label: 'Em Revisão',   color: '#5B21B6', bg: '#EDE9FE' },
  devolvido:    { label: 'Devolvido',    color: '#991B1B', bg: '#FEE2E2' },
  aprovado:     { label: 'Aprovado',     color: '#065F46', bg: '#D1FAE5' },
  enviado:      { label: 'Enviado',      color: '#374151', bg: '#F3F4F6' },
}

const TEMA: Record<NonNullable<ParecerTema>, { label: string; color: string; bg: string }> = {
  administrativo: { label: 'Administrativo', color: '#3730A3', bg: '#E0E7FF' },
  tributario:     { label: 'Tributário',     color: '#92400E', bg: '#FEF3C7' },
  financeiro:     { label: 'Financeiro',     color: '#0C4A6E', bg: '#E0F2FE' },
  previdenciario: { label: 'Previdenciário', color: '#701A75', bg: '#FAE8FF' },
  licitacao:      { label: 'Licitação',      color: '#3F6212', bg: '#ECFCCB' },
}

export default function ParecerCard({ parecer }: { parecer: ParecerRequest }) {
  const navigate = useNavigate()
  const s = STATUS[parecer.status]
  const t = parecer.tema ? TEMA[parecer.tema] : null
  const date = new Date(parecer.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

  return (
    <div onClick={() => navigate(`/pareceres/${parecer.id}`)}
      className="animate-fade-up rounded-2xl px-5 py-4 cursor-pointer transition-all hover:shadow-md hover:-translate-y-px"
      style={{ background: '#fff', border: '1px solid #E5E3DC' }}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center flex-wrap gap-1.5 mb-2">
            {parecer.numero_parecer && (
              <span className="font-mono text-xs font-bold" style={{ color: '#9CA3AF' }}>
                {parecer.numero_parecer}
              </span>
            )}
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full"
              style={{ background: s.bg, color: s.color }}>{s.label}</span>
            {t && (
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full"
                style={{ background: t.bg, color: t.color }}>{t.label}</span>
            )}
          </div>
          <p className="text-sm font-semibold truncate" style={{ color: '#1C1C2E' }}>
            {parecer.subject || '(sem assunto)'}
          </p>
          <p className="text-xs mt-1" style={{ color: '#9CA3AF' }}>
            {parecer.sender_email || '—'}
            {parecer.municipio_nome && <span className="ml-1">· {parecer.municipio_nome}</span>}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <span className="text-xs" style={{ color: '#9CA3AF' }}>{date}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D1D5DB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
      </div>
    </div>
  )
}
