import { useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingSpinner } from '../components/LoadingSpinner'
import type { UserInfo } from '../types/auth'
import type { DashboardOverview, QuickLinkTab } from '../types/dashboard'

interface DashboardPageProps {
  overview: DashboardOverview | null
  loading: boolean
  error: string | null
  currentUser: UserInfo | null
  onRefresh: () => Promise<void>
  onQuickLink: (tab: QuickLinkTab) => void
}

const PIE_COLORS = ['#ef5c77', '#ff9b54', '#47d28b', '#7ca7ff']
const BAR_COLORS = ['#ef5c77', '#7ca7ff', '#47d28b', '#ffcb68', '#c98eff']

type TimeframeMode = 'day' | 'week'

export function DashboardPage({
  overview,
  loading,
  error,
  currentUser,
  onRefresh,
  onQuickLink,
}: DashboardPageProps) {
  const [timeframe, setTimeframe] = useState<TimeframeMode>('day')

  const lineData = useMemo(() => {
    if (!overview) return []
    return timeframe === 'day' ? overview.analyses_over_time_day : overview.analyses_over_time_week
  }, [overview, timeframe])

  const barData = useMemo(() => {
    if (!overview) return []
    return Object.entries(overview.analyses_by_type).map(([type, count]) => ({ type, count }))
  }, [overview])

  const hasLineData = lineData.some((item) => item.count > 0)
  const hasPieData = (overview?.verdict_distribution ?? []).some((item) => item.count > 0)
  const hasBarData = barData.some((item) => item.count > 0)

  return (
    <>
      <section className="hero">
        <p className="eyebrow">SOC overview</p>
        <h1>{currentUser ? `Welcome back, ${currentUser.display_name}` : 'Dashboard'}</h1>
        <p className="hero-copy">
          Quick stats, recent analyses, and direct links to the most-used workflows.
        </p>
        <button type="button" onClick={() => void onRefresh()}>
          Refresh overview
        </button>
      </section>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner label="Refreshing dashboard..." />}

      {overview && !loading && (
        <>
          <section className="dashboard-grid">
            <article className="card stat-card accent">
              <span>Total analyses</span>
              <strong>{overview.total_analyses}</strong>
            </article>
            <article className="card stat-card danger">
              <span>Suspicious</span>
              <strong>{overview.suspicious_count}</strong>
            </article>
            <article className="card stat-card success">
              <span>Not suspicious</span>
              <strong>{overview.not_suspicious_count}</strong>
            </article>
            <article className="card stat-card warning">
              <span>Unknown</span>
              <strong>{overview.unknown_count}</strong>
            </article>
          </section>

          <section className="charts-grid charts-grid-priority">
            <article className="card chart-card">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Verdicts</p>
                  <h3>Distribution</h3>
                </div>
              </div>
              {!hasPieData ? (
                <div className="empty-state">No verdict distribution data yet.</div>
              ) : (
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={overview.verdict_distribution}
                        dataKey="count"
                        nameKey="label"
                        innerRadius={70}
                        outerRadius={105}
                        paddingAngle={3}
                      >
                        {overview.verdict_distribution.map((entry, index) => (
                          <Cell key={entry.label} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </article>

            <article className="card chart-card">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Volume</p>
                  <h3>Analyses by type</h3>
                </div>
              </div>
              {!hasBarData ? (
                <div className="empty-state">No analysis type data yet.</div>
              ) : (
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={barData}>
                      <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                      <XAxis dataKey="type" tick={{ fill: '#9fb3d8', fontSize: 12 }} />
                      <YAxis allowDecimals={false} tick={{ fill: '#9fb3d8', fontSize: 12 }} />
                      <Tooltip />
                      <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                        {barData.map((entry, index) => (
                          <Cell key={entry.type} fill={BAR_COLORS[index % BAR_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </article>
          </section>

          <section className="chart-stack">
            <article className="card chart-card chart-card-wide">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Trend</p>
                  <h3>Analyses over time</h3>
                </div>
                <div className="segmented-control">
                  <button
                    type="button"
                    className={timeframe === 'day' ? 'nav-tab active compact-tab' : 'nav-tab compact-tab'}
                    onClick={() => setTimeframe('day')}
                  >
                    Daily
                  </button>
                  <button
                    type="button"
                    className={timeframe === 'week' ? 'nav-tab active compact-tab' : 'nav-tab compact-tab'}
                    onClick={() => setTimeframe('week')}
                  >
                    Weekly
                  </button>
                </div>
              </div>
              {!hasLineData ? (
                <div className="empty-state">No analysis trend data yet.</div>
              ) : (
                <div className="chart-wrap">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={lineData}>
                      <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                      <XAxis dataKey="label" tick={{ fill: '#9fb3d8', fontSize: 12 }} />
                      <YAxis allowDecimals={false} tick={{ fill: '#9fb3d8', fontSize: 12 }} />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="count"
                        name={timeframe === 'day' ? 'Analyses / day' : 'Analyses / week'}
                        stroke="#7ca7ff"
                        strokeWidth={3}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </article>
          </section>

          <div className="dashboard-two-col">
            <section className="card">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Quick links</p>
                  <h3>Analyst shortcuts</h3>
                </div>
              </div>
              <div className="quick-links-grid">
                {overview.quick_links.map((link) => (
                  <button key={link.label} type="button" className="quick-link-card" onClick={() => onQuickLink(link.tab)}>
                    <strong>{link.label}</strong>
                    <span>{link.description}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="card">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Coverage split</p>
                  <h3>Analyses by type</h3>
                </div>
              </div>
              <div className="chip-row">
                {Object.entries(overview.analyses_by_type).length === 0 && (
                  <span className="data-chip muted">No data yet</span>
                )}
                {Object.entries(overview.analyses_by_type).map(([type, count]) => (
                  <span className="data-chip" key={type}>
                    {type}: {count}
                  </span>
                ))}
              </div>
            </section>
          </div>

          <section className="card">
            <div className="section-header">
              <div>
                <p className="eyebrow">Recent activity</p>
                <h3>Latest analyses</h3>
              </div>
              <span className="counter-pill">{overview.recent_analyses.length} rows</span>
            </div>
            {overview.recent_analyses.length === 0 ? (
              <p className="muted-copy">No analyses yet. Run a scan from one of the analyze tabs.</p>
            ) : (
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
                    {overview.recent_analyses.map((record) => (
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
            )}
          </section>
        </>
      )}
    </>
  )
}
