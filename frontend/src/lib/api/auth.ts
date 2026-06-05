import { env } from '$env/dynamic/public';
import { api, setTokens, clearTokens } from './client';

interface LoginResponse {
	access: string;
	refresh: string;
	// Solo presentes en el login con Google (los agrega GoogleLogin en el backend).
	created?: boolean;
	linked_existing?: boolean;
}

export interface GoogleLoginResult {
	/** El login con Google se conectó a una cuenta local que ya existía con ese email. */
	linkedExisting: boolean;
	/** El login con Google creó una cuenta nueva. */
	created: boolean;
}

interface User {
	id: number;
	username: string;
	email: string;
}

export async function login(username: string, password: string): Promise<void> {
	const data = await api<LoginResponse>('/auth/login/', {
		method: 'POST',
		body: { username, password },
		skipAuthRedirect: true
	});
	setTokens(data.access, data.refresh);
}

export async function register(
	username: string,
	email: string,
	password: string
): Promise<void> {
	await api('/auth/register/', {
		method: 'POST',
		body: { username, email, password }
	});
	await login(username, password);
}

export async function getMe(): Promise<User> {
	return api<User>('/auth/me/');
}

export async function logout(): Promise<void> {
	const refresh = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
	if (refresh) {
		// Blacklistea el refresh en el backend; si falla igual limpiamos local.
		await api('/auth/logout/', {
			method: 'POST',
			body: { refresh },
			skipAuthRedirect: true
		}).catch(() => {});
	}
	clearTokens();
}

// ─── Google OAuth — flujo access_token vía Google Identity Services ────────
//
// Usamos el token client de GIS (popup, sin redirect URI ni client_secret): el
// browser obtiene un access_token y lo mandamos al backend, que con allauth
// resuelve el perfil del usuario (``_fetch_user_info``) y devuelve el par JWT.
// Configurar es mínimo: en Google Cloud Console alcanza con crear un OAuth
// Client ID (Web) y autorizar el origin http://localhost:5173.

const GIS_SRC = 'https://accounts.google.com/gsi/client';

interface TokenResponse {
	access_token?: string;
	error?: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const google: any;

let gisLoader: Promise<void> | null = null;

function loadGis(): Promise<void> {
	if (typeof window === 'undefined') return Promise.reject(new Error('GIS solo en browser'));
	if (gisLoader) return gisLoader;
	gisLoader = new Promise<void>((resolve, reject) => {
		if (typeof google !== 'undefined' && google?.accounts?.oauth2) return resolve();
		const script = document.createElement('script');
		script.src = GIS_SRC;
		script.async = true;
		script.defer = true;
		script.onload = () => resolve();
		script.onerror = () => reject(new Error('No se pudo cargar Google Identity Services.'));
		document.head.appendChild(script);
	});
	return gisLoader;
}

export function isGoogleConfigured(): boolean {
	return !!env.PUBLIC_GOOGLE_OAUTH_CLIENT_ID;
}

/** Precarga el SDK de GIS para que el popup salga sin demora al hacer click. */
export function preloadGoogle(): void {
	if (isGoogleConfigured()) loadGis().catch(() => {});
}

/** Abre el popup de Google, obtiene un access_token y lo canjea por JWT. */
export async function loginWithGoogle(): Promise<GoogleLoginResult> {
	const clientId = env.PUBLIC_GOOGLE_OAUTH_CLIENT_ID;
	if (!clientId) {
		throw new Error(
			'El login con Google no está configurado todavía. Probá con usuario y contraseña.'
		);
	}
	await loadGis();

	const accessToken = await new Promise<string>((resolve, reject) => {
		const client = google.accounts.oauth2.initTokenClient({
			client_id: clientId,
			scope: 'openid email profile',
			callback: (resp: TokenResponse) => {
				if (resp?.access_token) resolve(resp.access_token);
				else reject(new Error('No pudimos obtener el acceso de Google.'));
			},
			error_callback: (err: { type?: string }) => {
				const cancelled = err?.type === 'popup_closed' || err?.type === 'popup_failed_to_open';
				reject(new Error(cancelled ? 'Cancelaste el acceso con Google.' : 'Falló el acceso con Google.'));
			}
		});
		client.requestAccessToken();
	});

	const data = await api<LoginResponse>('/auth/google/', {
		method: 'POST',
		body: { access_token: accessToken },
		skipAuthRedirect: true
	});
	setTokens(data.access, data.refresh);
	return { linkedExisting: !!data.linked_existing, created: !!data.created };
}
