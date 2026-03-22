import NotificationBell from '../dje/NotificationBell'

export function Topbar() {
  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return (
    <header className="h-12 flex items-center justify-end px-6 flex-shrink-0 gap-2" style={{ background: '#E8E5DE', borderBottom: '1px solid #DDD9D2' }}>
      <NotificationBell />
      <button
        onClick={handleLogout}
        className="text-sm transition-all duration-150 cursor-pointer"
        style={{ color: '#6B6860' }}
      >
        Sair
      </button>
    </header>
  )
}
