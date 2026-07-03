import { describe, it, expect } from 'vitest'
import { formatParecerTitle } from './formatTitle'

describe('formatParecerTitle', () => {
  it('converte caixa alta preservando sigla', () => {
    expect(formatParecerTitle('SOLICITAÇÃO DE PARECER JURIDICO LOCAÇÃO SDTS'))
      .toBe('Solicitação de Parecer Juridico Locação SDTS')
  })

  it('mantém preposições minúsculas no meio, mas capitaliza a primeira palavra', () => {
    expect(formatParecerTitle('PRORROGAÇÃO DO CONTRATO')).toBe('Prorrogação do Contrato')
  })

  it('preserva tokens com número', () => {
    expect(formatParecerTitle('CONTRATO Nº 3103005/2025'))
      .toBe('Contrato Nº 3103005/2025')
  })

  it('não altera título já formatado', () => {
    const s = 'Consulta sobre licitação'
    expect(formatParecerTitle(s)).toBe(s)
  })

  it('lida com vazio/nulo', () => {
    expect(formatParecerTitle('')).toBe('')
    expect(formatParecerTitle(null)).toBe('')
    expect(formatParecerTitle(undefined)).toBe('')
  })
})
