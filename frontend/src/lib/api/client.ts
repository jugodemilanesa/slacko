const API_BASE = '/api';

interface RequestOptions {
	method?: string;
	body?: unknown;
	headers?: Record<string, string>;
}

function getToken(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem('access_token');
}

export function setTokens(access: string, refresh: string): void {
	localStorage.setItem('access_token', access);
	localStorage.setItem('refresh_token', refresh);
}

export function clearTokens(): void {
	localStorage.removeItem('access_token');
	localStorage.removeItem('refresh_token');
}

export function isAuthenticated(): boolean {
	return !!getToken();
}

export async function api<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
	const { method = 'GET', body, headers = {} } = options;

	const token = getToken();
	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	if (body) {
		headers['Content-Type'] = 'application/json';
	}

	const response = await fetch(`${API_BASE}${endpoint}`, {
		method,
		headers,
		body: body ? JSON.stringify(body) : undefined
	});

	if (response.status === 401) {
		clearTokens();
		window.location.href = '/login';
		throw new Error('No autorizado');
	}

	if (!response.ok) {
		const error = await response.json().catch(() => ({}));
		throw new Error(error.detail || `Error ${response.status}`);
	}

	return response.json();
}
