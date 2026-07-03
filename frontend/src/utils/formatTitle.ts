/**
 * Formata o assunto de um parecer para exibição (SOMENTE display — não muta o dado).
 *
 * Os assuntos chegam em CAIXA ALTA do e-mail da prefeitura
 * (ex.: "SOLICITAÇÃO DE PARECER JURIDICO LOCAÇÃO SDTS"). Este helper converte
 * para Title Case pt-BR, preservando siglas e números.
 *
 * Regras:
 * - Só transforma quando a string é predominantemente MAIÚSCULA (evita mexer em
 *   título já digitado corretamente).
 * - Preposições/artigos curtos ficam minúsculos, exceto na 1ª palavra.
 * - Tokens que parecem sigla (sem vogal) ou que contêm dígito são preservados
 *   como no original (ex.: "SDTS", "TR", "nº 3103005/2025").
 */

// Palavras que ficam minúsculas no meio do título.
const LOWER_WORDS = new Set([
  'de', 'da', 'do', 'das', 'dos', 'e', 'a', 'o', 'as', 'os',
  'para', 'pra', 'com', 'em', 'no', 'na', 'nos', 'nas',
  'ao', 'aos', 'à', 'às', 'por', 'sob', 'sobre', 'entre', 'até', 'ou',
])

const VOWELS = /[aeiouáàâãéèêíïóôõöúùû]/i
const HAS_DIGIT = /\d/
const HAS_LETTER = /[a-záàâãéèêíïóôõöúùûç]/i

/** Fração de letras que estão em maiúscula (ignora não-letras). */
function upperRatio(s: string): number {
  const letters = s.replace(/[^a-záàâãéèêíïóôõöúùûçA-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÙÛÇ]/g, '')
  if (!letters) return 0
  let upper = 0
  for (const ch of letters) if (ch === ch.toUpperCase() && ch !== ch.toLowerCase()) upper++
  return upper / letters.length
}

/** Um token é preservado como está (sigla/número) se contém dígito ou não tem vogal. */
function isPreserved(token: string): boolean {
  const core = token.replace(/[^\p{L}\p{N}]/gu, '')
  if (!core) return false
  if (HAS_DIGIT.test(core)) return true
  // sem vogal alguma → provável sigla (SDTS, TR, PMDB, RPPS)
  if (HAS_LETTER.test(core) && !VOWELS.test(core)) return true
  return false
}

function capitalizeWord(word: string): string {
  // capitaliza a 1ª letra, mantém o resto minúsculo (o token já vem lowercased)
  return word.replace(/\p{L}/u, (c) => c.toUpperCase())
}

export function formatParecerTitle(subject: string | null | undefined): string {
  if (!subject) return ''
  const trimmed = subject.trim()
  if (!trimmed) return ''
  // Só normaliza se for predominantemente maiúscula.
  if (upperRatio(trimmed) < 0.6) return trimmed

  const tokens = trimmed.split(/(\s+)/) // mantém os separadores de espaço
  let wordIndex = 0
  return tokens
    .map((tok) => {
      if (/^\s+$/.test(tok) || tok === '') return tok
      const idx = wordIndex++
      if (isPreserved(tok)) return tok // sigla/número → como no original
      const lower = tok.toLowerCase()
      if (idx > 0 && LOWER_WORDS.has(lower)) return lower
      return capitalizeWord(lower)
    })
    .join('')
}
