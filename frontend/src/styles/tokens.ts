/**
 * Design System — Pearson Hardman
 *
 * Paleta semântica com 4 cores funcionais + 1 cor de identidade.
 * Projetado para usuários com baixo conforto tecnológico:
 * fontes grandes, poucos tons, hierarquia visual clara.
 */

/* ── Cores ────────────────────────────────────────── */

export const colors = {
  /** Cor de identidade — logo, links, CTAs, item ativo sidebar */
  brand: '#C9A94E',

  /** Superfícies */
  surface: {
    page:    '#F5F0E8',   // fundo principal das páginas
    card:    '#F5F0E8',   // fundo de cards e listas
    topbar:  '#EDE8DF',   // barra superior
    sidebar: '#142038',   // navegação lateral (base)
    sidebarGradient: 'linear-gradient(180deg, #0A1020 0%, #142038 60%, #1a2847 100%)',
  },

  /** Bordas e separadores */
  border: {
    card:    '#E0D9CE',   // borda de cards (1.5px)
    divider: '#EDE8DF',   // separador entre itens de lista (1px)
  },

  /** Textos */
  text: {
    primary:   '#0A1120', // títulos e conteúdo principal
    heading:   '#142038', // headings de destaque (h1)
    secondary: '#A69B8D', // labels, subtítulos, datas
    muted:     '#6B6860', // labels dentro de cards
    sidebar:   '#8A9BB0', // itens inativos da sidebar
  },

  /** Semânticas — cada cor tem um significado claro */
  semantic: {
    attention: '#C9A94E',  // pendentes, aguardando ação (âmbar)
    urgency:   '#8B2332',  // urgente, atrasado, devolvido (bordô)
    success:   '#5B7553',  // concluído, aprovado (oliva)
    neutral:   '#6B6860',  // informativo, sem ação necessária (cinza quente)
    info:      '#A69B8D',  // classificado, gerado, em revisão (cinza claro)
  },

  /** Status de pareceres — mapeamento direto */
  status: {
    pendente:     '#C9A94E',
    classificado: '#A69B8D',
    gerado:       '#A69B8D',
    em_correcao:  '#D97706',
    em_revisao:   '#A69B8D',
    devolvido:    '#8B2332',
    aprovado:     '#5B7553',
    enviado:      '#8C8A82',
  },
} as const

/* ── Tipografia ───────────────────────────────────── */

export const typography = {
  /** Fontes */
  family: {
    display: "'Fraunces', serif",   // headings, números grandes
    body:    "'Outfit', sans-serif", // corpo, labels, botões
  },

  /** Escala de tamanhos (mínimo 14px para acessibilidade) */
  size: {
    xs:      '12px',  // badges de status
    sm:      '14px',  // labels de seção, subtítulos
    base:    '16px',  // corpo de texto, itens de lista
    lg:      '18px',  // não usado frequentemente
    heading: '32px',  // saudação / título de página
    metric:  '38px',  // números dos cards de métrica
  },

  /** Pesos */
  weight: {
    light:    300,
    regular:  400,  // heading principal, corpo
    medium:   500,  // números de métricas, labels de card
    semibold: 600,  // badges, labels de seção
  },

  /** Tracking */
  tracking: {
    tight:   '-0.03em', // números grandes
    normal:  '-0.02em', // headings
    wide:    '0.05em',  // labels uppercase
  },
} as const

/* ── Espaçamento ──────────────────────────────────── */

export const spacing = {
  page: {
    x: '24px',  // px-6
    y: '32px',  // py-8
  },
  section: '32px',   // gap entre seções (space-y-8)
  card: {
    px: '20px',      // px-5
    py: '16px',      // py-4
  },
  listItem: {
    px: '20px',      // px-5
    py: '14px',       // py-3.5
  },
  gap: {
    cards: '12px',   // gap-3 entre cards
    grid:  '24px',   // gap-6 entre colunas
    list:  '8px',    // gap-2 entre alertas
  },
} as const

/* ── Bordas e raios ───────────────────────────────── */

export const borders = {
  card:    '1.5px solid #E0D9CE',
  divider: '1px solid #EDE8DF',
  radius: {
    card:  '12px',  // rounded-xl
    badge: '8px',   // rounded-lg
    sm:    '6px',   // rounded-md
  },
  /** Borda lateral de alertas */
  alertLeft: (color: string) => `4px solid ${color}`,
  /** Barra superior de cards de métrica */
  accentBar: (color: string) => ({ height: '4px', background: color }),
} as const

/* ── Interações ───────────────────────────────────── */

export const interactions = {
  /** Hover em cards e listas */
  hover: 'hover:brightness-[0.97]',
  /** Transição padrão */
  transition: 'transition-all duration-150',
  /** Press em botões */
  active: 'active:scale-[0.98]',
  /** Cursor para itens clicáveis */
  clickable: 'cursor-pointer',
} as const

/* ── Animações ────────────────────────────────────── */

export const animations = {
  /** Entrada de cards com contagem */
  count: 'animate-count',
  /** Fade-in com deslocamento vertical */
  fadeUp: 'animate-fade-up',
  /** Stagger delay entre items (ms) */
  staggerMs: 50,
} as const

/* ── Layout ───────────────────────────────────────── */

export const layout = {
  sidebar: {
    width: '224px',       // w-56
    background: 'linear-gradient(180deg, #0A1020 0%, #142038 60%, #1a2847 100%)',
    brandColor: '#C9A94E',
    activeItemBg: '#C9A94E18',
    activeItemText: '#C9A94E',
    inactiveText: '#8A9BB0',
    hoverBg: 'white/[0.06]',
  },
  topbar: {
    height: '48px',       // h-12
    background: '#EDE8DF',
    border: '1px solid #E0D9CE',
  },
} as const

/* ── Badges de status ─────────────────────────────── */

export function statusBadgeStyle(color: string) {
  return {
    color,
    background: `${color}18`,
  }
}

/* ── Skeleton loader ──────────────────────────────── */

export const skeleton = {
  background: '#EDE8DF',
  animation: 'animate-pulse',
} as const
