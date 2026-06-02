import { writable } from 'svelte/store';

const browser = typeof window !== 'undefined';

const initialDark = browser
	? localStorage.getItem('theme') === 'dark' ||
	  (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
	: false;

export const isDarkMode = writable<boolean>(initialDark);

if (browser) {
	isDarkMode.subscribe((value) => {
		if (value) {
			document.documentElement.classList.add('dark');
			localStorage.setItem('theme', 'dark');
		} else {
			document.documentElement.classList.remove('dark');
			localStorage.setItem('theme', 'light');
		}
	});
}

export function toggleDarkMode() {
	isDarkMode.update((current) => !current);
}
