export interface HibpBreach {
  name: string
  title: string
  domain?: string | null
  breach_date?: string | null
  added_date?: string | null
  modified_date?: string | null
  pwn_count?: number | null
  description: string
  data_classes: string[]
  logo_path?: string | null
  is_verified: boolean
  is_sensitive: boolean
  is_spam_list: boolean
  is_malware: boolean
  is_stealer_log: boolean
}

export interface HibpLookupResponse {
  email: string
  breached: boolean
  breaches: HibpBreach[]
  message: string
}
