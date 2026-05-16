import { api } from './client';

export interface TheoryCategory {
	id: string;
	title: string;
	description: string;
	concept_count: number;
}

export interface ConceptSummary {
	id: string;
	title: string;
	category: string;
	summary: string;
}

export interface ConceptDetail {
	id: string;
	title: string;
	category: string;
	aliases: string[];
	summary: string;
	content: string;
	related: string[];
}

export interface CategoriesResponse {
	categories: TheoryCategory[];
}

export interface ConceptsResponse {
	concepts: ConceptSummary[];
	count: number;
}

export interface ConceptDetailResponse {
	concept: ConceptDetail;
	related: ConceptSummary[];
}

export interface QueryMatchedResponse {
	matched: true;
	score: number;
	concept: ConceptDetail;
	related: ConceptSummary[];
	suggestions: ConceptSummary[];
}

export interface QueryUnmatchedResponse {
	matched: false;
	score: number;
	concept: null;
	related: [];
	suggestions: ConceptSummary[];
	message: string;
}

export type QueryResponse = QueryMatchedResponse | QueryUnmatchedResponse;

export function listCategories(): Promise<CategoriesResponse> {
	return api<CategoriesResponse>('/theory/categories/');
}

export function listConcepts(category?: string): Promise<ConceptsResponse> {
	const qs = category ? `?category=${encodeURIComponent(category)}` : '';
	return api<ConceptsResponse>(`/theory/concepts/${qs}`);
}

export function getConcept(conceptId: string): Promise<ConceptDetailResponse> {
	return api<ConceptDetailResponse>(`/theory/concepts/${encodeURIComponent(conceptId)}/`);
}

export function queryTheory(question: string): Promise<QueryResponse> {
	return api<QueryResponse>('/theory/query/', {
		method: 'POST',
		body: { question }
	});
}
