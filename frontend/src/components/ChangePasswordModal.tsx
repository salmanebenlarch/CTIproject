import { useEffect, useState } from 'react'

interface ChangePasswordModalProps {
  open: boolean
  loading: boolean
  error: string | null
  onClose: () => void
  onSubmit: (currentPassword: string, newPassword: string) => Promise<void>
}

export function ChangePasswordModal({
  open,
  loading,
  error,
  onClose,
  onSubmit,
}: ChangePasswordModalProps) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  useEffect(() => {
    if (!open) {
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    }
  }, [open])

  if (!open) return null

  const mismatch = confirmPassword.length > 0 && newPassword !== confirmPassword

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div className="modal-card" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="eyebrow">Account security</p>
            <h2>Change password</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="Close change password dialog">
            ×
          </button>
        </div>

        <form
          className="modal-form"
          onSubmit={async (event) => {
            event.preventDefault()
            if (mismatch) return
            await onSubmit(currentPassword, newPassword)
          }}
        >
          <label>
            Current password
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••"
            />
          </label>
          <label>
            New password
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="At least 8 characters"
            />
          </label>
          <label>
            Confirm new password
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat new password"
            />
          </label>
          {mismatch && <div className="error-banner compact">The new passwords do not match.</div>}
          {error && <div className="error-banner compact">{error}</div>}
          <button
            type="submit"
            disabled={!currentPassword || newPassword.length < 8 || mismatch || loading}
          >
            {loading ? 'Updating...' : 'Change password'}
          </button>
        </form>
      </div>
    </div>
  )
}
