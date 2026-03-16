import type { ParecerRequestDetail, ParecerVersion } from './parecer'

export interface EditorState {
  parecer: ParecerRequestDetail | null
  activeVersion: ParecerVersion | null
  isDirty: boolean
  isSaving: boolean
  showSplitView: boolean
  showReturnModal: boolean
}

export interface SavePayload {
  content_html: string
  version_id: string
}

export interface ReturnToAIPayload {
  parecer_id: string
  instructions: string
}

export interface ExportFormat {
  type: 'docx' | 'pdf'
}

export interface ApprovePayload {
  parecer_id: string
  send_email: boolean
}

export interface EditorAction {
  label: string
  onClick: () => void
  variant: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  loading?: boolean
}

export interface ReviewFlowStep {
  label: string
  status: 'done' | 'current' | 'pending'
  date?: string
}
