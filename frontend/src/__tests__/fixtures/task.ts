import type { Board, Column, Task } from '../../types/task'

export const taskFixture: Task = {
  id: 'task-1',
  column_id: 'col-todo',
  title: 'Revisar parecer 001/2026',
  description: 'Revisar e aprovar o parecer sobre licitação.',
  category: 'parecer',
  priority: 'high',
  position: 0,
  created_at: '2026-04-01T10:00:00Z',
  updated_at: '2026-04-01T10:00:00Z',
}

export const columnFixture: Column = {
  id: 'col-todo',
  board_id: 'board-1',
  name: 'A Fazer',
  position: 0,
  tasks: [taskFixture],
}

export const boardFixture: Board = {
  id: 'board-1',
  name: 'Tarefas do Escritório',
  columns: [columnFixture],
}
