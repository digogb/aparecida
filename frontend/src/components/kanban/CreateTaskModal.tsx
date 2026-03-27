import { useState } from 'react'
import { X } from 'lucide-react'
import { useCreateTask, useUsers } from '../../hooks/useTasks'
import type { Column, TaskCategory, TaskPriority } from '../../types/task'

interface CreateTaskModalProps {
  columns: Column[]
  defaultColumnId?: string
  onClose: () => void
}

const inputStyle: React.CSSProperties = {
  background: '#F5F0E8',
  border: '1.5px solid #E0D9CE',
  color: '#0A1120',
}

export default function CreateTaskModal({ columns, defaultColumnId, onClose }: CreateTaskModalProps) {
  const createTask = useCreateTask()
  const { data: users } = useUsers()

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [columnId, setColumnId] = useState(defaultColumnId ?? columns[0]?.id ?? '')
  const [category, setCategory] = useState<TaskCategory | ''>('')
  const [priority, setPriority] = useState<TaskPriority>('medium')
  const [assignedTo, setAssignedTo] = useState('')
  const [startDate, setStartDate] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [estimatedHours, setEstimatedHours] = useState('')
  const [tags, setTags] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !columnId) return

    await createTask.mutateAsync({
      column_id: columnId,
      title: title.trim(),
      description: description.trim() || undefined,
      category: category || undefined,
      priority,
      assigned_to: assignedTo || undefined,
      start_date: startDate ? new Date(startDate).toISOString() : undefined,
      due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
      estimated_hours: estimatedHours ? parseFloat(estimatedHours) : undefined,
      tags: tags.trim() ? tags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
    })
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(27,40,56,0.5)' }}>
      <div className="rounded-xl w-full max-w-lg max-h-[90vh] overflow-y-auto" style={{ background: '#F5F0E8', border: '1.5px solid #E0D9CE', boxShadow: '0 20px 60px rgba(27,40,56,0.15)' }}>
        <div className="flex items-center justify-between px-5 py-4 sticky top-0 z-10" style={{ borderBottom: '1px solid #EDE8DF', background: '#F5F0E8' }}>
          <h2 className="text-base font-medium" style={{ color: '#0A1120' }}>Nova Tarefa</h2>
          <button onClick={onClose} className="p-1 rounded-lg transition-all duration-150 hover:brightness-[0.97] cursor-pointer" style={{ color: '#A69B8D' }}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Título *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
              style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              placeholder="Descreva a tarefa..."
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Descrição</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2 resize-none"
              style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              placeholder="Detalhes opcionais..."
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Column */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Coluna</label>
              <select
                value={columnId}
                onChange={(e) => setColumnId(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              >
                {columns.map((col) => (
                  <option key={col.id} value={col.id}>{col.name}</option>
                ))}
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Prioridade</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as TaskPriority)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              >
                <option value="high">Alta</option>
                <option value="medium">Média</option>
                <option value="low">Baixa</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Category */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Categoria</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as TaskCategory | '')}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              >
                <option value="">Sem categoria</option>
                <option value="judicial">Judicial</option>
                <option value="administrativa">Administrativa</option>
                <option value="parecer">Parecer</option>
                <option value="publicacao_dje">Publicação DJE</option>
                <option value="prazo">Prazo</option>
              </select>
            </div>

            {/* Assignee */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Responsável</label>
              <select
                value={assignedTo}
                onChange={(e) => setAssignedTo(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              >
                <option value="">Sem responsável</option>
                {users?.map((u) => (
                  <option key={u.id} value={u.id}>{u.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Start date */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Data Início</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              />
            </div>

            {/* Due date */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Data Fim</label>
              <input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Estimated hours */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Horas Estimadas</label>
              <input
                type="number"
                min="0"
                step="0.5"
                value={estimatedHours}
                onChange={(e) => setEstimatedHours(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                placeholder="Ex: 4"
              />
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: '#6B6860' }}>Tags</label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                className="w-full rounded-xl px-3 py-2.5 text-base focus:outline-none focus:ring-2"
                style={{ ...inputStyle, '--tw-ring-color': '#C9A94E' } as React.CSSProperties}
                placeholder="Ex: urgente, contrato"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.97] cursor-pointer"
              style={{ background: '#F5F0E8', color: '#6B6860', border: '1.5px solid #E0D9CE' }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createTask.isPending}
              className="flex-1 px-4 py-2.5 text-sm font-medium rounded-xl transition-all duration-150 hover:brightness-[0.95] cursor-pointer disabled:opacity-50"
              style={{ background: '#142038', color: '#F5F0E8' }}
            >
              {createTask.isPending ? 'Criando...' : 'Criar Tarefa'}
            </button>
          </div>

          {createTask.isError && (
            <p className="text-sm text-center" style={{ color: '#8B2332' }}>
              {(createTask.error as any)?.response?.data?.detail ?? 'Erro ao criar tarefa'}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
