import { API_BASE_URL } from './client';
import { getErrorMessage as parseError } from './errors';

export type AdminEnquiryStatus =
  | 'new'
  | 'contacted'
  | 'qualified'
  | 'viewing_scheduled'
  | 'closed'
  | 'archived';

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  role: string;
  department?: string | null;
  is_super_admin: boolean;
  active: boolean;
  last_login_at?: string | null;
  password_reset_requested_at?: string | null;
}

export interface AdminEnquiry {
  id: string;
  reference_number: string;
  name: string;
  phone: string;
  email?: string | null;
  residence_interest?: string | null;
  enquiry_type: string;
  message?: string | null;
  consent: boolean;
  source: string;
  status: AdminEnquiryStatus | string;
  assigned_to?: string | null;
  internal_notes?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface AnalyticsPoint { label: string; value: number }
export interface TopPage { path: string; visits: number }
export interface AdminAnalytics {
  total_visits_30_days: number;
  unique_sessions_30_days: number;
  daily: AnalyticsPoint[];
  monthly: AnalyticsPoint[];
  top_pages: TopPage[];
}

export interface AdminOverview {
  total_enquiries: number;
  new_enquiries: number;
  active_enquiries: number;
  closed_enquiries: number;
  enquiries_last_7_days: number;
  active_team_members: number;
  overdue_enquiries: number;
  recent_enquiries: AdminEnquiry[];
  settings: AdminWorkspaceSettings;
  analytics: AdminAnalytics;
}

export interface TeamMember extends AdminUser {
  created_at: string;
  updated_at: string;
}

export interface AdminWorkspaceSettings {
  project_name: string;
  sales_email?: string | null;
  sales_phone?: string | null;
  whatsapp_number?: string | null;
  response_sla_hours: number;
  timezone: string;
  customer_site_url: string;
  notifications_enabled: boolean;
}

export interface AdminSettingsRecord {
  settings: AdminWorkspaceSettings;
  updated_at?: string | null;
}

export interface EnquiryListResponse {
  items: AdminEnquiry[];
  total: number;
  page: number;
  page_size: number;
}

interface LoginResponse {
  token: string;
  token_type: string;
  expires_at: number;
  user: AdminUser;
}

const TOKEN_KEY = 'ona_admin_token';
const USER_KEY = 'ona_admin_user';

function storage() { return window.sessionStorage; }

function adminUrl(path: string, baseUrl = API_BASE_URL) {
  return `${baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
}

async function fetchAdmin(path: string, init: RequestInit = {}) {
  return fetch(adminUrl(path), init);
}

export function getAdminToken(): string {
  try { return storage().getItem(TOKEN_KEY) || ''; } catch { return ''; }
}

export function getStoredAdminUser(): AdminUser | null {
  try {
    const value = storage().getItem(USER_KEY);
    return value ? JSON.parse(value) as AdminUser : null;
  } catch { return null; }
}

function saveSession(body: LoginResponse) {
  try {
    storage().setItem(TOKEN_KEY, body.token);
    storage().setItem(USER_KEY, JSON.stringify(body.user));
  } catch {
    // Authentication still works for the current page if sessionStorage is restricted.
  }
}

export function clearAdminSession() {
  try {
    storage().removeItem(TOKEN_KEY);
    storage().removeItem(USER_KEY);
  } catch {
    // Session storage can be unavailable in privacy-restricted contexts.
  }
}

async function adminRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAdminToken();
  const headers = new Headers(init.headers || {});
  if (!headers.has('Content-Type') && init.body) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetchAdmin(path, { ...init, headers });
  } catch {
    throw new Error('Unable to reach the ONA administration service. Check that the API is running.');
  }
  if (response.status === 401) clearAdminSession();
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<T>;
}

export async function adminLogin(email: string, password: string) {
  let response: Response;
  try {
    response = await fetchAdmin('/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    throw new Error('Unable to reach the ONA administration service. Check that the API is running.');
  }
  if (!response.ok) throw new Error(await parseError(response));
  const body = await response.json() as LoginResponse;
  saveSession(body);
  return body;
}

export async function requestPasswordReset(email: string) {
  let response: Response;
  try {
    response = await fetchAdmin('/admin/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });
  } catch {
    throw new Error('Unable to reach the ONA administration service. Check that the API is running.');
  }
  if (!response.ok) throw new Error(await parseError(response));
  return response.json() as Promise<{ success: boolean; message: string }>;
}

export function verifyAdminSession() {
  return adminRequest<{ user: AdminUser }>('/admin/me');
}

export async function updateMyProfile(payload: { name: string; email: string; phone?: string | null }) {
  const body = await adminRequest<LoginResponse>('/admin/profile', {
    method: 'PATCH', body: JSON.stringify(payload),
  });
  saveSession(body);
  return body.user;
}

export function changeMyPassword(payload: { current_password: string; new_password: string; confirm_password: string }) {
  return adminRequest<{ success: boolean; message: string }>('/admin/security/password', {
    method: 'POST', body: JSON.stringify(payload),
  });
}

export function getAdminOverview() { return adminRequest<AdminOverview>('/admin/overview'); }

export function getAdminEnquiries(params: { search?: string; status?: string; page?: number; pageSize?: number } = {}) {
  const query = new URLSearchParams();
  if (params.search) query.set('search', params.search);
  if (params.status && params.status !== 'all') query.set('status', params.status);
  query.set('page', String(params.page || 1));
  query.set('page_size', String(params.pageSize || 25));
  return adminRequest<EnquiryListResponse>(`/admin/enquiries?${query.toString()}`);
}

export function updateAdminEnquiry(
  id: string,
  payload: Partial<Pick<AdminEnquiry, 'status' | 'assigned_to' | 'internal_notes'>>,
) {
  return adminRequest<AdminEnquiry>(`/admin/enquiries/${encodeURIComponent(id)}`, {
    method: 'PATCH', body: JSON.stringify(payload),
  });
}

export function getTeam(includeInactive = true) {
  return adminRequest<TeamMember[]>(`/admin/team?include_inactive=${includeInactive ? 'true' : 'false'}`);
}

export function createTeamMember(payload: {
  name: string;
  email: string;
  password: string;
  phone?: string | null;
  role: string;
  department?: string | null;
  is_super_admin?: boolean;
  active?: boolean;
}) {
  return adminRequest<TeamMember>('/admin/team', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateTeamMember(
  id: string,
  payload: Partial<Pick<TeamMember, 'name' | 'email' | 'phone' | 'role' | 'department' | 'is_super_admin' | 'active'>>,
) {
  return adminRequest<TeamMember>(`/admin/team/${encodeURIComponent(id)}`, {
    method: 'PATCH', body: JSON.stringify(payload),
  });
}

export function resetTeamPassword(id: string, newPassword: string) {
  return adminRequest<{ success: boolean; message: string }>(`/admin/team/${encodeURIComponent(id)}/reset-password`, {
    method: 'POST', body: JSON.stringify({ new_password: newPassword }),
  });
}

export function deactivateTeamMember(id: string) {
  return adminRequest<{ success: boolean; message: string }>(`/admin/team/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });
}

export function getAdminSettings() { return adminRequest<AdminSettingsRecord>('/admin/settings'); }

export function updateAdminSettings(settings: AdminWorkspaceSettings) {
  return adminRequest<AdminSettingsRecord>('/admin/settings', {
    method: 'PATCH', body: JSON.stringify(settings),
  });
}
