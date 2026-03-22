import { NavLink } from 'react-router-dom'
import { sidebarRoutes } from '../../routes'

export function Sidebar() {
  return (
    <aside
      className="w-56 h-screen p-4 flex-shrink-0 flex flex-col"
      style={{ background: '#1B2838' }}
    >
      <h1
        className="font-display text-lg mb-8 px-3 pt-1"
        style={{ color: '#C4953A', fontWeight: 500, letterSpacing: '-0.01em' }}
      >
        Ione
      </h1>
      <nav className="flex flex-col gap-0.5">
        {sidebarRoutes.map((r) => (
          <NavLink
            key={r.path}
            to={r.path!}
            className={({ isActive }) =>
              `px-3 py-2 rounded-lg text-sm transition-colors duration-150 ${
                isActive
                  ? 'font-medium'
                  : 'hover:bg-white/[0.06]'
              }`
            }
            style={({ isActive }) =>
              isActive
                ? { background: '#C4953A18', color: '#C4953A' }
                : { color: '#8A9BB0' }
            }
          >
            {r.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
