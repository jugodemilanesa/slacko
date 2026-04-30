import { writable } from 'svelte/store';

interface User {
	id: number;
	username: string;
	email: string;
}

export const user = writable<User | null>(null);
export const isLoggedIn = writable(false);
