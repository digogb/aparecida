import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchUnreadMovements } from '../services/djeApi'

export function useNotifications() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['notifications'],
    queryFn: fetchUnreadMovements,
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ['notifications'] })
  }

  return {
    notifications: query.data ?? [],
    count: query.data?.length ?? 0,
    isLoading: query.isLoading,
    invalidate,
  }
}
