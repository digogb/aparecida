import { useState } from 'react'
import { X } from 'lucide-react'
import { useCreateTask } from '../../hooks/useTasks'
import type { Column, TaskCategory, TaskPriority } from '../../types/task'

interface CreateTaskModalProps {
  columns: Column[]
  defaultColumnId?: string
  onClose: () => void
}

export default function CreateTaskModal({ columns, defaultColumnId, onClose }: CreateTaskModalProps) {
  const createTask = useCreateTask()

  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [columnId, setColumnId] = useState(defaultColumnId ?? columns[0]?.id ?? '')
  const [category, setCategory] = useState<TaskCategory | ''>('')
  const [priority, setPriority] = useState<TaskPriority>('medium')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !columnId) return

    await createTask.mutateAsync({
      column_id: columnId,
      title: title.trim(),
      description: description.trim() || undefined,
      category: category || undefined,
      priority,
    })
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between px-5 py-4 border-b">
          <h2 className="text-base font-semibold text-gray-900">Nova Tarefa</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Título *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Descreva a tarefa..."
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              placeholder="Detalhes opcionais..."
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Column */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Coluna</label>
              <select
                value={columnId}
                onChange={(e) => setColumnId(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {columns.map((col) => (
                  <option key={col.id} value={col.id}>{col.name}</option>
                ))}
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prioridade</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as TaskPriority)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="high">Alta</option>
                <option value="medium">Média</option>
                <option value="low">Baixa</option>
              </select>
            </div>
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as TaskCategory | '')}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Sem categoria</option>
              <option value="judicial">Judicial</option>
              <option value="administrativa">Administrativa</option>
              <option value="parecer">Parecer</option>
              <option value="publicacao_dje">Publicação DJE</option>
              <option value="prazo">Prazo</option>
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createTask.isPending}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {createTask.isPending ? 'Criando...' : 'Criar Tarefa'}
            </button>
          </div>

          {createTask.isError && (
            <p className="text-xs text-red-600 text-center">
              {(createTask.error as any)?.response?.data?.detail ?? 'Erro ao criar tarefa'}
            </p>
          )}
        </form>
      </div>
    </div>
  )
}
