import { useMemo } from 'react'
import { extrairMarcadoresRevisao, type MarcadorRevisao } from '../../utils/revisaoMarkers'

interface Props {
  /** TipTap JSON da versão ativa do parecer */
  tiptap: unknown
}

/**
 * Painel lateral da Camada 6 — lista os marcadores `[REVISAR — ...]` e
 * `[!VERIFICAR: ... !]` ainda pendentes de revisão humana, agrupados por
 * seção do parecer (EMENTA / RELATÓRIO / FUNDAMENTOS / CONCLUSÃO).
 *
 * Quando o P2 (Sonnet) não consegue verificar uma norma, julgado ou valor
 * via banco curado + web_search, ele insere um marcador. Este painel torna
 * todos visíveis ao advogado revisor antes da exportação.
 */
export default function RevisaoMarkersPanel({ tiptap }: Props) {
  const marcadores = useMemo<MarcadorRevisao[]>(
    () => extrairMarcadoresRevisao(tiptap),
    [tiptap],
  )

  if (marcadores.length === 0) {
    return (
      <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
        <h3
          className="text-sm font-medium uppercase tracking-widest mb-2"
          style={{ color: '#A69B8D' }}
        >
          Revisão Humana
        </h3>
        <p className="text-sm" style={{ color: '#A69B8D' }}>
          Nenhum ponto pendente.
        </p>
      </div>
    )
  }

  // Agrupa por seção para leitura mais natural
  const porSecao = new Map<string, MarcadorRevisao[]>()
  for (const m of marcadores) {
    const chave = m.secao ?? '—'
    const lista = porSecao.get(chave) ?? []
    lista.push(m)
    porSecao.set(chave, lista)
  }

  return (
    <div className="p-3" style={{ borderBottom: '1px solid #E0D9CE' }}>
      <h3
        className="text-sm font-medium uppercase tracking-widest mb-2 flex items-center gap-2"
        style={{ color: '#A69B8D' }}
      >
        <span>Revisão Humana</span>
        <span
          className="px-1.5 rounded-full text-xs font-bold"
          style={{ background: '#C00000', color: '#fff' }}
          title={`${marcadores.length} ponto(s) pendente(s)`}
        >
          {marcadores.length}
        </span>
      </h3>
      <p className="text-xs mb-2" style={{ color: '#6B6860' }}>
        Já destacados em <span style={{ color: '#C00000', fontWeight: 700 }}>vermelho/negrito</span>{' '}
        no editor — passe o mouse sobre o trecho para ver o que verificar.
      </p>
      <p className="text-xs mb-3" style={{ color: '#A69B8D' }}>
        Para resolver: confirme a informação e edite o texto removendo os colchetes.
      </p>
      <ul className="space-y-2">
        {[...porSecao.entries()].map(([secao, lista]) => (
          <li key={secao}>
            <div
              className="text-xs font-semibold uppercase tracking-wider mb-1"
              style={{ color: '#6B6860' }}
            >
              {secao}
            </div>
            <ul className="space-y-1.5">
              {lista.map((m) => (
                <li
                  key={m.indice}
                  className="text-xs px-2 py-1.5 rounded"
                  style={{
                    background: '#FBF7EE',
                    borderLeft: '3px solid #C00000',
                  }}
                  title={m.textoCompleto}
                >
                  <span
                    className="font-mono mr-1"
                    style={{ color: '#C00000', fontWeight: 700 }}
                  >
                    {m.tipo === 'revisar' ? '[REVISAR]' : '[VERIFICAR]'}
                  </span>
                  <span style={{ color: '#3B3833' }}>{m.conteudo}</span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  )
}
