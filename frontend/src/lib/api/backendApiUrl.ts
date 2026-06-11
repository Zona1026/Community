const DEFAULT_BACKEND_API_URL = 'http://127.0.0.1:5000';

export function getBackendApiUrl(): string {
  const value = process.env.BACKEND_API_URL?.trim();

  return (value || DEFAULT_BACKEND_API_URL).replace(/\/$/, '');
}
