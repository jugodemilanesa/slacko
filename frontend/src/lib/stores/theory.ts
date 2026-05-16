import { writable } from 'svelte/store';
import type { ConceptDetail, ConceptSummary, QueryResponse } from '$lib/api/theory';

export interface QueryHistoryEntry {
	id: string;
	question: string;
	matchedTitle: string | null;
	matchedConceptId: string | null;
	timestamp: number;
}

export const lastQuery = writable<string>('');
export const lastResponse = writable<QueryResponse | null>(null);
export const selectedConcept = writable<ConceptDetail | null>(null);
export const selectedConceptRelated = writable<ConceptSummary[]>([]);
export const isLoading = writable<boolean>(false);
export const queryError = writable<string | null>(null);
export const queryHistory = writable<QueryHistoryEntry[]>([]);

const MAX_HISTORY = 5;

function genId() {
	return Math.random().toString(36).slice(2, 10);
}

export function pushHistory(question: string, response: QueryResponse) {
	const entry: QueryHistoryEntry = {
		id: genId(),
		question,
		matchedTitle: response.matched ? response.concept.title : null,
		matchedConceptId: response.matched ? response.concept.id : null,
		timestamp: Date.now()
	};
	queryHistory.update((items) => {
		const filtered = items.filter((it) => it.question.trim() !== question.trim());
		return [entry, ...filtered].slice(0, MAX_HISTORY);
	});
}

export function clearTheory() {
	lastQuery.set('');
	lastResponse.set(null);
	selectedConcept.set(null);
	selectedConceptRelated.set([]);
	isLoading.set(false);
	queryError.set(null);
	queryHistory.set([]);
}
