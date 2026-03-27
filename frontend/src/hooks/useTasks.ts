import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createTask,
  createTaskComment,
  deleteTask,
  fetchDefaultBoard,
  fetchTaskComments,
  fetchTaskHistory,
  fetchUsers,
  moveTask,
  updateTask,
} from '../services/taskApi'
import type { TaskCreatePayload, TaskMovePayload, TaskUpdatePayload } from '../types/task'

export const BOARD_QUERY_KEY = ['board', 'default']

export function useBoard() {
  return useQuery({
    queryKey: BOARD_QUERY_KEY,
    queryFn: fetchDefaultBoard,
    staleTime: 30_000,
  })
}

export function useCreateTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: TaskCreatePayload) => createTask(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY })
    },
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: string; payload: TaskUpdatePayload }) =>
      updateTask(taskId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY })
    },
  })
}

export function useDeleteTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (taskId: string) => deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY })
    },
  })
}

export function useMoveTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ taskId, payload }: { taskId: string; payload: TaskMovePayload }) =>
      moveTask(taskId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: BOARD_QUERY_KEY })
    },
  })
}

export function useTaskHistory(taskId: string | null) {
  return useQuery({
    queryKey: ['task-history', taskId],
    queryFn: () => fetchTaskHistory(taskId!),
    enabled: !!taskId,
  })
}

export function useTaskComments(taskId: string | null) {
  return useQuery({
    queryKey: ['task-comments', taskId],
    queryFn: () => fetchTaskComments(taskId!),
    enabled: !!taskId,
  })
}

export function useCreateComment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ taskId, content }: { taskId: string; content: string }) =>
      createTaskComment(taskId, content),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['task-comments', variables.taskId] })
    },
  })
}

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
    staleTime: 60_000,
  })
}
