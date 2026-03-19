import { NavLink } from 'react-router-dom'
import { sidebarRoutes } from '../../routes'

export function Sidebar() {
  return (
    <aside className="w-56 border-r bg-gray-50 h-screen p-4 flex-shrink-0">
      <h1 className="text-lg font-semibold mb-6 text-gray-900">Ione</h1>
      <nav className="flex flex-col gap-1">
        {sidebarRoutes.map((r) => (
          <NavLink
            key={r.path}
            to={r.path!}
            className={({ isActive }) =>
              `px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`
            }
          >
            {r.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
