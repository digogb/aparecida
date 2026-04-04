import api from './api'
import type { DashboardAlertsResponse, DashboardRecent, DashboardStats, PareceresOverview } from '../types/dashboard'

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>('/api/dashboard/stats')
  return data
}

export async function fetchDashboardAlerts(): Promise<DashboardAlertsResponse> {
  const { data } = await api.get<DashboardAlertsResponse>('/api/dashboard/alerts')
  return data
}

export async function fetchDashboardRecent(): Promise<DashboardRecent> {
  const { data } = await api.get<DashboardRecent>('/api/dashboard/recent')
  return data
}

export async function fetchPareceresOverview(): Promise<PareceresOverview> {
  const { data } = await api.get<PareceresOverview>('/api/dashboard/pareceres-overview')
  return data
}
