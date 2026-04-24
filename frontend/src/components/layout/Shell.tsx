import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function Shell() {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <div className="flex flex-col md:flex-row min-h-screen" style={{ background: '#FAF8F5' }}>
      {/* Sidebar: inline em md+, drawer em mobile */}
      <Sidebar
        variant="inline"
        drawerOpen={drawerOpen}
        onDrawerClose={() => setDrawerOpen(false)}
      />

      {/* Conteúdo principal */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden md:h-screen">
        <Topbar onMenuToggle={() => setDrawerOpen(true)} />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
