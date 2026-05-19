export interface AbuseIPDBReport {
  reportedAt: string
  comment: string
  categories: number[]
  reporterId: number
  reporterCountryCode: string
  reporterCountryName: string
}

export interface AbuseIPDBResult {
  ipAddress: string
  isPublic: boolean
  ipVersion: number
  isWhitelisted: boolean | null
  abuseConfidenceScore: number
  countryCode: string | null
  countryName: string | null
  usageType: string | null
  isp: string | null
  domain: string | null
  hostnames: string[]
  isTor: boolean
  totalReports: number
  numDistinctUsers: number
  lastReportedAt: string | null
  reports: AbuseIPDBReport[]
}

export interface AbuseIPDBLookupResponse {
  ip: string
  result: AbuseIPDBResult
}