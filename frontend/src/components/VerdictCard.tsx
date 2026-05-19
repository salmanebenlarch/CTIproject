import type { AnalysisResult } from '../types/analysis'

export function VerdictCard({ result }: { result: AnalysisResult }) {
  const labelMap = {
    suspicious: 'Suspicious',
    not_suspicious: 'Not suspicious',
    unknown: 'Unknown',
  } as const

  return (
    <section className="card verdict-card">
      <div className={`badge ${result.verdict}`}>{labelMap[result.verdict]}</div>
      <h3>{result.input_value}</h3>
      <p>{result.summary}</p>

      <div className="meta-grid">
        <div>
          <span>Type</span>
          <strong>{result.indicator_type}</strong>
        </div>
        <div>
          <span>Reputation</span>
          <strong>{result.metadata.reputation ?? 'n/a'}</strong>
        </div>
        <div>
          <span>Community votes</span>
          <strong>{Object.values(result.metadata.total_votes).reduce((sum, count) => sum + count, 0)}</strong>
        </div>
        <div>
          <span>Status</span>
          <strong>{result.raw_status ?? 'completed'}</strong>
        </div>
      </div>

      <div className="stats-grid">
        <div><strong>{result.detection_stats.malicious}</strong><span>malicious</span></div>
        <div><strong>{result.detection_stats.suspicious}</strong><span>suspicious</span></div>
        <div><strong>{result.detection_stats.harmless}</strong><span>harmless</span></div>
        <div><strong>{result.detection_stats.undetected}</strong><span>undetected</span></div>
      </div>

      {!!result.metadata.tags.length && (
        <div className="chip-row">
          {result.metadata.tags.slice(0, 8).map((tag) => (
            <span className="data-chip" key={tag}>{tag}</span>
          ))}
        </div>
      )}
    </section>
  )
}
