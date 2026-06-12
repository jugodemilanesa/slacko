import { writable } from 'svelte/store';

export const isShinyStore = writable<boolean>(false);

export function rollShiny() {
	isShinyStore.set(Math.random() < 0.01);
}
