import { writable } from 'svelte/store';
import type { ConceptDetail, ConceptSummary, QueryResponse } from '$lib/api/theory';

export interface QueryHistoryEntry {
	id: string;
	question: string;
	matchedTitle: string | null;
	matchedConceptId: string | null;
	timestamp: number;
}

export type TheoryTurn =
	| {
			id: string;
			kind: 'query';
			question: string;
			response: QueryResponse;
			timestamp: number;
	  }
	| {
			id: string;
			kind: 'concept';
			concept: ConceptDetail;
			related: ConceptSummary[];
			fromConceptId?: string | null;
			timestamp: number;
	  };

export const turns = writable<TheoryTurn[]>([]);
export const lastQuery = writable<string>('');
export const isLoading = writable<boolean>(false);
export const queryError = writable<string | null>(null);
export const queryHistory = writable<QueryHistoryEntry[]>([]);

const MAX_HISTORY = 10;

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

export function pushQueryTurn(question: string, response: QueryResponse) {
	turns.update((items) => [
		...items,
		{
			id: genId(),
			kind: 'query',
			question,
			response,
			timestamp: Date.now()
		}
	]);
}

export function pushConceptTurn(
	concept: ConceptDetail,
	related: ConceptSummary[],
	fromConceptId: string | null = null
) {
	turns.update((items) => [
		...items,
		{
			id: genId(),
			kind: 'concept',
			concept,
			related,
			fromConceptId,
			timestamp: Date.now()
		}
	]);
}

export function clearTheory() {
	turns.set([]);
	lastQuery.set('');
	isLoading.set(false);
	queryError.set(null);
	queryHistory.set([]);
}
