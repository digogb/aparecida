import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import type { User } from '../types'

/** Usuário autenticado atual (/api/auth/me). queryKey compartilhada → o react-query
 *  deduplica entre todos os consumidores (lista, dashboard, cards). */
export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      const { data } = await api.get<User>('/api/auth/me')
      return data
    },
    staleTime: 5 * 60_000,
  })
}
