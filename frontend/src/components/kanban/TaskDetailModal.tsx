import { useState, useMemo } from 'react'
import {
  X, Calendar, Clock, User, Tag, CheckSquare, Square,
  MessageSquare, History, Trash2, Save,
} from 'lucide-react'
import {
  useUpdateTask, useDeleteTask, useTaskHistory,
  useTaskComments, useCreateComment, useUsers,
} from '../../hooks/useTasks'
import type { Task, Column, TaskCategory, TaskPriority, ChecklistItem, UserMinimal } from '../../types/task'

interface TaskDetailModalProps {
  task: Task
  columns: Column[]
  onClose: () => void
}

const inputStyle: React.CSSProperties = {
  background: '#FAF8F5',
  border: '1.5px solid #E0D9CE',
  color: '#0A1120',
}

const PRIORITY_LABELS: Record<string, string> = { high: 'Alta', medium: 'Média', low: 'Baixa' }
const PRIORITY_COLORS: Record<string, string> = { high: '#8B2332', medium: '#C9A94E', low: '#5B7553' }
const CATEGORY_LABELS: Record<string, string> = {
  judicial: 'Judicial', administrativa: 'Administrativa', parecer: 'Parecer',
  publicacao_dje: 'Publicação DJE', prazo: 'Prazo',
}

type TabId = 'details' | 'comments' | 'history'

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function toInputDate(iso?: string | null) {
  if (!iso) return ''
  return new Date(iso).toISOString().split('T')[0]
}

function getUserName(userId: string | undefined, users: UserMinimal[] | undefined): string {
  if (!userId || !users) return ''
  return users.find(u => u.id === userId)?.name ?? ''
}

