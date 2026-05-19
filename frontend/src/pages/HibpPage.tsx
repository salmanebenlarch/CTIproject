import { useState } from 'react'

import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingSpinner } from '../components/LoadingSpinner'
import type { HibpLookupResponse } from '../types/hibp'

interface HibpPageProps {
  result: HibpLookupResponse | null
  loading: boolean
  error: string | null
  onLookup: (email: string) => Promise<void>
}

export function HibpPage({ result, loading, error, onLookup }: HibpPageProps) {
  const [email, setEmail] = useState('')

  return (
    <>
      <section className="hero">
        <p className="eyebrow">Exposure check</p>
        <h1>Have I Been Pwned</h1>
        <p className="hero-copy">
          Check whether an email address appears in known breach data using a backend proxy to the HIBP v3 API.
        </p>
      </section>

      <section className="panel">
        <form
          className="stack-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await onLookup(email.trim())
          }}
        >
          <label htmlFor="hibp-email">Email address</label>
          <div className="toolbar-row compact-toolbar">
            <input
              id="hibp-email"
              type="email"
              placeholder="name@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
            <button type="submit" disabled={loading || !email.trim()}>
              {loading ? 'Checking...' : 'Check breaches'}
            </button>
          </div>
        </form>
      </section>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner label="Checking Have I Been Pwned..." />}

      {!loading && result && (
        <section className="hibp-results">
          <article className={result.breached ? 'card hibp-summary danger-outline' : 'card hibp-summary success-outline'}>
            <div>
              <p className="eyebrow">Lookup result</p>
              <h3>{result.email}</h3>
              <p className="hero-copy">{result.message}</p>
            </div>
            <div className="hibp-status-pill-wrap">
              <span className={result.breached ? 'inline-badge suspicious' : 'inline-badge not_suspicious'}>
                {result.breached ? `${result.breaches.length} breach(es)` : 'All clear!'}
              </span>
            </div>
          </article>

          {result.breached && (
            <div className="hibp-breach-grid">
              {result.breaches.map((breach) => (
                <article className="card hibp-breach-card" key={`${breach.name}-${breach.breach_date ?? 'na'}`}>
                  <div className="section-header">
                    <div>
                      <p className="eyebrow">{breach.domain ?? 'Unknown domain'}</p>
                      <h3>{breach.title}</h3>
                    </div>
                    {breach.breach_date && <span className="counter-pill">{breach.breach_date}</span>}
                  </div>
                  <p className="muted-copy">{breach.description}</p>
                  <div className="chip-row">
                    {breach.data_classes.map((dataClass) => (
                      <span className="data-chip" key={`${breach.name}-${dataClass}`}>
                        {dataClass}
                      </span>
                    ))}
                  </div>
                  <div className="chip-row hibp-flags">
                    {breach.is_verified && <span className="data-chip muted">verified</span>}
                    {breach.is_sensitive && <span className="data-chip muted">sensitive</span>}
                    {breach.is_spam_list && <span className="data-chip muted">spam list</span>}
                    {breach.is_malware && <span className="data-chip muted">malware</span>}
                    {breach.is_stealer_log && <span className="data-chip muted">stealer log</span>}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}
    </>
  )
}
