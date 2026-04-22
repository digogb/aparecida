import { lazy } from 'react'
import { Navigate } from 'react-router-dom'
import type { RouteObject } from 'react-router-dom'

const DashboardPareceresPage = lazy(() => import('./components/dashboard/DashboardPareceresPage'))
const ParecerList = lazy(() => import('./components/parecer/ParecerList'))
const LegalEditor = lazy(() => import('./components/editor/LegalEditor'))

export type AppRoute = RouteObject & {
  label?: string
  icon?: string
  showInSidebar?: boolean
}

export const routes: AppRoute[] = [
  { path: '/', element: <DashboardPareceresPage />, label: 'Dashboard', icon: 'home', showInSidebar: true },
  { path: '/pareceres', element: <ParecerList />, label: 'Pareceres', icon: 'file-text', showInSidebar: true },
  { path: '/pareceres/:id', element: <LegalEditor /> },
  { path: '/dashboard', element: <Navigate to="/" replace /> },
]

export const sidebarRoutes = routes.filter((r) => r.showInSidebar)
