export type Verdict = 'suspicious' | 'not_suspicious' | 'unknown'
export type IndicatorType = 'file' | 'url' | 'ip' | 'domain' | 'hash'

export interface DetectionStats {
  harmless: number
  malicious: number
  suspicious: number
  undetected: number
  timeout: number
  failure?: number
}

export interface EngineDetection {
  engine_name: string
  category?: string | null
  result?: string | null
  method?: string | null
  engine_version?: string | null
  engine_update?: string | null
}

export interface AnalysisMetadata {
  source: string
  vt_object_type?: string | null
  vt_id?: string | null
  permalink?: string | null
  reputation?: number | null
  categories: Record<string, string>
  tags: string[]
  total_votes: Record<string, number>
  title?: string | null
  last_final_url?: string | null
  http_status?: number | null
  file_name?: string | null
  file_size?: number | null
  type_description?: string | null
  type_tag?: string | null
  popular_threat_name?: string | null
  popular_threat_category?: string | null
}

export interface AnalysisResult {
  input_value: string
  indicator_type: IndicatorType
  verdict: Verdict
  summary: string
  detection_stats: DetectionStats
  engines: EngineDetection[]
  metadata: AnalysisMetadata
  raw_status?: string | null
  queued: boolean
}

export interface AnalysisRecord {
  id: string
  input_value: string
  indicator_type: IndicatorType
  verdict: Verdict
  username?: string | null
  created_at: string
  raw_status?: string | null
}
