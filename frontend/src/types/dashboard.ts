import type { AnalysisRecord } from './analysis'

export type QuickLinkTab = 'dashboard' | 'news' | 'hibp' | 'file' | 'url' | 'indicator' | 'admin'

export interface QuickLink {
  label: string
  tab: QuickLinkTab
  description: string
}

export interface CountPoint {
  label: string
  count: number
}

export interface DashboardOverview {
  total_analyses: number
  suspicious_count: number
  not_suspicious_count: number
  unknown_count: number
  analyses_by_type: Record<string, number>
  analyses_over_time_day: CountPoint[]
  analyses_over_time_week: CountPoint[]
  verdict_distribution: CountPoint[]
  recent_analyses: AnalysisRecord[]
  quick_links: QuickLink[]
}
