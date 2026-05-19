import { useState } from 'react'

import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingSpinner } from '../components/LoadingSpinner'
import type { AbuseIPDBLookupResponse } from '../types/abuseipdb'

interface AbuseIpdbPageProps {
  result: AbuseIPDBLookupResponse | null
  loading: boolean
  error: string | null
  onLookup: (ip: string) => Promise<void>
}

function ScoreBadge({ score }: { score: number }) {
  const className =
    score >= 75
      ? 'inline-badge suspicious'
      : score >= 25
        ? 'inline-badge unknown'
        : 'inline-badge not_suspicious'
  const label =
    score >= 75 ? 'High risk' : score >= 25 ? 'Moderate' : 'Low risk'

  return <span className={className}>{label} — {score}%</span>
}

export function AbuseIpdbPage({ result, loading, error, onLookup }: AbuseIpdbPageProps) {
  const [ip, setIp] = useState('')

  const data = result?.result

  return (
    <>
      <section className="hero">
        <p className="eyebrow">IP Reputation</p>
        <h1>AbuseIPDB</h1>
        <p className="hero-copy">
          Check whether an IP address has been reported for malicious activity using the AbuseIPDB v2 API.
        </p>
      </section>

      <section className="panel">
        <form
          className="stack-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await onLookup(ip.trim())
          }}
        >
          <label htmlFor="abuseipdb-ip">IP Address</label>
          <div className="toolbar-row compact-toolbar">
            <input
              id="abuseipdb-ip"
              type="text"
              placeholder="e.g. 118.25.6.39"
              value={ip}
              onChange={(event) => setIp(event.target.value)}
              required
            />
            <button type="submit" disabled={loading || !ip.trim()}>
              {loading ? 'Checking...' : 'Check IP'}
            </button>
          </div>
        </form>
      </section>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner label="Querying AbuseIPDB..." />}

      {!loading && data && (
        <section className="hibp-results">
          {/* Summary card */}
          <article
            className={
              data.abuseConfidenceScore >= 25
                ? 'card hibp-summary danger-outline'
                : 'card hibp-summary success-outline'
            }
          >
            <div>
              <p className="eyebrow">Lookup result</p>
              <h3>{data.ipAddress}</h3>
              <p className="hero-copy">
                {data.isp ?? 'Unknown ISP'}
                {data.domain ? ` — ${data.domain}` : ''}
                {data.countryName ? ` · ${data.countryName}` : ''}
              </p>
            </div>
            <div className="hibp-status-pill-wrap">
              <ScoreBadge score={data.abuseConfidenceScore} />
            </div>
          </article>

          {/* Details grid */}
          <div className="hibp-breach-grid">
            {/* Info card */}
            <article className="card hibp-breach-card">
              <div className="section-header">
                <div>
                  <p className="eyebrow">IP Details</p>
                  <h3>Network info</h3>
                </div>
              </div>
              <div className="chip-row">
                <span className="data-chip">IPv{data.ipVersion}</span>
                {data.isPublic && <span className="data-chip">Public</span>}
                {data.isTor && <span className="data-chip muted">Tor exit node</span>}
                {data.isWhitelisted && <span className="data-chip muted">Whitelisted</span>}
                {data.usageType && <span className="data-chip muted">{data.usageType}</span>}
                {data.hostnames.map((h) => (
                  <span className="data-chip muted" key={h}>{h}</span>
                ))}
              </div>
            </article>

            {/* Stats card */}
            <article className="card hibp-breach-card">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Abuse Stats</p>
                  <h3>Report summary</h3>
                </div>
                {data.lastReportedAt && (
                  <span className="counter-pill">
                    Last: {new Date(data.lastReportedAt).toLocaleDateString()}
                  </span>
                )}
              </div>
              <div className="chip-row">
                <span className="data-chip">{data.totalReports} reports</span>
                <span className="data-chip">{data.numDistinctUsers} reporters</span>
                <span className="data-chip">{data.abuseConfidenceScore}% confidence</span>
              </div>
            </article>
          </div>

          {/* Reports list */}
          {data.reports.length > 0 && (
            <>
              <h2 style={{ marginTop: '2rem' }}>Recent reports</h2>
              <div className="hibp-breach-grid">
                {data.reports.map((report, index) => (
                  <article className="card hibp-breach-card" key={index}>
                    <div className="section-header">
                      <div>
                        <p className="eyebrow">{report.reporterCountryName}</p>
                        <h3>{new Date(report.reportedAt).toLocaleString()}</h3>
                      </div>
                    </div>
                    {report.comment && (
                      <p className="muted-copy">{report.comment}</p>
                    )}
                    <div className="chip-row">
                      {report.categories.map((cat) => (
                        <span className="data-chip" key={cat}>Cat. {cat}</span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}
        </section>
      )}
    </>
  )
}