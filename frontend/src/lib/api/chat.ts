/**
 * REST client para las sesiones de chat y sus mensajes.
 *
 * Endpoints (todos requieren `Authorization: Bearer <jwt>`):
 *   GET    /api/chat/sessions/?archived=...
 *   POST   /api/chat/sessions/
 *   GET    /api/chat/sessions/<uuid>/
 *   PATCH  /api/chat/sessions/<uuid>/
 *   DELETE /api/chat/sessions/<uuid>/
 *   GET    /api/chat/sessions/<uuid>/messages/
 *   GET    /api/chat/sessions/search/?q=...
 *
 * El chat en vivo no pasa por acá — usa el WebSocket en `lib/api/socket.ts`.
 * Estos endpoints sirven para listar/buscar el historial y crear la sesión
 * antes de abrir el socket.
 */

import { api } from './client';

export type SessionMode = 'guided' | 'free' | 'llm' | '';

export interface SessionSummary {
	id: string;
	title: string;
	mode: SessionMode;
	state: string;
	archived: boolean;
	pinned: boolean;
	tags: string[];
	created_at: string;
	updated_at: string;
	last_message_at: string;
}

export interface ChatToolCall {
	name: string;
	arguments: string; // JSON string with the tool args
	result_summary: string;
}

export interface Message {
	id: string;
	role: 'user' | 'assistant' | 'system';
	content: string;
	metadata: Record<string, unknown>;
	tool_calls: ChatToolCall[];
	citations: string[];
	cost_tokens: number;
	created_at: string;
}

export interface SessionDetail extends SessionSummary {
	model_data: Record<string, unknown>;
	messages: Message[];
}

export interface CreateSessionInput {
	mode?: SessionMode;
	title?: string;
}

export interface UpdateSessionInput {
	title?: string;
	archived?: boolean;
	pinned?: boolean;
	tags?: string[];
}

export interface SearchResponse {
	sessions: SessionSummary[];
	messages: Array<{
		id: string;
		session_id: string;
		role: string;
		content: string;
		created_at: string;
	}>;
}

export function listSessions(opts: { archived?: boolean } = {}): Promise<SessionSummary[]> {
	const qs = opts.archived !== undefined ? `?archived=${opts.archived}` : '';
	return api<SessionSummary[]>(`/chat/sessions/${qs}`);
}

export function createSession(input: CreateSessionInput = {}): Promise<SessionSummary> {
	return api<SessionSummary>('/chat/sessions/', {
		method: 'POST',
		body: input
	});
}

export function getSession(id: string): Promise<SessionDetail> {
	return api<SessionDetail>(`/chat/sessions/${encodeURIComponent(id)}/`);
}

export function patchSession(id: string, patch: UpdateSessionInput): Promise<SessionSummary> {
	return api<SessionSummary>(`/chat/sessions/${encodeURIComponent(id)}/`, {
		method: 'PATCH',
		body: patch
	});
}

export function deleteSession(id: string): Promise<void> {
	return api<void>(`/chat/sessions/${encodeURIComponent(id)}/`, { method: 'DELETE' });
}

export function listSessionMessages(id: string): Promise<Message[]> {
	return api<Message[]>(`/chat/sessions/${encodeURIComponent(id)}/messages/`);
}

export function searchSessions(q: string): Promise<SearchResponse> {
	const qs = `?q=${encodeURIComponent(q)}`;
	return api<SearchResponse>(`/chat/sessions/search/${qs}`);
}
