const AUTHOR_COLORS = [
  { bg: '#142038', border: '#14203860', text: '#FAF8F5' },
  { bg: '#5B7553', border: '#5B755360', text: '#FAF8F5' },
  { bg: '#8B2332', border: '#8B233260', text: '#FAF8F5' },
  { bg: '#7A5C2E', border: '#7A5C2E60', text: '#FAF8F5' },
  { bg: '#3D5A80', border: '#3D5A8060', text: '#FAF8F5' },
  { bg: '#6B4C82', border: '#6B4C8260', text: '#FAF8F5' },
]

const IA_COLOR = { bg: '#C9A94E22', border: '#C9A94E55', text: '#7A5C2E' }

export function colorForInitials(initials: string) {
  if (!initials || initials === 'IA') return IA_COLOR
  let hash = 0
  for (let i = 0; i < initials.length; i++) hash = (hash * 31 + initials.charCodeAt(i)) & 0xffff
  return AUTHOR_COLORS[hash % AUTHOR_COLORS.length]
}

export function getInitials(name: string | null | undefined): string {
  if (!name) return 'IA'
  return name.split(' ').filter(Boolean).slice(0, 2).map(w => w[0].toUpperCase()).join('')
}

const HIGHLIGHT_PALETTE = [
  'rgba(20, 32, 56, 0.18)',
  'rgba(91, 117, 83, 0.22)',
  'rgba(139, 35, 50, 0.18)',
  'rgba(122, 92, 46, 0.22)',
  'rgba(61, 90, 128, 0.20)',
  'rgba(107, 76, 130, 0.20)',
]

const IA_HIGHLIGHT = 'rgba(201, 169, 78, 0.30)'

export function highlightColorForInitials(initials: string): string {
  if (!initials || initials === 'IA') return IA_HIGHLIGHT
  let hash = 0
  for (let i = 0; i < initials.length; i++) hash = (hash * 31 + initials.charCodeAt(i)) & 0xffff
  return HIGHLIGHT_PALETTE[hash % HIGHLIGHT_PALETTE.length]
}
