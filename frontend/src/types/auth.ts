export type UserRole = 'admin' | 'user'

export interface UserInfo {
  username: string
  display_name: string
  role: UserRole
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface StoredSession {
  access_token: string
  user: UserInfo
}

export interface ApiKeyStatus {
  configured: boolean
  source: 'environment' | 'runtime_override'
  masked_key?: string | null
}

export interface ChangePasswordResponse {
  status: string
}
