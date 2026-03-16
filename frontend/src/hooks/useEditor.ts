import { useCallback, useEffect, useRef, useState } from 'react'
import { useEditor as useTipTapEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Placeholder from '@tiptap/extension-placeholder'
import Typography from '@tiptap/extension-typography'
import { useQueryClient } from '@tanstack/react-query'
import CitacaoLegal from '../components/editor/extensions/CitacaoLegal'
import Ementa from '../components/editor/extensions/Ementa'
import AIContent from '../components/editor/extensions/AIContent'
import { saveVersion, returnToAI, approveParecer, exportParecer, requestCorrection } from '../services/editorApi'
import type { ParecerRequestDetail, ParecerVersion } from '../types/parecer'

export function useEditorInstance(parecer: ParecerRequestDetail | null) {
  const [activeVersion, setActiveVersion] = useState<ParecerVersion | null>(null)
  const [isDirty, setIsDirty] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [showSplitView, setShowSplitView] = useState(false)
  const [showReturnModal, setShowReturnModal] = useState(false)
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const queryClient = useQueryClient()

  // Pick latest version on parecer load
  useEffect(() => {
    if (parecer?.versions?.length) {
      const sorted = [...parecer.versions].sort(
        (a, b) => b.version_number - a.version_number
      )
      setActiveVersion(sorted[0])
    }
  }, [parecer])

  const editor = useTipTapEditor({
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      Underline,
      Placeholder.configure({ placeholder: 'Comece a digitar a minuta...' }),
      Typography,
      CitacaoLegal,
      Ementa,
      AIContent,
    ],
    content: activeVersion?.content_html || '',
    onUpdate: () => {
      setIsDirty(true)
    },
    editorProps: {
      attributes: {
        class:
          'prose prose-sm max-w-none focus:outline-none min-h-[500px] px-8 py-6',
      },
    },
  })

  // Sync content when activeVersion changes
  useEffect(() => {
    if (editor && activeVersion?.content_html != null) {
      const currentContent = editor.getHTML()
      if (currentContent !== activeVersion.content_html) {
        editor.commands.setContent(activeVersion.content_html)
        setIsDirty(false)
      }
    }
  }, [activeVersion, editor])

  // Auto-save debounce 2s
  useEffect(() => {
    if (!isDirty || !editor || !parecer || !activeVersion) return
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    saveTimerRef.current = setTimeout(async () => {
      setIsSaving(true)
      try {
        await saveVersion(parecer.id, activeVersion.id, editor.getHTML())
        setIsDirty(false)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
      } catch (err) {
        console.error('Auto-save failed:', err)
      } finally {
        setIsSaving(false)
      }
    }, 2000)
    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    }
  }, [isDirty, editor, parecer, activeVersion, queryClient])

  const handleSave = useCallback(async () => {
    if (!editor || !parecer || !activeVersion) return
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
    setIsSaving(true)
    try {
      await saveVersion(parecer.id, activeVersion.id, editor.getHTML())
      setIsDirty(false)
      queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
    } catch (err) {
      console.error('Save failed:', err)
    } finally {
      setIsSaving(false)
    }
  }, [editor, parecer, activeVersion, queryClient])

  const handleReturnToAI = useCallback(
    async (instructions: string) => {
      if (!parecer) return
      try {
        const newVersion = await returnToAI(parecer.id, instructions)
        setActiveVersion(newVersion)
        setShowReturnModal(false)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
      } catch (err) {
        console.error('Return to AI failed:', err)
      }
    },
    [parecer, queryClient]
  )

  const handleApprove = useCallback(
    async (sendEmail: boolean) => {
      if (!parecer) return
      await handleSave()
      try {
        await approveParecer(parecer.id, sendEmail)
        queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
      } catch (err) {
        console.error('Approve failed:', err)
      }
    },
    [parecer, handleSave, queryClient]
  )

  const handleExport = useCallback(
    async (format: 'docx' | 'pdf') => {
      if (!parecer) return
      try {
        const blob = await exportParecer(parecer.id, format)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${parecer.numero_parecer || 'parecer'}.${format}`
        a.click()
        URL.revokeObjectURL(url)
      } catch (err) {
        console.error('Export failed:', err)
      }
    },
    [parecer]
  )

  const handleRequestCorrection = useCallback(async () => {
    if (!parecer) return
    try {
      await requestCorrection(parecer.id)
      queryClient.invalidateQueries({ queryKey: ['parecer', parecer.id] })
    } catch (err) {
      console.error('Request correction failed:', err)
    }
  }, [parecer, queryClient])

  return {
    editor,
    activeVersion,
    setActiveVersion,
    isDirty,
    isSaving,
    showSplitView,
    setShowSplitView,
    showReturnModal,
    setShowReturnModal,
    handleSave,
    handleReturnToAI,
    handleApprove,
    handleExport,
    handleRequestCorrection,
  }
}
