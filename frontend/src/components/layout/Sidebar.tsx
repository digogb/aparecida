import { NavLink } from 'react-router-dom'
import { sidebarRoutes } from '../../routes'

export function Sidebar() {
  return (
    <aside
      className="w-56 h-screen p-4 flex-shrink-0 flex flex-col"
      style={{ background: 'linear-gradient(180deg, #0A1020 0%, #142038 60%, #1a2847 100%)' }}
    >
      <div className="flex items-center gap-3 mb-8 px-3 pt-1">
        <div>
          <div className="font-display text-base font-medium" style={{ color: '#C9A94E', letterSpacing: '-0.01em', lineHeight: 1.2 }}>
            Ione Advogados
          </div>
          <div className="text-xs" style={{ color: '#C9A94E99', letterSpacing: '0.04em' }}>
            &amp; Associados
          </div>
        </div>
        <div className="h-8 w-px" style={{ background: '#C9A94E33' }} />
      </div>
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
                ? { background: '#C9A94E18', color: '#C9A94E' }
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
