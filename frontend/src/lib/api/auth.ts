import { api, setTokens } from './client';

interface LoginResponse {
	access: string;
	refresh: string;
}

interface User {
	id: number;
	username: string;
	email: string;
}

export async function login(username: string, password: string): Promise<void> {
	const data = await api<LoginResponse>('/auth/login/', {
		method: 'POST',
		body: { username, password }
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
