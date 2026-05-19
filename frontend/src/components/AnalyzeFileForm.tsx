import { useState } from 'react'

interface AnalyzeFileFormProps {
  onSubmit: (file: File) => Promise<void>
  loading: boolean
}

export function AnalyzeFileForm({ onSubmit, loading }: AnalyzeFileFormProps) {
  const [file, setFile] = useState<File | null>(null)

  return (
    <form
      className="panel"
      onSubmit={async (event) => {
        event.preventDefault()
        if (file) await onSubmit(file)
      }}
    >
      <div>
        <p className="eyebrow">File reputation</p>
        <h2>Analyze by file</h2>
      </div>
      <p className="panel-copy">
        Upload a suspicious sample and get a VirusTotal-backed verdict with engine-level detections.
      </p>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      <button type="submit" disabled={!file || loading}>
        {loading ? 'Analyzing...' : 'Upload and analyze'}
      </button>
    </form>
  )
}
