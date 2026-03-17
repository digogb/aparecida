import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createTask, fetchDefaultBoard, moveTask } from '../services/taskApi'
import type { TaskCreatePayload, TaskMovePayload } from '../types/task'

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
