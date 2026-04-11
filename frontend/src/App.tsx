import { Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Shell } from './components/layout/Shell'
import { routes } from './routes'
import LoginPage from './components/auth/LoginPage'
import ToastContainer from './components/ui/Toast'

const qc = new QueryClient()

export default function App() {
  const isAuthenticated = !!localStorage.getItem('token')

  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Suspense fallback={<div className="flex items-center justify-center h-screen text-gray-500">Carregando...</div>}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={isAuthenticated ? <Shell /> : <Navigate to="/login" replace />}>
              {routes.map((r) => (
                <Route key={r.path} path={r.path} element={r.element} />
              ))}
            </Route>
          </Routes>
        </Suspense>
        <ToastContainer />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
