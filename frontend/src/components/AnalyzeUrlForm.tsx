import { useState } from 'react'

interface AnalyzeUrlFormProps {
  onSubmit: (url: string) => Promise<void>
  loading: boolean
}

export function AnalyzeUrlForm({ onSubmit, loading }: AnalyzeUrlFormProps) {
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
        <p className="eyebrow">URL analysis</p>
        <h2>Analyze URL</h2>
      </div>
      <p className="panel-copy">Check whether a link has been flagged as malicious or suspicious.</p>
      <input
        className="search-input"
        type="url"
        placeholder="https://example.com"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button type="submit" disabled={!value.trim() || loading}>
        {loading ? 'Analyzing...' : 'Analyze URL'}
      </button>
    </form>
  )
}
