import api from './api'
import type {
  Board,
  Task,
  TaskComment,
  TaskCreatePayload,
  TaskHistoryEntry,
  TaskMovePayload,
  TaskUpdatePayload,
  UserMinimal,
} from '../types/task'

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

export async function updateTask(taskId: string, payload: TaskUpdatePayload): Promise<Task> {
  const res = await api.patch<Task>(`/api/tasks/${taskId}`, payload)
  return res.data
}

export async function deleteTask(taskId: string): Promise<void> {
  await api.delete(`/api/tasks/${taskId}`)
}

export async function moveTask(taskId: string, payload: TaskMovePayload): Promise<Task> {
  const res = await api.patch<Task>(`/api/tasks/${taskId}/move`, payload)
  return res.data
}

export async function fetchTaskHistory(taskId: string): Promise<TaskHistoryEntry[]> {
  const res = await api.get<TaskHistoryEntry[]>(`/api/tasks/${taskId}/history`)
  return res.data
}

export async function fetchTaskComments(taskId: string): Promise<TaskComment[]> {
  const res = await api.get<TaskComment[]>(`/api/tasks/${taskId}/comments`)
  return res.data
}

export async function createTaskComment(taskId: string, content: string): Promise<TaskComment> {
  const res = await api.post<TaskComment>(`/api/tasks/${taskId}/comments`, { content })
  return res.data
}

export async function fetchUsers(): Promise<UserMinimal[]> {
  const res = await api.get<UserMinimal[]>('/api/users')
  return res.data
}
