/**
 * Store del modo "Chat con Slacko (LLM)".
 *
 * Mantiene el estado de UNA conversación en vivo: la sesión activa, los
 * turnos, el status del socket, y los errores. Es independiente del store
 * `chat.ts` (que gobierna el modo guiado determinístico) para no mezclar
 * vocabularios.
 *
 * Persistencia: el id de la sesión se cachea en localStorage bajo
 * `slacko.llmSession`. Al volver al chat, si la sesión sigue accesible se
 * re-abre; si no (404, sesión borrada), arrancamos una nueva.
 */

import { writable, derived, get } from 'svelte/store';

import {
	createSession,
	getSession,
	type Message,
	type SessionSummary
} from '$lib/api/chat';
import { connectChat, type ChatSocket, type InboundError } from '$lib/api/socket';

const STORAGE_KEY = 'slacko.llmSession';

export type LLMStatus =
	| 'idle'         // no socket yet
	| 'connecting'   // socket opening
	| 'open'         // socket ready, no request in flight
	| 'thinking'     // user message sent, awaiting assistant turn
	| 'reconnecting' // backoff retry
	| 'error';

export interface LLMChatMessage {
	id: string;
	role: 'user' | 'assistant';
	content: string;
	provider?: string;
	model?: string;
	toolCalls?: Message['tool_calls'];
	citations?: string[];
	error?: string;
	createdAt: string;
	animate?: boolean;
}

export const session = writable<SessionSummary | null>(null);
export const messages = writable<LLMChatMessage[]>([]);
export const status = writable<LLMStatus>('idle');
export const lastError = writable<string | null>(null);

export const isThinking = derived(status, ($s) => $s === 'thinking');
export const isLive = derived(status, ($s) => $s === 'open' || $s === 'thinking');

let socket: ChatSocket | null = null;

function genId(): string {
	return Math.random().toString(36).slice(2, 10);
}

function loadCachedSessionId(): string | null {
	if (typeof window === 'undefined') return null;
	return window.localStorage.getItem(STORAGE_KEY);
}

function cacheSessionId(id: string | null) {
	if (typeof window === 'undefined') return;
	if (id) window.localStorage.setItem(STORAGE_KEY, id);
	else window.localStorage.removeItem(STORAGE_KEY);
}

function getAccessToken(): string | null {
	if (typeof window === 'undefined') return null;
	return window.localStorage.getItem('access_token');
}

function fromDb(m: Message): LLMChatMessage {
	if (m.role === 'system') {
		// We skip system messages in the rendered transcript.
		return {
			id: m.id,
			role: 'assistant',
			content: m.content,
			createdAt: m.created_at
		};
	}
	return {
		id: m.id,
		role: m.role,
		content: m.content,
		provider: (m.metadata?.provider as string | undefined) ?? undefined,
		model: (m.metadata?.model as string | undefined) ?? undefined,
		toolCalls: m.tool_calls,
		citations: m.citations,
		error: (m.metadata?.error as string | undefined) ?? undefined,
		createdAt: m.created_at
	};
}

/**
 * Abre el modo LLM: o re-abre la sesión cacheada, o crea una nueva.
 * Idempotente — llamar dos veces no duplica sockets.
 */
export async function start(): Promise<void> {
	if (socket) return; // already connected

	status.set('connecting');
	lastError.set(null);

	const token = getAccessToken();
	if (!token) {
		status.set('error');
		lastError.set('No estás autenticado. Volvé a iniciar sesión.');
		return;
	}

	let active: SessionSummary | null = null;
	const cached = loadCachedSessionId();

	if (cached) {
		try {
			const detail = await getSession(cached);
			active = detail;
			messages.set(detail.messages.filter((m) => m.role !== 'system').map(fromDb));
		} catch {
			// Cached session gone or inaccessible — drop the cache and create fresh.
			cacheSessionId(null);
		}
	}

	if (!active) {
		try {
			active = await createSession({
				mode: 'llm',
				title: `Chat ${new Date().toLocaleDateString('es-AR')}`
			});
			messages.set([]);
		} catch (err) {
			status.set('error');
			lastError.set(
				err instanceof Error
					? err.message
					: 'No pude crear una sesión nueva con el servidor.'
			);
			return;
		}
	}

	session.set(active);
	cacheSessionId(active.id);

	socket = connectChat(active.id, token, {
		onOpen: () => status.set('open'),
		onMessage: (msg) => {
			messages.update((arr) => [
				...arr,
				{
					id: genId(),
					role: 'assistant',
					content: msg.content,
					provider: msg.metadata?.provider,
					model: msg.metadata?.model,
					toolCalls: msg.tool_calls,
					citations: msg.citations,
					error: msg.metadata?.error as string | undefined,
					createdAt: new Date().toISOString(),
					animate: true
				}
			]);
			status.set('open');
		},
		onError: (err) => {
			const message =
				(err as InboundError)?.message ??
				'Falla en la conexión con el servidor.';
			lastError.set(message);
		},
		onClose: () => {
			if (get(status) !== 'reconnecting') status.set('idle');
		},
		onReconnecting: (attempt, delayMs) => {
			status.set('reconnecting');
			lastError.set(
				`Reintentando conexión (intento ${attempt}/3, esperando ${delayMs / 1000}s)…`
			);
		}
	});
}

export function send(text: string): void {
	const trimmed = text.trim();
	if (!trimmed) return;
	if (!socket) {
		lastError.set('La conexión todavía no está lista.');
		return;
	}
	const now = new Date().toISOString();
	messages.update((arr) => [
		...arr,
		{ id: genId(), role: 'user', content: trimmed, createdAt: now }
	]);
	status.set('thinking');
	socket.send(trimmed);
}

/**
 * Termina la sesión actual: cierra el socket y limpia el cache, pero NO
 * borra los mensajes del backend (siguen accesibles via /sessions/<id>/).
 */
export function reset(): void {
	socket?.close();
	socket = null;
	cacheSessionId(null);
	session.set(null);
	messages.set([]);
	status.set('idle');
	lastError.set(null);
}

/**
 * Carga otra sesión existente (útil para el historial del sidebar de Fase 5).
 */
export async function openSession(id: string): Promise<void> {
	reset();
	cacheSessionId(id);
	await start();
}
