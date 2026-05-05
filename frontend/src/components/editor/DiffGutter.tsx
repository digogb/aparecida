import { useEffect, useRef, useState } from 'react'
import type { Editor } from '@tiptap/react'
import type { DiffAnnotation } from './extensions/DiffHighlight'
import { colorForInitials } from '../../utils/authorColors'

interface Props {
  editor: Editor | null
  annotation: DiffAnnotation
  scrollContainerRef: React.RefObject<HTMLDivElement>
}

interface Badge {
  top: number
  left: number
  /** Iniciais do parágrafo, separadas por ' / ' quando múltiplos autores */
  initials: string
}

export default function DiffGutter({ editor, annotation, scrollContainerRef }: Props) {
  const [badges, setBadges] = useState<Badge[]>([])
  const frameRef = useRef<number>(0)

  useEffect(() => {
    const compute = () => {
      if (!editor || !scrollContainerRef.current) { setBadges([]); return }

      const container = scrollContainerRef.current
      const containerRect = container.getBoundingClientRect()
      const editorEl = editor.view.dom as HTMLElement
      const editorRect = editorEl.getBoundingClientRect()

      const badgeLeft = editorRect.right - containerRect.left + 4

      const newBadges = annotation.paraFirstPositions
        .map((pos, i) => {
          try {
            const coords = editor.view.coordsAtPos(pos)
            const top = coords.top - containerRect.top + container.scrollTop
            const initials = annotation.paraInitials?.[i] ?? annotation.initials
            return { top, left: badgeLeft, initials }
          } catch {
            return null
          }
        })
        .filter((b): b is Badge => b !== null)

      setBadges(newBadges)
    }

    compute()

    const container = scrollContainerRef.current
    if (!container) return

    const schedule = () => {
      cancelAnimationFrame(frameRef.current)
      frameRef.current = requestAnimationFrame(compute)
    }

    container.addEventListener('scroll', schedule, { passive: true })
    const obs = new ResizeObserver(schedule)
    obs.observe(container)

    return () => {
      container.removeEventListener('scroll', schedule)
      obs.disconnect()
      cancelAnimationFrame(frameRef.current)
    }
  }, [editor, annotation, scrollContainerRef])

  if (!badges.length) return null

  return (
    <>
      {badges.map((badge, i) => {
        const list = badge.initials.split(' / ').filter(Boolean)
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: badge.top,
              left: badge.left,
              transform: 'translateY(2px)',
              display: 'flex',
              gap: 3,
              pointerEvents: 'none',
              zIndex: 10,
            }}
          >
            {list.map((ini, j) => {
              const color = colorForInitials(ini)
              return (
                <span
                  key={j}
                  style={{
                    padding: '2px 7px',
                    fontSize: '0.6rem',
                    fontWeight: 700,
                    borderRadius: '9999px',
                    background: color.bg,
                    color: color.text,
                    border: `1px solid ${color.border}`,
                    lineHeight: 1.5,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {ini}
                </span>
              )
            })}
          </div>
        )
      })}
    </>
  )
}
