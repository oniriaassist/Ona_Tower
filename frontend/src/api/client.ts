import { errorMessage } from './errors';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`, init);
  } catch {
    throw new Error('Unable to reach the ONA Towers service. Please try again shortly.');
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(errorMessage(body, response.status));
  }

  return body as T;
}
