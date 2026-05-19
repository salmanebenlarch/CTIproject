import { useState } from 'react'

import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingSpinner } from '../components/LoadingSpinner'
import type { AnalysisRecord } from '../types/analysis'
import type { UserInfo } from '../types/auth'
import type { AdminOverview } from '../types/admin'

interface AdminPageProps {
  overview: AdminOverview | null
  loading: boolean
  error: string | null
  currentUser: UserInfo | null
  selectedUsername: string | null
  selectedUserAnalyses: AnalysisRecord[]
  userHistoryLoading: boolean
  userHistoryError: string | null
  onRefresh: () => Promise<void>
  onCreateUser: (payload: {
    username: string
    password: string
    display_name?: string
    role: 'admin' | 'user'
  }) => Promise<void>
  onUpdateApiKey: (apiKey: string) => Promise<void>
  onClearApiKey: () => Promise<void>
  onDeleteUser: (username: string) => Promise<void>
  onChangeUserRole: (username: string, role: 'admin' | 'user') => Promise<void>
  onLoadUserHistory: (username: string) => Promise<void>
}

export function AdminPage({
  overview,
  loading,
  error,
  currentUser,
  selectedUsername,
  selectedUserAnalyses,
  userHistoryLoading,
  userHistoryError,
  onRefresh,
  onCreateUser,
  onUpdateApiKey,
  onClearApiKey,
  onDeleteUser,
  onChangeUserRole,
  onLoadUserHistory,
}: AdminPageProps) {
  const [apiKey, setApiKey] = useState('')
  const [userForm, setUserForm] = useState<{
    username: string
    password: string
    display_name: string
    role: 'admin' | 'user'
  }>({ username: '', password: '', display_name: '', role: 'user' })
  const [submittingUser, setSubmittingUser] = useState(false)
  const [updatingKey, setUpdatingKey] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [busyUsername, setBusyUsername] = useState<string | null>(null)

  return (
    <>
      <section className="hero">
        <p className="eyebrow">Privileged workspace</p>
        <h1>Admin controls</h1>
        <p className="hero-copy">
          Manage runtime API key overrides, inspect persisted analyses, and control user access.
        </p>
        <button type="button" onClick={() => void onRefresh()}>
          Refresh admin view
        </button>
      </section>

      {error && <ErrorBanner message={error} />}
      {actionError && <ErrorBanner message={actionError} />}
      {loading && <LoadingSpinner label="Loading admin controls..." />}

      {overview && !loading && (
        <div className="admin-grid">
          <section className="card">
            <div className="section-header">
              <div>
                <p className="eyebrow">API key</p>
                <h3>VirusTotal runtime key</h3>
              </div>
            </div>
            <p className="muted-copy">
              Current source: <strong>{overview.api_key_status.source}</strong>
            </p>
            <p className="muted-copy">
              Active key: <strong>{overview.api_key_status.masked_key ?? 'not configured'}</strong>
            </p>
            <form
              className="stack-form"
              onSubmit={async (event) => {
                event.preventDefault()
                setActionError(null)
                setUpdatingKey(true)
                try {
                  await onUpdateApiKey(apiKey.trim())
                  setApiKey('')
                } catch (err) {
                  setActionError(err instanceof Error ? err.message : 'Failed to update runtime key.')
                } finally {
                  setUpdatingKey(false)
                }
              }}
            >
              <input
                type="password"
                placeholder="Paste a new runtime VirusTotal API key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
              <div className="inline-actions">
                <button type="submit" disabled={!apiKey.trim() || updatingKey}>
                  {updatingKey ? 'Saving...' : 'Override runtime key'}
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={async () => {
                    setActionError(null)
                    try {
                      await onClearApiKey()
                    } catch (err) {
                      setActionError(err instanceof Error ? err.message : 'Failed to clear runtime key.')
                    }
                  }}
                >
                  Clear override
                </button>
              </div>
            </form>
          </section>

          <section className="card">
            <div className="section-header">
              <div>
                <p className="eyebrow">User management</p>
                <h3>Create persistent user</h3>
              </div>
              <span className="counter-pill">{overview.users.length} users</span>
            </div>
            <form
              className="stack-form"
              onSubmit={async (event) => {
                event.preventDefault()
                setActionError(null)
                setSubmittingUser(true)
                try {
                  await onCreateUser({
                    username: userForm.username.trim(),
                    password: userForm.password,
                    display_name: userForm.display_name.trim() || undefined,
                    role: userForm.role,
                  })
                  setUserForm({ username: '', password: '', display_name: '', role: 'user' })
                } catch (err) {
                  setActionError(err instanceof Error ? err.message : 'Failed to create user.')
                } finally {
                  setSubmittingUser(false)
                }
              }}
            >
              <input
                placeholder="Username"
                value={userForm.username}
                onChange={(e) => setUserForm((state) => ({ ...state, username: e.target.value }))}
              />
              <input
                placeholder="Display name"
                value={userForm.display_name}
                onChange={(e) => setUserForm((state) => ({ ...state, display_name: e.target.value }))}
              />
              <input
                type="password"
                placeholder="Password"
                value={userForm.password}
                onChange={(e) => setUserForm((state) => ({ ...state, password: e.target.value }))}
              />
              <select
                value={userForm.role}
                onChange={(e) =>
                  setUserForm((state) => ({ ...state, role: e.target.value as 'admin' | 'user' }))
                }
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
              <button
                type="submit"
                disabled={!userForm.username.trim() || userForm.password.length < 8 || submittingUser}
              >
                {submittingUser ? 'Creating...' : 'Create user'}
              </button>
            </form>
          </section>

          <section className="card full-span">
            <div className="section-header">
              <div>
                <p className="eyebrow">Users</p>
                <h3>Access list and role controls</h3>
              </div>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Display name</th>
                    <th>Role</th>
                    <th>Analyses</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.users.map((user) => {
                    const isCurrent = currentUser?.username === user.username
                    const targetRole = user.role === 'admin' ? 'user' : 'admin'
                    const roleLabel = user.role === 'admin' ? 'Make user' : 'Make admin'
                    return (
                      <tr key={user.username} className={selectedUsername === user.username ? 'selected-row' : undefined}>
                        <td>{user.username}</td>
                        <td>{user.display_name}</td>
                        <td>
                          <span className={`inline-badge ${user.role}`}>{user.role}</span>
                        </td>
                        <td>{overview.analysis_counts_by_user[user.username] ?? 0}</td>
                        <td>
                          <div className="table-actions">
                            <button
                              type="button"
                              className="secondary-button"
                              onClick={() => void onLoadUserHistory(user.username)}
                            >
                              View history
                            </button>
                            <button
                              type="button"
                              className="secondary-button"
                              disabled={isCurrent || busyUsername === user.username}
                              onClick={async () => {
                                setActionError(null)
                                setBusyUsername(user.username)
                                try {
                                  await onChangeUserRole(user.username, targetRole)
                                } catch (err) {
                                  setActionError(err instanceof Error ? err.message : 'Failed to update role.')
                                } finally {
                                  setBusyUsername(null)
                                }
                              }}
                            >
                              {busyUsername === user.username ? 'Saving...' : roleLabel}
                            </button>
                            <button
                              type="button"
                              className="danger-button"
                              disabled={isCurrent || busyUsername === user.username}
                              onClick={async () => {
                                const confirmed = window.confirm(`Delete user ${user.username}?`)
                                if (!confirmed) return
                                setActionError(null)
                                setBusyUsername(user.username)
                                try {
                                  await onDeleteUser(user.username)
                                } catch (err) {
                                  setActionError(err instanceof Error ? err.message : 'Failed to delete user.')
                                } finally {
                                  setBusyUsername(null)
                                }
                              }}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card full-span">
            <div className="section-header">
              <div>
                <p className="eyebrow">All analyses</p>
                <h3>Recent analysis log</h3>
              </div>
              <span className="counter-pill">{overview.analyses.length} entries</span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Input</th>
                    <th>Type</th>
                    <th>Verdict</th>
                    <th>User</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.analyses.map((record) => (
                    <tr key={record.id}>
                      <td>{new Date(record.created_at).toLocaleString()}</td>
                      <td>{record.input_value}</td>
                      <td>{record.indicator_type}</td>
                      <td>
                        <span className={`inline-badge ${record.verdict}`}>{record.verdict.replace('_', ' ')}</span>
                      </td>
                      <td>{record.username ?? 'guest'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card full-span">
            <div className="section-header">
              <div>
                <p className="eyebrow">Per-user history</p>
                <h3>{selectedUsername ? `Analysis history for ${selectedUsername}` : 'Select a user to inspect history'}</h3>
              </div>
            </div>
            {userHistoryError && <ErrorBanner message={userHistoryError} />}
            {userHistoryLoading && <LoadingSpinner label="Loading user history..." />}
            {!userHistoryLoading && !selectedUsername && (
              <p className="muted-copy">Choose “View history” on a user row to inspect their activity.</p>
            )}
            {!userHistoryLoading && selectedUsername && selectedUserAnalyses.length === 0 && (
              <p className="muted-copy">No analyses recorded for this user yet.</p>
            )}
            {!userHistoryLoading && selectedUserAnalyses.length > 0 && (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Input</th>
                      <th>Type</th>
                      <th>Verdict</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedUserAnalyses.map((record) => (
                      <tr key={record.id}>
                        <td>{new Date(record.created_at).toLocaleString()}</td>
                        <td>{record.input_value}</td>
                        <td>{record.indicator_type}</td>
                        <td>
                          <span className={`inline-badge ${record.verdict}`}>{record.verdict.replace('_', ' ')}</span>
                        </td>
                        <td>{record.raw_status ?? 'completed'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      )}
    </>
  )
}
