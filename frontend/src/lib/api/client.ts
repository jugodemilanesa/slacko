const API_BASE = '/api';

interface RequestOptions {
	method?: string;
	body?: unknown;
	headers?: Record<string, string>;
	skipAuthRedirect?: boolean;
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

function translateError(msg: string): string {
	if (!msg) return '';
	const lower = msg.toLowerCase();
	if (lower.includes('no active account found') || lower.includes('no se encontró ninguna cuenta activa')) {
		return 'Usuario o contraseña incorrectos.';
	}
	return msg;
}

function formatApiError(errorObj: any): string {
	if (!errorObj) return '';
	if (typeof errorObj === 'string') return translateError(errorObj);
	
	if (errorObj.detail) {
		if (typeof errorObj.detail === 'string') {
			return translateError(errorObj.detail);
		}
		if (Array.isArray(errorObj.detail)) {
			return errorObj.detail.map(translateError).join(' ');
		}
	}

	const messages: string[] = [];
	for (const key of Object.keys(errorObj)) {
		if (key === 'detail') continue;
		
		const val = errorObj[key];
		let fieldName = key;
		
		if (key === 'username') fieldName = 'Usuario';
		else if (key === 'password') fieldName = 'Contraseña';
		else if (key === 'email') fieldName = 'Email';
		else if (key === 'non_field_errors') fieldName = '';

		const prefix = fieldName ? `${fieldName}: ` : '';
		
		if (Array.isArray(val)) {
			messages.push(`${prefix}${val.map(translateError).join(' ')}`);
		} else if (typeof val === 'string') {
			messages.push(`${prefix}${translateError(val)}`);
		} else if (typeof val === 'object') {
			messages.push(`${prefix}${JSON.stringify(val)}`);
		}
	}

	if (messages.length > 0) {
		return messages.join('\n');
	}
	
	return '';
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
		if (!options.skipAuthRedirect) {
			window.location.href = '/login';
			throw new Error('No autorizado');
		}
	}

	if (!response.ok) {
		const errorObj = await response.json().catch(() => null);
		const formattedError = errorObj ? formatApiError(errorObj) : '';
		throw new Error(formattedError || `Error ${response.status}`);
	}

	return response.json();
}
