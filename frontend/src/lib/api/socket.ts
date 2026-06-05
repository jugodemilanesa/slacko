/**
 * Cliente WebSocket para el chat en vivo con el orquestador.
 *
 * El backend autentica por la cookie de sesión de Django (AuthMiddlewareStack
 * de Channels) — el browser la manda sola en el handshake, sin token en la URL.
 * El protocolo de mensajes es JSON sin
 * streaming intermedio: el cliente manda `{ message: string }` y el servidor
 * responde con un único `{ type: "message", role, content, metadata,
 * tool_calls, citations }` por turno (o `{ type: "error", ... }`).
 *
 * Esta función expone una API minimalista (`send`, `close`) y maneja:
 *   - reconexión con backoff exponencial (3 reintentos: 1s, 2s, 4s)
 *   - cleanup determinístico (cierra el socket viejo antes de reintentar)
 *   - parsing robusto del JSON entrante
 */

import type { ChatToolCall } from './chat';

export interface InboundMessage {
	type: 'message';
	role: 'assistant';
	content: string;
	metadata: { provider?: string; error?: string; [k: string]: unknown };
	tool_calls: ChatToolCall[];
	citations: string[];
}

export interface InboundError {
	type: 'error';
	message: string;
	details?: string;
}

export type Inbound = InboundMessage | InboundError;

export interface ChatSocketHandlers {
	onOpen?: () => void;
	onMessage: (msg: InboundMessage) => void;
	onError?: (err: InboundError | Event) => void;
	onClose?: (ev: CloseEvent) => void;
	onReconnecting?: (attempt: number, delayMs: number) => void;
}

export interface ChatSocket {
	send: (text: string) => void;
	close: () => void;
	readonly status: 'connecting' | 'open' | 'closed';
}

const MAX_RETRIES = 3;
const BACKOFF_MS = [1000, 2000, 4000];

function wsUrlFor(sessionId: string): string {
	// Vite proxies /ws/ to the backend in dev; in prod the same origin serves
	// both. Build the URL from the current page origin to inherit ws/wss. La
	// cookie de sesión autentica el handshake (mismo origin → el browser la manda).
	const proto = location.protocol === 'https:' ? 'wss' : 'ws';
	return `${proto}://${location.host}/ws/chat/${sessionId}/`;
}

export function connectChat(sessionId: string, handlers: ChatSocketHandlers): ChatSocket {
	let socket: WebSocket | null = null;
	let attempt = 0;
	let manuallyClosed = false;
	let status: ChatSocket['status'] = 'connecting';

	function open() {
		status = 'connecting';
		socket = new WebSocket(wsUrlFor(sessionId));

		socket.addEventListener('open', () => {
			attempt = 0;
			status = 'open';
			handlers.onOpen?.();
		});

		socket.addEventListener('message', (ev) => {
			let parsed: Inbound;
			try {
				parsed = JSON.parse(ev.data);
			} catch (err) {
				handlers.onError?.({
					type: 'error',
					message: 'Respuesta inválida del servidor.',
					details: String(err)
				});
				return;
			}
			if (parsed.type === 'error') {
				handlers.onError?.(parsed);
				return;
			}
			handlers.onMessage(parsed);
		});

		socket.addEventListener('error', (ev) => {
			handlers.onError?.(ev);
		});

		socket.addEventListener('close', (ev) => {
			status = 'closed';
			handlers.onClose?.(ev);
			if (manuallyClosed) return;
			if (attempt < MAX_RETRIES) {
				const delay = BACKOFF_MS[attempt];
				attempt += 1;
				handlers.onReconnecting?.(attempt, delay);
				setTimeout(() => {
					if (!manuallyClosed) open();
				}, delay);
			}
		});
	}

	open();

	return {
		send(text: string) {
			if (!socket || socket.readyState !== WebSocket.OPEN) {
				handlers.onError?.({
					type: 'error',
					message: 'No hay conexión con el servidor todavía.',
					details: `readyState=${socket?.readyState ?? 'null'}`
				});
				return;
			}
			socket.send(JSON.stringify({ message: text }));
		},
		close() {
			manuallyClosed = true;
			socket?.close();
		},
		get status() {
			return status;
		}
	};
}
