import { useState } from 'react'

interface IndicatorSearchFormProps {
  onSubmit: (value: string) => Promise<void>
  loading: boolean
}

export function IndicatorSearchForm({ onSubmit, loading }: IndicatorSearchFormProps) {
  const [value, setValue] = useState('')

  return (
    <form
      className="panel"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(value.trim())
      }}
    >
      <div>
        <p className="eyebrow">IOC lookup</p>
        <h2>Analyze IP / Domain / Hash</h2>
      </div>
      <p className="panel-copy">Use one unified field for IP addresses, domains, and file hashes.</p>
      <input
        className="search-input"
        type="text"
        placeholder="8.8.8.8, example.com, or SHA256 hash"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button type="submit" disabled={!value.trim() || loading}>
        {loading ? 'Analyzing...' : 'Analyze indicator'}
      </button>
    </form>
  )
}
