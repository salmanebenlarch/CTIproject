import type { AdminOverview } from '../types/admin'
import type { AnalysisRecord, AnalysisResult } from '../types/analysis'
import type { ApiKeyStatus, ChangePasswordResponse, LoginResponse, UserInfo, UserRole } from '../types/auth'
import type { DashboardOverview } from '../types/dashboard'
import type { HibpLookupResponse } from '../types/hibp'
import type { NewsCategory, NewsStory } from '../types/news'
import type { AbuseIPDBLookupResponse } from '../types/abuseipdb'



const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

function authHeaders(token?: string): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = 'Request failed'
    try {
      const payload = await response.json()
      message = payload.detail ?? message
    } catch {
      // ignore
    }
    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}
export async function fetchAbuseIPDB(ip: string): Promise<AbuseIPDBLookupResponse> {
  const response = await fetch(
    `${API_BASE}/abuseipdb/check/${encodeURIComponent(ip)}`
  )
  return handleResponse<AbuseIPDBLookupResponse>(response)
}

export function getNewsImageUrl(storyId: number): string {
  return `${API_BASE}/news/${storyId}/image`
}

export async function analyzeUrl(url: string, token?: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/analyze/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ url }),
  })
  return handleResponse<AnalysisResult>(response)
}

export async function analyzeIndicator(value: string, token?: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE}/analyze/indicator`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ value }),
  })
  return handleResponse<AnalysisResult>(response)
}

export async function analyzeFile(file: File, token?: string): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_BASE}/analyze/file`, {
    method: 'POST',
    headers: authHeaders(token),
    body: formData,
  })
  return handleResponse<AnalysisResult>(response)
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  return handleResponse<LoginResponse>(response)
}

export async function logout(token?: string): Promise<void> {
  await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
    headers: authHeaders(token),
  })
}

export async function changePassword(
  token: string,
  currentPassword: string,
  newPassword: string,
): Promise<ChangePasswordResponse> {
  const response = await fetch(`${API_BASE}/auth/change-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  })
  return handleResponse<ChangePasswordResponse>(response)
}

export async function fetchCurrentUser(token: string): Promise<UserInfo> {
  const response = await fetch(`${API_BASE}/auth/me`, {
    headers: authHeaders(token),
  })
  return handleResponse<UserInfo>(response)
}

export async function fetchDashboardOverview(token?: string): Promise<DashboardOverview> {
  const response = await fetch(`${API_BASE}/dashboard/overview`, {
    headers: authHeaders(token),
  })
  return handleResponse<DashboardOverview>(response)
}

export async function fetchTopNews(limit = 10, category: NewsCategory = 'all'): Promise<NewsStory[]> {
  const response = await fetch(`${API_BASE}/news/top?limit=${limit}&category=${category}`)
  return handleResponse<NewsStory[]>(response)
}

export async function fetchHIBPBreaches(email: string): Promise<HibpLookupResponse> {
  const response = await fetch(`${API_BASE}/hibp/breached-account?email=${encodeURIComponent(email)}`)
  return handleResponse<HibpLookupResponse>(response)
}

export async function fetchAdminOverview(token: string): Promise<AdminOverview> {
  const response = await fetch(`${API_BASE}/admin/overview`, {
    headers: authHeaders(token),
  })
  return handleResponse<AdminOverview>(response)
}

export async function createUser(
  token: string,
  payload: { username: string; password: string; display_name?: string; role: UserRole },
): Promise<UserInfo> {
  const response = await fetch(`${API_BASE}/admin/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(payload),
  })
  return handleResponse<UserInfo>(response)
}

export async function updateUserRole(
  token: string,
  username: string,
  role: UserRole,
): Promise<UserInfo> {
  const response = await fetch(`${API_BASE}/admin/users/${encodeURIComponent(username)}/role`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ role }),
  })
  return handleResponse<UserInfo>(response)
}

export async function deleteUser(token: string, username: string): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/admin/users/${encodeURIComponent(username)}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
  return handleResponse<{ status: string }>(response)
}

export async function fetchUserAnalyses(token: string, username: string): Promise<AnalysisRecord[]> {
  const response = await fetch(`${API_BASE}/admin/users/${encodeURIComponent(username)}/analyses`, {
    headers: authHeaders(token),
  })
  return handleResponse<AnalysisRecord[]>(response)
}

export async function updateRuntimeApiKey(token: string, apiKey: string): Promise<ApiKeyStatus> {
  const response = await fetch(`${API_BASE}/admin/api-key`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify({ api_key: apiKey }),
  })
  return handleResponse<ApiKeyStatus>(response)
}

export async function clearRuntimeApiKey(token: string): Promise<ApiKeyStatus> {
  const response = await fetch(`${API_BASE}/admin/api-key`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
  return handleResponse<ApiKeyStatus>(response)
}
