import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard, Search, FolderOpen, Globe, GitBranch,
  Copy, Map, Clock, BarChart3, Moon, Sun, Download,
} from 'lucide-react'
import { useThemeStore } from '../store/theme'
import './Layout.css'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/search', icon: Search, label: 'Search' },
  { to: '/cases', icon: FolderOpen, label: 'Cases' },
  { to: '/sources', icon: Globe, label: 'Sources' },
  { to: '/graph', icon: GitBranch, label: 'Relationships' },
  { to: '/duplicates', icon: Copy, label: 'Duplicates' },
  { to: '/map', icon: Map, label: 'Map' },
  { to: '/timelines', icon: Clock, label: 'Timelines' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/export', icon: Download, label: 'Export' },
]

export default function Layout() {
  const { darkMode, toggleDarkMode } = useThemeStore()

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">⬡</span>
          <div>
            <strong>CHRE</strong>
            <small>Research Engine</small>
          </div>
        </div>
        <nav>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <button className="theme-toggle" onClick={toggleDarkMode} aria-label="Toggle theme">
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          {darkMode ? 'Light mode' : 'Dark mode'}
        </button>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
