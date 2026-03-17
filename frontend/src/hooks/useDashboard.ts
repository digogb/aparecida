import { useQuery } from '@tanstack/react-query'
import { fetchDashboardAlerts, fetchDashboardRecent, fetchDashboardStats } from '../services/dashboardApi'

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: fetchDashboardStats,
    staleTime: 60_000,
    refetchInterval: 120_000,
  })
}

export function useDashboardAlerts() {
  return useQuery({
    queryKey: ['dashboard', 'alerts'],
    queryFn: fetchDashboardAlerts,
    staleTime: 60_000,
    refetchInterval: 120_000,
  })
}

export function useDashboardRecent() {
  return useQuery({
    queryKey: ['dashboard', 'recent'],
    queryFn: fetchDashboardRecent,
    staleTime: 60_000,
  })
}
