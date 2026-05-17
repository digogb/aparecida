import { describe, it, expect } from 'vitest'
import { contarMarcadoresRevisao, extrairMarcadoresRevisao } from './revisaoMarkers'

describe('contarMarcadoresRevisao', () => {
  it('retorna 0 para conteúdo vazio ou inválido', () => {
    expect(contarMarcadoresRevisao(null)).toBe(0)
    expect(contarMarcadoresRevisao(undefined)).toBe(0)
    expect(contarMarcadoresRevisao('texto')).toBe(0)
    expect(contarMarcadoresRevisao({})).toBe(0)
    expect(contarMarcadoresRevisao({ type: 'doc', content: [] })).toBe(0)
  })

  it('conta marcador [REVISAR — ...] em parágrafo simples', () => {
    const tiptap = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Conforme [REVISAR — art. 53 da Lei] o caso.' },
          ],
        },
      ],
    }
    expect(contarMarcadoresRevisao(tiptap)).toBe(1)
  })

  it('conta marcador [!VERIFICAR: ... !] em parágrafo simples', () => {
    const tiptap = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'A norma é [!VERIFICAR: LC 1.234/2018 !] local.' },
          ],
        },
      ],
    }
    expect(contarMarcadoresRevisao(tiptap)).toBe(1)
  })

  it('soma marcadores de tipos diferentes em múltiplos nós', () => {
    const tiptap = {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [{ type: 'text', text: '[REVISAR — A]' }],
        },
        {
          type: 'heading',
          attrs: { level: 2 },
          content: [{ type: 'text', text: 'EMENTA' }],
        },
        {
          type: 'paragraph',
          content: [
            { type: 'text', text: 'Foo ' },
            { type: 'text', text: '[!VERIFICAR: B !]' },
            { type: 'text', text: ' bar [REVISAR — C].' },
          ],
        },
      ],
    }
    expect(contarMarcadoresRevisao(tiptap)).toBe(3)
  })

  it('tolera variações de hífen no [REVISAR — ...]', () => {
    const tiptap = {
      type: 'doc',
      content: [
        { type: 'paragraph', content: [{ type: 'text', text: '[REVISAR - hífen]' }] },
        { type: 'paragraph', content: [{ type: 'text', text: '[REVISAR – en-dash]' }] },
        { type: 'paragraph', content: [{ type: 'text', text: '[REVISAR — em-dash]' }] },
      ],
    }
    expect(contarMarcadoresRevisao(tiptap)).toBe(3)
  })
})

describe('extrairMarcadoresRevisao', () => {
  const tiptap = {
    type: 'doc',
    content: [
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'EMENTA' }],
      },
      {
        type: 'paragraph',
        content: [{ type: 'text', text: '[REVISAR — conferir art. 53]' }],
      },
      {
        type: 'heading',
        attrs: { level: 2 },
        content: [{ type: 'text', text: 'II — FUNDAMENTOS' }],
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: 'Conforme [!VERIFICAR: LC municipal !] a regra.' },
        ],
      },
      {
        type: 'paragraph',
        content: [
          { type: 'text', text: '[REVISAR — Tema 1226 STF] e [REVISAR — valor]' },
        ],
      },
    ],
  }

  it('agrupa por seção e identifica tipo de cada marcador', () => {
    const marcadores = extrairMarcadoresRevisao(tiptap)
    expect(marcadores).toHaveLength(4)
    expect(marcadores[0]).toMatchObject({
      tipo: 'revisar',
      conteudo: 'conferir art. 53',
      secao: 'EMENTA',
      indice: 0,
    })
    expect(marcadores[1]).toMatchObject({
      tipo: 'verificar',
      conteudo: 'LC municipal',
      secao: 'FUNDAMENTOS',
      indice: 1,
    })
    expect(marcadores[2].secao).toBe('FUNDAMENTOS')
    expect(marcadores[3].secao).toBe('FUNDAMENTOS')
  })

  it('retorna lista vazia para conteúdo nulo/sem markers', () => {
    expect(extrairMarcadoresRevisao(null)).toEqual([])
    expect(extrairMarcadoresRevisao(undefined)).toEqual([])
    expect(
      extrairMarcadoresRevisao({
        type: 'doc',
        content: [{ type: 'paragraph', content: [{ type: 'text', text: 'limpo' }] }],
      }),
    ).toEqual([])
  })

  it('detecta seção sem prefixo de numeral romano', () => {
    const result = extrairMarcadoresRevisao({
      type: 'doc',
      content: [
        { type: 'heading', attrs: { level: 2 }, content: [{ type: 'text', text: 'CONCLUSÃO' }] },
        { type: 'paragraph', content: [{ type: 'text', text: '[REVISAR — A]' }] },
      ],
    })
    expect(result[0].secao).toBe('CONCLUSÃO')
  })
})
