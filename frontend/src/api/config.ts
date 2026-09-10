const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export { API_BASE };

export function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...init,
    headers: {
      ...(init?.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}