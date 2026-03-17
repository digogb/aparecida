import api from './api'
import type { Board, Task, TaskCreatePayload, TaskHistoryEntry, TaskMovePayload } from '../types/task'

export async function fetchDefaultBoard(): Promise<Board> {
  const res = await api.get<Board>('/api/boards/default/tasks')
  return res.data
}

export async function fetchBoard(boardId: string): Promise<Board> {
  const res = await api.get<Board>(`/api/boards/${boardId}/tasks`)
  return res.data
}

export async function createTask(payload: TaskCreatePayload): Promise<Task> {
  const res = await api.post<Task>('/api/tasks', payload)
  return res.data
}

export async function moveTask(taskId: string, payload: TaskMovePayload): Promise<Task> {
  const res = await api.patch<Task>(`/api/tasks/${taskId}/move`, payload)
  return res.data
}

export async function fetchTaskHistory(taskId: string): Promise<TaskHistoryEntry[]> {
  const res = await api.get<TaskHistoryEntry[]>(`/api/tasks/${taskId}/history`)
  return res.data
}
