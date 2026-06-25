import { env } from '$env/dynamic/public';

// En dev, PUBLIC_API_BASE queda vacío y se usa el path relativo '/api' (Vite lo
// proxea al backend). En prod (frontend en Vercel, backend en Railway) se setea
// PUBLIC_API_BASE=https://<backend> y las requests van directo al backend.
const API_BASE = `${env.PUBLIC_API_BASE || ''}/api`;

interface RequestOptions {
	method?: string;
	body?: unknown;
	headers?: Record<string, string>;
	skipAuthRedirect?: boolean;
}

const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

/** Lee una cookie por nombre (para el token CSRF, que no es httpOnly). */
function getCookie(name: string): string | null {
	if (typeof document === 'undefined') return null;
	const match = document.cookie.match(new RegExp('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)'));
	return match ? decodeURIComponent(match[2]) : null;
}

let csrfReady: Promise<void> | null = null;

/** Pide la cookie csrftoken al backend una sola vez (idempotente). */
export function ensureCsrf(): Promise<void> {
	if (csrfReady) return csrfReady;
	csrfReady = fetch(`${API_BASE}/auth/csrf/`, { credentials: 'include' })
		.then(() => undefined)
		.catch(() => undefined);
	return csrfReady;
}

function translateError(msg: string): string {
	if (!msg) return '';
	const lower = msg.toLowerCase();
	if (
		lower.includes('no active account found') ||
		lower.includes('no se encontró ninguna cuenta activa')
	) {
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

	// Métodos no seguros: la auth por sesión exige el header X-CSRFToken.
	if (UNSAFE_METHODS.has(method.toUpperCase())) {
		if (!getCookie('csrftoken')) await ensureCsrf();
		const csrf = getCookie('csrftoken');
		if (csrf) headers['X-CSRFToken'] = csrf;
	}

	if (body) {
		headers['Content-Type'] = 'application/json';
	}

	const response = await fetch(`${API_BASE}${endpoint}`, {
		method,
		headers,
		// La cookie de sesión viaja en cada request.
		credentials: 'include',
		body: body ? JSON.stringify(body) : undefined
	});

	// Sin sesión válida el backend responde 401/403. Mandamos al login salvo
	// que el caller maneje el caso (ej. el chequeo de auth o el propio login).
	if ((response.status === 401 || response.status === 403) && !options.skipAuthRedirect) {
		if (typeof window !== 'undefined') {
			window.location.href = '/login';
		}
		throw new Error('No autorizado');
	}

	if (!response.ok) {
		const errorObj = await response.json().catch(() => null);
		const formattedError = errorObj ? formatApiError(errorObj) : '';
		throw new Error(formattedError || `Error ${response.status}`);
	}

	// 204 No Content (ej. logout) no trae body.
	if (response.status === 204) {
		return undefined as T;
	}
	return response.json();
}
