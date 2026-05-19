import type { AnalysisResult } from '../types/analysis'
import type { UserInfo } from '../types/auth'
import { AnalyzeFileForm } from '../components/AnalyzeFileForm'
import { AnalyzeUrlForm } from '../components/AnalyzeUrlForm'
import { IndicatorSearchForm } from '../components/IndicatorSearchForm'
import { EngineResultsTable } from '../components/EngineResultsTable'
import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { VerdictCard } from '../components/VerdictCard'

interface HomePageProps {
  activeTab: 'file' | 'url' | 'indicator'
  loading: boolean
  error: string | null
  result: AnalysisResult | null
  currentUser: UserInfo | null
  onAnalyzeFile: (file: File) => Promise<void>
  onAnalyzeUrl: (url: string) => Promise<void>
  onAnalyzeIndicator: (value: string) => Promise<void>
}

export function HomePage(props: HomePageProps) {
  const {
    activeTab,
    loading,
    error,
    result,
    currentUser,
    onAnalyzeFile,
    onAnalyzeUrl,
    onAnalyzeIndicator,
  } = props

  return (
    <>
      <section className="hero hero-centered">
        <p className="eyebrow">Threat analysis workspace</p>
        <h1>Analyze files, URLs, IPs, domains, and hashes</h1>
        <p className="hero-copy">
          Fast VirusTotal-powered screening with a clear verdict, SOC-style cards, and engine-level detail.
        </p>
        {currentUser && (
          <div className="info-strip">
            Logged in as <strong>{currentUser.display_name}</strong> ({currentUser.role}) — your analyses are added to the dashboard timeline.
          </div>
        )}
      </section>

      {activeTab === 'file' && <AnalyzeFileForm onSubmit={onAnalyzeFile} loading={loading} />}
      {activeTab === 'url' && <AnalyzeUrlForm onSubmit={onAnalyzeUrl} loading={loading} />}
      {activeTab === 'indicator' && (
        <IndicatorSearchForm onSubmit={onAnalyzeIndicator} loading={loading} />
      )}

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner label="Running analysis..." />}

      {!loading && !result && <div className="empty-state">Run an analysis to see the verdict and scanner details.</div>}

      {result && !loading && (
        <div className="results-grid">
          <VerdictCard result={result} />
          <EngineResultsTable engines={result.engines} />
        </div>
      )}
    </>
  )
}
