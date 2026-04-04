import { lazy } from 'react'
import type { RouteObject } from 'react-router-dom'

const DashboardPage = lazy(() => import('./components/dashboard/DashboardPage'))
const DashboardPareceresPage = lazy(() => import('./components/dashboard/DashboardPareceresPage'))
const ParecerList = lazy(() => import('./components/parecer/ParecerList'))
const LegalEditor = lazy(() => import('./components/editor/LegalEditor'))
const MovementList = lazy(() => import('./components/dje/MovementList'))
const KanbanBoard = lazy(() => import('./components/kanban/KanbanBoard'))

export type AppRoute = RouteObject & {
  label?: string
  icon?: string
  showInSidebar?: boolean
}

export const routes: AppRoute[] = [
  { path: '/', element: <DashboardPareceresPage />, label: 'Dashboard', icon: 'home', showInSidebar: true },
  { path: '/pareceres', element: <ParecerList />, label: 'Pareceres', icon: 'file-text', showInSidebar: true },
  { path: '/pareceres/:id', element: <LegalEditor /> },
  { path: '/movimentacoes', element: <MovementList />, label: 'Movimentações', icon: 'bell', showInSidebar: false },
  { path: '/tarefas', element: <KanbanBoard />, label: 'Tarefas', icon: 'columns', showInSidebar: false },
  { path: '/dashboard', element: <DashboardPage /> },
]

export const sidebarRoutes = routes.filter((r) => r.showInSidebar)
