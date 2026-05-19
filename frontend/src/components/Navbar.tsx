import type { UserInfo } from '../types/auth'
import type { AppTab } from '../types/navigation'

interface NavbarProps {
  activeTab: AppTab
  onChange: (tab: AppTab) => void
  isAdmin: boolean
  currentUser: UserInfo | null
  onLoginClick: () => void
  onChangePasswordClick: () => void
  onLogout: () => void
}

export function Navbar({
  activeTab,
  onChange,
  isAdmin,
  currentUser,
  onLoginClick,
  onChangePasswordClick,
  onLogout,
}: NavbarProps) {
  const tabs: { key: AppTab; label: string }[] = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'news', label: 'News' },
    { key: 'hibp', label: 'Pwned?' },
    { key: 'abuseipdb', label: 'AbuseIPDB' },
    { key: 'file', label: 'Analyze by file' },
    { key: 'url', label: 'Analyze URL' },
    { key: 'indicator', label: 'Analyze IP / Domain / Hash' },
  ]

  if (isAdmin) {
    tabs.push({ key: 'admin', label: 'Admin' })
  }

  return (
    <nav className="top-nav" aria-label="Primary navigation">
      <div className="brand-block">
        <img src="/logo.png" alt="HISN logo" className="brand-logo" />
        <div className="brand-meta">
          <div className="brand-subtitle">Threat analysis workspace</div>
        </div>
      </div>

      <div className="nav-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={activeTab === tab.key ? 'nav-tab active' : 'nav-tab'}
            onClick={() => onChange(tab.key)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="nav-actions">
        {currentUser ? (
          <>
            <div className="user-chip">
              <span className="user-name">{currentUser.display_name}</span>
              <span className={`role-pill ${currentUser.role}`}>{currentUser.role}</span>
            </div>
            <button type="button" className="nav-action secondary" onClick={onChangePasswordClick}>
              Change password
            </button>
            <button type="button" className="nav-action secondary" onClick={onLogout}>
              Logout
            </button>
          </>
        ) : (
          <button type="button" className="nav-action" onClick={onLoginClick}>
            Login
          </button>
        )}
      </div>
    </nav>
  )
}
