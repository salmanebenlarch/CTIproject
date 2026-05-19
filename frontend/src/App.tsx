import { useEffect, useState } from 'react'

import { ChangePasswordModal } from './components/ChangePasswordModal'
import { LoginModal } from './components/LoginModal'
import { Navbar } from './components/Navbar'
import {
  analyzeFile,
  analyzeIndicator,
  analyzeUrl,
  changePassword,
  clearRuntimeApiKey,
  createUser,
  deleteUser,
  fetchAdminOverview,
  fetchCurrentUser,
  fetchDashboardOverview,
  fetchHIBPBreaches,
  fetchTopNews,
  fetchUserAnalyses,
  login,
  logout,
  updateRuntimeApiKey,
  updateUserRole,
} from './lib/api'
import { AdminPage } from './pages/AdminPage'
import { DashboardPage } from './pages/DashboardPage'
import { HibpPage } from './pages/HibpPage'
import { HomePage } from './pages/HomePage'
import { NewsPage } from './pages/NewsPage'
import type { AdminOverview } from './types/admin'
import type { AnalysisRecord, AnalysisResult } from './types/analysis'
import type { StoredSession } from './types/auth'
import type { DashboardOverview } from './types/dashboard'
import type { HibpLookupResponse } from './types/hibp'
import type { AppTab } from './types/navigation'
import type { NewsCategory, NewsStory } from './types/news'
import { fetchAbuseIPDB } from './lib/api'
import { AbuseIpdbPage } from './pages/AbuseIpdbPage'
import type { AbuseIPDBLookupResponse } from './types/abuseipdb'

const SESSION_STORAGE_KEY = 'sec-radar-session'
const NEWS_REFRESH_INTERVAL_MS = 5 * 60 * 1000

function readStoredSession(): StoredSession | null {
  try {
    const raw = window.localStorage.getItem(SESSION_STORAGE_KEY)
    return raw ? (JSON.parse(raw) as StoredSession) : null
  } catch {
    return null
  }
}

