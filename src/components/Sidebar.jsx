import { NavLink } from 'react-router-dom'

const navItems = [
  { section: 'Overview' },
  { path: '/dashboard', icon: '📊', label: 'Dashboard' },
  { section: 'Analysis' },
  { path: '/upload', icon: '📁', label: 'Upload Logs' },
  { path: '/realtime', icon: '📡', label: 'Real-Time Monitor' },
  { section: 'Security' },
  { path: '/alerts', icon: '🔔', label: 'Alerts' },
  { path: '/performance', icon: '⚡', label: 'Model Performance' },
]

export default function Sidebar({ onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <div className="sidebar-logo">🛡️</div>
          <div>
            <div className="sidebar-title">NetGuard AI</div>
            <div className="sidebar-version">v2.0 • IDS Platform</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item, i) =>
          item.section ? (
            <div key={i} className="nav-section-title">{item.section}</div>
          ) : (
            <NavLink key={item.path} to={item.path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          )
        )}
      </nav>

      <div className="sidebar-footer">
        <button className="btn-logout" onClick={onLogout}>
          <span className="nav-icon">🚪</span>
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  )
}
