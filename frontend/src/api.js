const DEFAULT_API_BASE_URL =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:5000`
    : 'http://127.0.0.1:5000';

export const API_BASE_URL = import.meta.env.VITE_API_URL || DEFAULT_API_BASE_URL;

export function apiUrl(path) {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
}

export function apiFetch(path, options = {}) {
  const { headers, credentials, ...rest } = options;

  return fetch(apiUrl(path), {
    credentials: credentials || 'include',
    headers: {
      ...headers,
    },
    ...rest,
  });
}