export default function App() {
  const [activeTab, setActiveTab] = useState<AppTab>('dashboard')
  const [showLogin, setShowLogin] = useState(false)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [session, setSession] = useState<StoredSession | null>(() => readStoredSession())

  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)

  const [pageLoading, setPageLoading] = useState(false)
  const [pageError, setPageError] = useState<string | null>(null)
  const [dashboard, setDashboard] = useState<DashboardOverview | null>(null)
  const [stories, setStories] = useState<NewsStory[]>([])
  const [newsCategory, setNewsCategory] = useState<NewsCategory>('all')
  const [adminOverview, setAdminOverview] = useState<AdminOverview | null>(null)

  const [hibpLoading, setHibpLoading] = useState(false)
  const [hibpError, setHibpError] = useState<string | null>(null)
  const [hibpResult, setHibpResult] = useState<HibpLookupResponse | null>(null)

  const [abuseLoading, setAbuseLoading] = useState(false)
  const [abuseError, setAbuseError] = useState<string | null>(null)
  const [abuseResult, setAbuseResult] = useState<AbuseIPDBLookupResponse | null>(null)

  const [selectedUsername, setSelectedUsername] = useState<string | null>(null)
  const [selectedUserAnalyses, setSelectedUserAnalyses] = useState<AnalysisRecord[]>([])
  const [userHistoryLoading, setUserHistoryLoading] = useState(false)
  const [userHistoryError, setUserHistoryError] = useState<string | null>(null)

  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)
  const [changePasswordLoading, setChangePasswordLoading] = useState(false)
  const [changePasswordError, setChangePasswordError] = useState<string | null>(null)

  const isAdmin = session?.user.role === 'admin'

  function persistSession(next: StoredSession | null) {
    setSession(next)
    if (next) {
      window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(next))
    } else {
      window.localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }

  async function loadDashboard(token = session?.access_token) {
    setPageError(null)
    setPageLoading(true)
    try {
      const overview = await fetchDashboardOverview(token)
      setDashboard(overview)
    } catch (err) {
      setPageError(err instanceof Error ? err.message : 'Failed to load dashboard.')
    } finally {
      setPageLoading(false)
    }
  }

  async function loadNews(category = newsCategory, options?: { silent?: boolean }) {
    if (!options?.silent) {
      setPageError(null)
      setPageLoading(true)
    }
    try {
      const items = await fetchTopNews(10, category)
      setStories(items)
      if (!options?.silent) {
        setPageError(null)
      }
    } catch (err) {
      setPageError(err instanceof Error ? err.message : 'Failed to load news feed.')
    } finally {
      if (!options?.silent) {
        setPageLoading(false)
      }
    }
  }

  async function loadAdminOverview(token = session?.access_token) {
    if (!token) return
    setPageError(null)
    setPageLoading(true)
    try {
      const overview = await fetchAdminOverview(token)
      setAdminOverview(overview)
    } catch (err) {
      setPageError(err instanceof Error ? err.message : 'Failed to load admin overview.')
    } finally {
      setPageLoading(false)
    }
  }

  async function loadUserHistory(username: string, token = session?.access_token) {
    if (!token) return
    setSelectedUsername(username)
    setUserHistoryError(null)
    setUserHistoryLoading(true)
    try {
      const analyses = await fetchUserAnalyses(token, username)
      setSelectedUserAnalyses(analyses)
    } catch (err) {
      setUserHistoryError(err instanceof Error ? err.message : 'Failed to load user analysis history.')
      setSelectedUserAnalyses([])
    } finally {
      setUserHistoryLoading(false)
    }
  }

  useEffect(() => {
    const token = session?.access_token
    if (!token) {
      void loadDashboard(undefined)
      return
    }

    void (async () => {
      try {
        const user = await fetchCurrentUser(token)
        persistSession({ access_token: token, user })
      } catch {
        persistSession(null)
      } finally {
        void loadDashboard(token)
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (activeTab === 'dashboard') {
      void loadDashboard()
    }
    if (activeTab === 'admin' && isAdmin) {
      void loadAdminOverview()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, isAdmin])

  useEffect(() => {
    if (activeTab !== 'news') return

    void loadNews(newsCategory)
    const intervalId = window.setInterval(() => {
      void loadNews(newsCategory, { silent: true })
    }, NEWS_REFRESH_INTERVAL_MS)

    return () => window.clearInterval(intervalId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, newsCategory])

  async function handleLogin(username: string, password: string) {
    setAuthError(null)
    setAuthLoading(true)
    try {
      const response = await login(username, password)
      persistSession({ access_token: response.access_token, user: response.user })
      setShowLogin(false)
      setActiveTab(response.user.role === 'admin' ? 'admin' : 'dashboard')
      await loadDashboard(response.access_token)
      if (response.user.role === 'admin') {
        await loadAdminOverview(response.access_token)
      }
    } catch (err) {
      setAuthError(err instanceof Error ? err.message : 'Login failed.')
    } finally {
      setAuthLoading(false)
    }
  }

  async function handleLogout() {
    try {
      await logout(session?.access_token)
    } finally {
      persistSession(null)
      setAdminOverview(null)
      setSelectedUsername(null)
      setSelectedUserAnalyses([])
      setShowLogin(false)
      setShowChangePassword(false)
      setActiveTab('dashboard')
      void loadDashboard(undefined)
    }
  }

  async function handleChangePassword(currentPassword: string, newPassword: string) {
    if (!session?.access_token) return
    setChangePasswordError(null)
    setChangePasswordLoading(true)
    try {
      await changePassword(session.access_token, currentPassword, newPassword)
      setShowChangePassword(false)
    } catch (err) {
      setChangePasswordError(err instanceof Error ? err.message : 'Failed to change password.')
    } finally {
      setChangePasswordLoading(false)
    }
  }

  async function handleHIBPLookup(email: string) {
    setHibpError(null)
    setHibpLoading(true)
    try {
      const response = await fetchHIBPBreaches(email)
      setHibpResult(response)
    } catch (err) {
      setHibpError(err instanceof Error ? err.message : 'Failed to query Have I Been Pwned.')
      setHibpResult(null)
    } finally {
      setHibpLoading(false)
    }
  }
  async function handleAbuseIPDBLookup(ip: string) {
    setAbuseError(null)
    setAbuseLoading(true)
    try {
      const response = await fetchAbuseIPDB(ip)
      setAbuseResult(response)
    } catch (err) {
      setAbuseError(err instanceof Error ? err.message : 'Failed to query AbuseIPDB.')
      setAbuseResult(null)
    } finally {
    setAbuseLoading(false)
    }
  }

  async function wrapAnalysisRequest(fn: () => Promise<AnalysisResult>) {
    setAnalysisLoading(true)
    setAnalysisError(null)
    try {
      const response = await fn()
      setResult(response)
      void loadDashboard()
      if (isAdmin) {
        void loadAdminOverview()
      }
      if (selectedUsername) {
        void loadUserHistory(selectedUsername)
      }
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Unexpected error')
      setResult(null)
    } finally {
      setAnalysisLoading(false)
    }
  }

  async function handleCreateUser(payload: {
    username: string
    password: string
    display_name?: string
    role: 'admin' | 'user'
  }) {
    if (!session?.access_token) return
    await createUser(session.access_token, payload)
    await loadAdminOverview()
  }

  async function handleUpdateApiKey(apiKey: string) {
    if (!session?.access_token) return
    await updateRuntimeApiKey(session.access_token, apiKey)
    await loadAdminOverview()
  }

  async function handleClearApiKey() {
    if (!session?.access_token) return
    await clearRuntimeApiKey(session.access_token)
    await loadAdminOverview()
  }

  async function handleDeleteUser(username: string) {
    if (!session?.access_token) return
    await deleteUser(session.access_token, username)
    if (selectedUsername === username) {
      setSelectedUsername(null)
      setSelectedUserAnalyses([])
    }
    await loadAdminOverview()
  }

  async function handleChangeUserRole(username: string, role: 'admin' | 'user') {
    if (!session?.access_token) return
    await updateUserRole(session.access_token, username, role)
    await loadAdminOverview()
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="header-shell">
          <Navbar
            activeTab={activeTab}
            onChange={setActiveTab}
            isAdmin={isAdmin}
            currentUser={session?.user ?? null}
            onLoginClick={() => {
              setAuthError(null)
              setShowLogin(true)
            }}
            onChangePasswordClick={() => {
              setChangePasswordError(null)
              setShowChangePassword(true)
            }}
            onLogout={() => void handleLogout()}
          />
        </div>
      </header>

      <LoginModal
        open={showLogin}
        loading={authLoading}
        error={authError}
        onClose={() => setShowLogin(false)}
        onSubmit={handleLogin}
      />

      <ChangePasswordModal
        open={showChangePassword}
        loading={changePasswordLoading}
        error={changePasswordError}
        onClose={() => setShowChangePassword(false)}
        onSubmit={handleChangePassword}
      />

      <main className="page-shell">
        {activeTab === 'dashboard' && (
          <DashboardPage
            overview={dashboard}
            loading={pageLoading}
            error={pageError}
            currentUser={session?.user ?? null}
            onRefresh={() => loadDashboard()}
            onQuickLink={(tab) => setActiveTab(tab)}
          />
        )}

        {activeTab === 'news' && (
          <NewsPage
            stories={stories}
            category={newsCategory}
            loading={pageLoading}
            error={pageError}
            onRefresh={() => loadNews(newsCategory)}
            onCategoryChange={(category) => setNewsCategory(category)}
          />
        )}

        {activeTab === 'hibp' && (
          <HibpPage
            result={hibpResult}
            loading={hibpLoading}
            error={hibpError}
            onLookup={handleHIBPLookup}
          />
        )}
        
        {activeTab === 'abuseipdb' && (
          <AbuseIpdbPage
            result={abuseResult}
            loading={abuseLoading}
            error={abuseError}
            onLookup={handleAbuseIPDBLookup}
          />
        )}

        {(activeTab === 'file' || activeTab === 'url' || activeTab === 'indicator') && (
          <HomePage
            activeTab={activeTab}
            loading={analysisLoading}
            error={analysisError}
            result={result}
            currentUser={session?.user ?? null}
            onAnalyzeFile={(file) => wrapAnalysisRequest(() => analyzeFile(file, session?.access_token))}
            onAnalyzeUrl={(url) => wrapAnalysisRequest(() => analyzeUrl(url, session?.access_token))}
            onAnalyzeIndicator={(value) =>
              wrapAnalysisRequest(() => analyzeIndicator(value, session?.access_token))
            }
          />
        )}

        {activeTab === 'admin' && isAdmin && (
          <AdminPage
            overview={adminOverview}
            loading={pageLoading}
            error={pageError}
            currentUser={session?.user ?? null}
            selectedUsername={selectedUsername}
            selectedUserAnalyses={selectedUserAnalyses}
            userHistoryLoading={userHistoryLoading}
            userHistoryError={userHistoryError}
            onRefresh={() => loadAdminOverview()}
            onCreateUser={handleCreateUser}
            onUpdateApiKey={handleUpdateApiKey}
            onClearApiKey={handleClearApiKey}
            onDeleteUser={handleDeleteUser}
            onChangeUserRole={handleChangeUserRole}
            onLoadUserHistory={loadUserHistory}
          />
        )}
      </main>
    </div>
  )
}
