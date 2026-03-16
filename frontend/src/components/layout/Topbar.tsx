export function Topbar() {
  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return (
    <header className="h-12 border-b bg-white flex items-center justify-end px-6 flex-shrink-0">
      <button
        onClick={handleLogout}
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        Sair
      </button>
    </header>
  )
}
