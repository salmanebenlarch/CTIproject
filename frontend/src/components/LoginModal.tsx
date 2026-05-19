import { useEffect, useState } from 'react'

interface LoginModalProps {
  open: boolean
  loading: boolean
  error: string | null
  onClose: () => void
  onSubmit: (username: string, password: string) => Promise<void>
}

export function LoginModal({ open, loading, error, onClose, onSubmit }: LoginModalProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  useEffect(() => {
    if (!open) {
      setUsername('')
      setPassword('')
    }
  }, [open])

  if (!open) return null

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div className="modal-card" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="eyebrow">Authentication</p>
            <h2>Login</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close login dialog">
            ×
          </button>
        </div>

        <form
          className="modal-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await onSubmit(username.trim(), password)
          }}
        >
          <label>
            Username
            <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="admin" />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </label>
          {error && <div className="error-banner compact">{error}</div>}
          <button type="submit" disabled={!username || !password || loading}>
            {loading ? 'Signing in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}