export default function TaskDetailModal({ task, columns, onClose }: TaskDetailModalProps) {
  const updateTask = useUpdateTask()
  const deleteTaskMut = useDeleteTask()
  const { data: history } = useTaskHistory(task.id)
  const { data: comments } = useTaskComments(task.id)
  const createComment = useCreateComment()
  const { data: users } = useUsers()

  const [activeTab, setActiveTab] = useState<TabId>('details')
  const [editing, setEditing] = useState(false)
  const [commentText, setCommentText] = useState('')

  // Editable fields
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description ?? '')
  const [category, setCategory] = useState<TaskCategory | ''>(task.category ?? '')
  const [priority, setPriority] = useState<TaskPriority>(task.priority)
  const [assignedTo, setAssignedTo] = useState(task.assigned_to ?? '')
  const [startDate, setStartDate] = useState(toInputDate(task.start_date))
  const [dueDate, setDueDate] = useState(toInputDate(task.due_date))
  const [estimatedHours, setEstimatedHours] = useState(task.estimated_hours?.toString() ?? '')
  const [tags, setTags] = useState((task.tags ?? []).join(', '))
  const [checklist, setChecklist] = useState<ChecklistItem[]>(task.checklist ?? [])
  const [newCheckItem, setNewCheckItem] = useState('')

  const isOverdue = task.due_date && new Date(task.due_date) < new Date()

  const checklistProgress = useMemo(() => {
    if (!checklist.length) return null
    const done = checklist.filter(i => i.done).length
    return { done, total: checklist.length, pct: Math.round((done / checklist.length) * 100) }
  }, [checklist])

  const columnName = columns.find(c => c.id === task.column_id)?.name ?? ''

  const handleSave = async () => {
    await updateTask.mutateAsync({
      taskId: task.id,
      payload: {
        title: title.trim(),
        description: description.trim() || undefined,
        category: category || undefined,
        priority,
        assigned_to: assignedTo || null,
        start_date: startDate ? new Date(startDate).toISOString() : null,
        due_date: dueDate ? new Date(dueDate).toISOString() : null,
        estimated_hours: estimatedHours ? parseFloat(estimatedHours) : null,
        tags: tags.trim() ? tags.split(',').map(t => t.trim()).filter(Boolean) : [],
        checklist,
      },
    })
    setEditing(false)
  }

  const handleDelete = async () => {
    if (!confirm('Tem certeza que deseja excluir esta tarefa?')) return
    await deleteTaskMut.mutateAsync(task.id)
    onClose()
  }

  const toggleCheckItem = async (index: number) => {
    const updated = checklist.map((item, i) =>
      i === index ? { ...item, done: !item.done } : item
    )
    setChecklist(updated)
    await updateTask.mutateAsync({
      taskId: task.id,
      payload: { checklist: updated },
    })
  }

  const addCheckItem = () => {
    if (!newCheckItem.trim()) return
    setChecklist([...checklist, { text: newCheckItem.trim(), done: false }])
    setNewCheckItem('')
  }

  const removeCheckItem = (index: number) => {
    setChecklist(checklist.filter((_, i) => i !== index))
  }

  const handleAddComment = async () => {
    if (!commentText.trim()) return
    await createComment.mutateAsync({ taskId: task.id, content: commentText.trim() })
    setCommentText('')
  }

  const tabs: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'details', label: 'Detalhes', icon: <CheckSquare className="w-4 h-4" /> },
    { id: 'comments', label: `Comentários${comments?.length ? ` (${comments.length})` : ''}`, icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'history', label: 'Histórico', icon: <History className="w-4 h-4" /> },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col" style={{ background: '#FAF8F5', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>

        {/* Header */}
        <div className="flex items-start justify-between px-5 py-4 shrink-0" style={{ borderBottom: '1px solid #EDE8DF' }}>
          <div className="flex-1 min-w-0 mr-3">
            {editing ? (
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-lg px-2 py-1 text-base font-medium focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              />
            ) : (
              <h2 className="text-base font-medium leading-tight" style={{ color: '#0A1120' }}>{task.title}</h2>
            )}
            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
              <span className="text-xs px-2 py-0.5 rounded-lg font-medium" style={{ background: `${PRIORITY_COLORS[task.priority]}18`, color: PRIORITY_COLORS[task.priority] }}>
                {PRIORITY_LABELS[task.priority]}
              </span>
              {task.category && (
                <span className="text-xs px-2 py-0.5 rounded-lg font-medium" style={{ background: '#14203818', color: '#142038' }}>
                  {CATEGORY_LABELS[task.category]}
                </span>
              )}
              <span className="text-xs" style={{ color: '#A69B8D' }}>{columnName}</span>
              {isOverdue && (
                <span className="text-xs font-medium px-2 py-0.5 rounded-lg" style={{ background: '#8B233218', color: '#8B2332' }}>
                  Vencida
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            {editing ? (
              <button onClick={handleSave} disabled={updateTask.isPending}
                className="p-1.5 rounded-lg transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
                style={{ color: '#5B7553' }} title="Salvar">
                <Save className="w-5 h-5" />
              </button>
            ) : (
              <button onClick={() => setEditing(true)}
                className="px-3 py-1 rounded-lg text-xs font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
                style={{ background: '#142038', color: '#FAF8F5' }}>
                Editar
              </button>
            )}
            <button onClick={handleDelete}
              className="p-1.5 rounded-lg transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
              style={{ color: '#8B2332' }} title="Excluir">
              <Trash2 className="w-4 h-4" />
            </button>
            <button onClick={onClose} className="p-1 rounded-lg transition-all duration-150 hover:brightness-[0.97] cursor-pointer" style={{ color: '#A69B8D' }}>
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-0 px-5 shrink-0" style={{ borderBottom: '1px solid #EDE8DF' }}>
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium transition-all duration-150 cursor-pointer relative"
              style={{ color: activeTab === tab.id ? '#142038' : '#A69B8D' }}>
              {tab.icon}
              {tab.label}
              {activeTab === tab.id && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5" style={{ background: '#142038' }} />
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-y-auto p-5">

          {/* DETAILS TAB */}
          {activeTab === 'details' && (
            <div className="space-y-5">
              {/* Info grid */}
              <div className="grid grid-cols-2 gap-4">
                {/* Assignee */}
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium mb-1" style={{ color: '#A69B8D' }}>
                    <User className="w-3.5 h-3.5" /> Responsável
                  </label>
                  {editing ? (
                    <select value={assignedTo} onChange={(e) => setAssignedTo(e.target.value)}
                      className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}>
                      <option value="">Sem responsável</option>
                      {users?.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
                    </select>
                  ) : (
                    <p className="text-sm" style={{ color: '#0A1120' }}>
                      {getUserName(task.assigned_to, users) || <span style={{ color: '#A69B8D' }}>—</span>}
                    </p>
                  )}
                </div>

                {/* Priority */}
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium mb-1" style={{ color: '#A69B8D' }}>
                    Prioridade
                  </label>
                  {editing ? (
                    <select value={priority} onChange={(e) => setPriority(e.target.value as TaskPriority)}
                      className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}>
                      <option value="high">Alta</option>
                      <option value="medium">Média</option>
                      <option value="low">Baixa</option>
                    </select>
                  ) : (
                    <span className="text-sm font-medium" style={{ color: PRIORITY_COLORS[task.priority] }}>
                      {PRIORITY_LABELS[task.priority]}
                    </span>
                  )}
                </div>

                {/* Start date */}
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium mb-1" style={{ color: '#A69B8D' }}>
                    <Calendar className="w-3.5 h-3.5" /> Data Início
                  </label>
                  {editing ? (
                    <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)}
                      className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties} />
                  ) : (
                    <p className="text-sm" style={{ color: '#0A1120' }}>
                      {task.start_date ? formatDate(task.start_date) : <span style={{ color: '#A69B8D' }}>—</span>}
                    </p>
                  )}
                </div>

                {/* Due date */}
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium mb-1" style={{ color: '#A69B8D' }}>
                    <Calendar className="w-3.5 h-3.5" /> Data Fim
                  </label>
                  {editing ? (
                    <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)}
                      className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties} />
                  ) : (
                    <p className="text-sm" style={{ color: isOverdue ? '#8B2332' : '#0A1120' }}>
                      {task.due_date ? formatDate(task.due_date) : <span style={{ color: '#A69B8D' }}>—</span>}
                    </p>
                  )}
                </div>

                {/* Estimated hours */}
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium mb-1" style={{ color: '#A69B8D' }}>
                    <Clock className="w-3.5 h-3.5" /> Horas Estimadas
                  </label>
                  {editing ? (
                    <input type="number" min="0" step="0.5" value={estimatedHours}
                      onChange={(e) => setEstimatedHours(e.target.value)}
                      className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties} />
                  ) : (
                    <p className="text-sm" style={{ color: '#0A1120' }}>
                      {task.estimated_hours ? `${task.estimated_hours}h` : <span style={{ color: '#A69B8D' }}>—</span>}
                    </p>
                  )}
                </div>

                {/* Category */}
                <div>
                  <label className="flex items-center gap-1.5 text-xs font-medium mb-1" style={{ color: '#A69B8D' }}>
                    Categoria
                  </label>
                  {editing ? (
                    <select value={category} onChange={(e) => setCategory(e.target.value as TaskCategory | '')}
                      className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                      style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}>
                      <option value="">Sem categoria</option>
                      <option value="judicial">Judicial</option>
                      <option value="administrativa">Administrativa</option>
                      <option value="parecer">Parecer</option>
                      <option value="publicacao_dje">Publicação DJE</option>
                      <option value="prazo">Prazo</option>
                    </select>
                  ) : (
                    <p className="text-sm" style={{ color: '#0A1120' }}>
                      {task.category ? CATEGORY_LABELS[task.category] : <span style={{ color: '#A69B8D' }}>—</span>}
                    </p>
                  )}
                </div>
              </div>

              {/* Tags */}
              <div>
                <label className="flex items-center gap-1.5 text-xs font-medium mb-1.5" style={{ color: '#A69B8D' }}>
                  <Tag className="w-3.5 h-3.5" /> Tags
                </label>
                {editing ? (
                  <input type="text" value={tags} onChange={(e) => setTags(e.target.value)}
                    className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                    style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                    placeholder="Separadas por vírgula" />
                ) : (
                  <div className="flex gap-1.5 flex-wrap">
                    {(task.tags ?? []).length > 0 ? (
                      task.tags!.map((tag, i) => (
                        <span key={i} className="text-xs px-2 py-0.5 rounded-lg font-medium"
                          style={{ background: '#C9A94E18', color: '#8B7A3A' }}>
                          {tag}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm" style={{ color: '#A69B8D' }}>—</span>
                    )}
                  </div>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="text-xs font-medium mb-1.5 block" style={{ color: '#A69B8D' }}>Descrição</label>
                {editing ? (
                  <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4}
                    className="w-full rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 resize-none"
                    style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                    placeholder="Detalhes da tarefa..." />
                ) : (
                  <p className="text-sm whitespace-pre-wrap" style={{ color: task.description ? '#0A1120' : '#A69B8D' }}>
                    {task.description || '—'}
                  </p>
                )}
              </div>

              {/* Checklist */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="flex items-center gap-1.5 text-xs font-medium" style={{ color: '#A69B8D' }}>
                    <CheckSquare className="w-3.5 h-3.5" /> Checklist
                    {checklistProgress && (
                      <span className="ml-1">({checklistProgress.done}/{checklistProgress.total})</span>
                    )}
                  </label>
                </div>
                {checklistProgress && (
                  <div className="w-full h-1.5 rounded-full mb-3" style={{ background: '#E0D9CE' }}>
                    <div className="h-full rounded-full transition-all duration-300"
                      style={{ width: `${checklistProgress.pct}%`, background: checklistProgress.pct === 100 ? '#5B7553' : '#C9A94E' }} />
                  </div>
                )}
                <div className="space-y-1.5">
                  {checklist.map((item, i) => (
                    <div key={i} className="flex items-center gap-2 group">
                      <button onClick={() => toggleCheckItem(i)} className="shrink-0 cursor-pointer" style={{ color: item.done ? '#5B7553' : '#A69B8D' }}>
                        {item.done ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4" />}
                      </button>
                      <span className="text-sm flex-1" style={{ color: item.done ? '#A69B8D' : '#0A1120', textDecoration: item.done ? 'line-through' : 'none' }}>
                        {item.text}
                      </span>
                      {editing && (
                        <button onClick={() => removeCheckItem(i)} className="opacity-0 group-hover:opacity-100 cursor-pointer" style={{ color: '#8B2332' }}>
                          <X className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
                {/* Add checklist item (always visible) */}
                <div className="flex items-center gap-2 mt-2">
                  <input type="text" value={newCheckItem} onChange={(e) => setNewCheckItem(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCheckItem())}
                    className="flex-1 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2"
                    style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                    placeholder="Novo item..." />
                  <button onClick={addCheckItem}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer"
                    style={{ background: '#142038', color: '#FAF8F5' }}>
                    Adicionar
                  </button>
                </div>
              </div>

              {/* Timestamps */}
              <div className="flex gap-6 text-xs pt-2" style={{ color: '#A69B8D' }}>
                <span>Criada: {formatDateTime(task.created_at)}</span>
                <span>Atualizada: {formatDateTime(task.updated_at)}</span>
              </div>
            </div>
          )}

          {/* COMMENTS TAB */}
          {activeTab === 'comments' && (
            <div className="space-y-4">
              <div className="flex gap-2">
                <input type="text" value={commentText} onChange={(e) => setCommentText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddComment()}
                  className="flex-1 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2"
                  style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                  placeholder="Escreva um comentário..." />
                <button onClick={handleAddComment} disabled={createComment.isPending || !commentText.trim()}
                  className="px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50"
                  style={{ background: '#142038', color: '#FAF8F5' }}>
                  Enviar
                </button>
              </div>

              {!comments?.length && (
                <p className="text-sm text-center py-8" style={{ color: '#A69B8D' }}>Nenhum comentário ainda.</p>
              )}

              {comments?.map(c => (
                <div key={c.id} className="rounded-xl p-3" style={{ background: '#FAF8F5', border: '1px solid #EDE8DF' }}>
                  <div className="flex items-center gap-2 mb-1.5">
                    <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ background: '#14203818' }}>
                      <User className="w-3 h-3" style={{ color: '#142038' }} />
                    </div>
                    <span className="text-sm font-medium" style={{ color: '#0A1120' }}>
                      {getUserName(c.user_id, users) || 'Usuário'}
                    </span>
                    <span className="text-xs" style={{ color: '#A69B8D' }}>{formatDateTime(c.created_at)}</span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap" style={{ color: '#0A1120' }}>{c.content}</p>
                </div>
              ))}
            </div>
          )}

          {/* HISTORY TAB */}
          {activeTab === 'history' && (
            <div className="space-y-0">
              {!history?.length && (
                <p className="text-sm text-center py-8" style={{ color: '#A69B8D' }}>Nenhum registro.</p>
              )}
              {history?.map((h, i) => (
                <div key={h.id} className="flex gap-3 py-3" style={i < (history?.length ?? 0) - 1 ? { borderBottom: '1px solid #EDE8DF' } : {}}>
                  <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5" style={{ background: '#C9A94E18' }}>
                    <History className="w-3 h-3" style={{ color: '#C9A94E' }} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm" style={{ color: '#0A1120' }}>{h.notes}</p>
                    <div className="flex gap-3 mt-0.5">
                      <span className="text-xs" style={{ color: '#A69B8D' }}>{formatDateTime(h.created_at)}</span>
                      {h.changed_by && (
                        <span className="text-xs" style={{ color: '#A69B8D' }}>
                          por {getUserName(h.changed_by, users) || 'Sistema'}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
