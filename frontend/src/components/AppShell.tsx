import { NavLink, Outlet } from 'react-router-dom'
import { Logo } from './Logo'
import { useAuthStore } from '../lib/auth-store'
import { useWorkspaceStore } from '../lib/workspace-store'

const navItems = [
  { to: '/app', label: 'Dashboard', icon: '🏠', end: true },
  { to: '/app/workspace', label: 'AI Employees', icon: '🤖', end: false },
]

export function AppShell() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const workspace = useWorkspaceStore((s) => s.current)

  const initials = user?.email ? user.email.slice(0, 2).toUpperCase() : '?'

  return (
    <div className="flex min-h-screen">
      <aside className="fixed top-0 bottom-0 left-0 w-[220px] glass border-r border-border p-3.5 flex flex-col z-20">
        <div className="flex items-center gap-2 px-2 pb-6 font-display font-bold text-[17px]">
          <Logo size={20} />
          Vynera
        </div>
        <nav className="flex flex-col gap-0.5">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[13.5px] transition-colors ${
                  isActive ? 'bg-primary/15 text-white' : 'text-text-dim hover:bg-white/5 hover:text-text'
                }`
              }
            >
              <span className="w-4 text-center">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto pt-4 border-t border-border">
          <button
            onClick={logout}
            className="w-full text-left text-[12.5px] text-text-dim hover:text-text px-3 py-2"
          >
            Log out
          </button>
        </div>
      </aside>

      <div className="ml-[220px] flex-1">
        <header className="fixed top-0 left-[220px] right-0 h-[60px] glass border-b border-border z-10 flex items-center justify-between px-7">
          <div className="font-display font-bold text-[16px]">
            {workspace ? workspace.name : 'VYNERA'}
          </div>
          <div className="flex items-center gap-2 text-[13px] text-text-dim">
            <div className="w-[26px] h-[26px] rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-[11px] font-semibold text-bg">
              {initials}
            </div>
            {user?.email}
          </div>
        </header>

        <main className="pt-[60px] p-9">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
