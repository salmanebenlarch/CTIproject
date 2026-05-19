import type { AnalysisRecord } from './analysis'
import type { ApiKeyStatus, UserInfo } from './auth'

export interface AdminOverview {
  api_key_status: ApiKeyStatus
  users: UserInfo[]
  analyses: AnalysisRecord[]
  analysis_counts_by_user: Record<string, number>
}
