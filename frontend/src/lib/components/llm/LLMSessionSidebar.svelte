<script lang="ts">
	import { onMount } from 'svelte';

	import {
		listSessions,
		patchSession,
		deleteSession,
		type SessionSummary
	} from '$lib/api/chat';
	import { session as currentSession, openSession, reset, start } from '$lib/stores/llmChat';

	let {
		open = $bindable(false)
	}: {
		open?: boolean;
	} = $props();

	let sessions = $state<SessionSummary[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let showArchived = $state(false);

	async function refresh() {
		loading = true;
		error = null;
		try {
			const list = await listSessions({ archived: showArchived });
			// Only LLM-mode sessions in this sidebar.
			sessions = list.filter((s) => s.mode === 'llm');
		} catch (e) {
			error = e instanceof Error ? e.message : 'No pude cargar el historial.';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (open) {
			refresh();
		}
	});

	onMount(refresh);

	function isActive(id: string): boolean {
		return $currentSession?.id === id;
	}

	async function pick(id: string) {
		if (isActive(id)) {
			open = false;
			return;
		}
		open = false;
		await openSession(id);
	}

	async function newChat() {
		open = false;
		reset();
		await start();
		refresh();
	}

	async function togglePin(s: SessionSummary, e: Event) {
		e.stopPropagation();
		try {
			await patchSession(s.id, { pinned: !s.pinned });
			refresh();
		} catch {
			// silent — keep sidebar open
		}
	}

	async function toggleArchive(s: SessionSummary, e: Event) {
		e.stopPropagation();
		try {
			await patchSession(s.id, { archived: !s.archived });
			refresh();
		} catch {
			// silent
		}
	}

	async function remove(s: SessionSummary, e: Event) {
		e.stopPropagation();
		if (!confirm(`Eliminar este chat (${s.title || 'sin título'})? Es irreversible.`)) {
			return;
		}
		try {
			await deleteSession(s.id);
			if (isActive(s.id)) {
				reset();
				start();
			}
			refresh();
		} catch {
			// silent
		}
	}

	function fmtDate(iso: string): string {
		const d = new Date(iso);
		const now = new Date();
		const diffMs = now.getTime() - d.getTime();
		const diffMin = Math.floor(diffMs / 60000);
		if (diffMin < 1) return 'recién';
		if (diffMin < 60) return `${diffMin}m`;
		const diffH = Math.floor(diffMin / 60);
		if (diffH < 24) return `${diffH}h`;
		const diffDays = Math.floor(diffH / 24);
		if (diffDays < 7) return `${diffDays}d`;
		return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short' });
	}

	function handleEscape(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) open = false;
	}
</script>

<svelte:window onkeydown={handleEscape} />

{#if open}
	<div
		class="backdrop"
		role="button"
		tabindex="-1"
		aria-label="Cerrar"
		onclick={() => (open = false)}
		onkeydown={(e) => e.key === 'Enter' && (open = false)}
	></div>
{/if}

<aside class="sidebar" class:open aria-hidden={!open} aria-label="Historial de chats">
	<header class="head">
		<div>
			<div class="overline">Historial</div>
			<h2 class="title">Tus chats</h2>
		</div>
		<button type="button" class="close" onclick={() => (open = false)} aria-label="Cerrar">×</button>
	</header>

	<div class="controls">
		<button type="button" class="new-btn" onclick={newChat}>
			<span class="new-glyph">+</span>
			Nuevo chat
		</button>
		<label class="archived-toggle">
			<input type="checkbox" bind:checked={showArchived} onchange={refresh} />
			<span>Archivados</span>
		</label>
	</div>

	<div class="body">
		{#if loading}
			<div class="status">
				<span class="dot"></span><span class="dot"></span><span class="dot"></span>
			</div>
		{:else if error}
			<div class="err" role="alert">
				<div class="err-label">No se cargó</div>
				<div class="err-msg">{error}</div>
				<button type="button" class="retry" onclick={refresh}>Reintentar</button>
			</div>
		{:else if sessions.length === 0}
			<div class="empty">
				<div class="empty-glyph">∞</div>
				<p>
					{showArchived ? 'No hay chats archivados.' : 'Todavía no hay chats. Empezá uno y va a aparecer acá.'}
				</p>
			</div>
		{:else}
			<ul class="list">
				{#each sessions as s (s.id)}
					<li>
						<div
							role="button"
							tabindex="0"
							class="item"
							class:active={isActive(s.id)}
							class:pinned={s.pinned}
							onclick={() => pick(s.id)}
							onkeydown={(e) => {
								if (e.key === 'Enter' || e.key === ' ') {
									e.preventDefault();
									pick(s.id);
								}
							}}
						>
							<div class="item-head">
								<span class="item-title">{s.title || 'Sin título'}</span>
								{#if s.pinned}
									<span class="pin-mark" aria-hidden="true">★</span>
								{/if}
							</div>
							<div class="item-meta">
								<span class="when">{fmtDate(s.last_message_at)}</span>
								<span class="dot-sep" aria-hidden="true">·</span>
								<span class="id-frag">{s.id.slice(0, 6)}</span>
							</div>

							<div class="actions">
								<button
									type="button"
									class="act"
									onclick={(e) => togglePin(s, e)}
									title={s.pinned ? 'Despinear' : 'Pinear'}
								>
									{s.pinned ? '☆' : '★'}
								</button>
								<button
									type="button"
									class="act"
									onclick={(e) => toggleArchive(s, e)}
									title={s.archived ? 'Desarchivar' : 'Archivar'}
								>
									{s.archived ? '↑' : '↓'}
								</button>
								<button
									type="button"
									class="act danger"
									onclick={(e) => remove(s, e)}
									title="Eliminar"
								>
									×
								</button>
							</div>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</aside>

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(26, 26, 46, 0.4);
		backdrop-filter: blur(2px);
		-webkit-backdrop-filter: blur(2px);
		z-index: 70;
		border: none;
		cursor: pointer;
		animation: fadeIn 0.18s ease-out;
	}

	.sidebar {
		position: fixed;
		top: 0;
		left: 0;
		bottom: 0;
		width: min(360px, 92vw);
		background: var(--color-surface-card);
		border-right: 1px solid var(--color-bot-border);
		box-shadow: 28px 0 64px -28px rgba(26, 26, 46, 0.4);
		z-index: 71;
		display: flex;
		flex-direction: column;
		transform: translateX(-100%);
		transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
	}

	.sidebar.open {
		transform: translateX(0);
	}

	.head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		padding: 1.5rem 1.25rem 1rem 1.25rem;
		border-bottom: 1px dashed var(--color-bot-border);
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: 0.25rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: 1.55rem;
		color: var(--color-ink);
		margin: 0;
		line-height: 1;
	}

	.close {
		font-family: var(--font-display);
		font-size: 1.5rem;
		line-height: 1;
		background: transparent;
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink-muted);
		width: 32px;
		height: 32px;
		border-radius: 50%;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		transition: all 0.15s ease;
		flex-shrink: 0;
	}

	.close:hover {
		color: var(--color-error);
		border-color: var(--color-error);
	}

	.controls {
		padding: 0.85rem 1.25rem 0.6rem 1.25rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		border-bottom: 1px dashed var(--color-bot-border);
	}

	.new-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.95rem;
		border-radius: 999px;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		color: white;
		border: none;
		cursor: pointer;
		font-family: var(--font-body);
		font-size: 0.82rem;
		font-weight: 500;
		transition: transform 0.18s ease, box-shadow 0.18s ease;
	}

	.new-btn:hover {
		transform: translateY(-1px);
		box-shadow: 0 10px 22px -10px color-mix(in srgb, var(--color-primary) 60%, transparent);
	}

	.new-glyph {
		font-family: var(--font-mono);
		font-size: 1.05rem;
		line-height: 0.85;
	}

	.archived-toggle {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		cursor: pointer;
	}

	.archived-toggle input {
		accent-color: var(--color-accent);
	}

	.body {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem 0.75rem 1.5rem 0.75rem;
	}

	.body::-webkit-scrollbar {
		width: 6px;
	}
	.body::-webkit-scrollbar-thumb {
		background: var(--color-bot-border);
		border-radius: 3px;
	}

	.list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.item {
		position: relative;
		width: 100%;
		display: block;
		padding: 0.65rem 2.2rem 0.7rem 0.85rem;
		border-radius: 8px;
		background: transparent;
		border: 1px solid transparent;
		cursor: pointer;
		text-align: left;
		font-family: var(--font-body);
		transition: background 0.15s ease, border-color 0.15s ease;
	}

	.item:hover {
		background: var(--color-surface-warm);
	}

	.item.active {
		background: color-mix(in srgb, var(--color-primary) 8%, var(--color-surface-card));
		border-color: color-mix(in srgb, var(--color-primary) 30%, transparent);
	}

	.item.pinned::before {
		content: '';
		position: absolute;
		left: 0;
		top: 50%;
		transform: translateY(-50%);
		width: 3px;
		height: 60%;
		background: linear-gradient(180deg, var(--color-primary), var(--color-accent));
		border-radius: 0 2px 2px 0;
	}

	.item-head {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.2rem;
	}

	.item-title {
		font-size: 0.88rem;
		color: var(--color-ink);
		font-weight: 500;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		flex: 1;
		min-width: 0;
	}

	.pin-mark {
		font-family: var(--font-display);
		color: var(--color-accent);
		font-size: 0.85rem;
		line-height: 1;
	}

	.item-meta {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.1em;
		color: var(--color-ink-muted);
		text-transform: lowercase;
	}

	.dot-sep {
		opacity: 0.5;
	}

	.id-frag {
		opacity: 0.6;
	}

	.actions {
		position: absolute;
		right: 0.4rem;
		top: 50%;
		transform: translateY(-50%);
		display: flex;
		gap: 0.15rem;
		opacity: 0;
		transition: opacity 0.15s ease;
	}

	.item:hover .actions,
	.item:focus-within .actions {
		opacity: 1;
	}

	.act {
		width: 22px;
		height: 22px;
		border-radius: 4px;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink-muted);
		font-family: var(--font-display);
		font-size: 0.85rem;
		line-height: 1;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		transition: all 0.12s ease;
	}

	.act:hover {
		color: var(--color-primary);
		border-color: var(--color-primary);
	}

	.act.danger:hover {
		color: var(--color-error);
		border-color: var(--color-error);
	}

	/* Status / empty / error -------------------------------------------- */
	.status {
		display: flex;
		gap: 6px;
		padding: 1.2rem 0.85rem;
		justify-content: center;
	}

	.dot {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: var(--color-ink-muted);
		animation: bounce 1.2s infinite ease-in-out both;
	}
	.dot:nth-child(2) {
		animation-delay: 0.15s;
	}
	.dot:nth-child(3) {
		animation-delay: 0.3s;
	}

	.empty {
		padding: 2rem 1.25rem;
		text-align: center;
		color: var(--color-ink-muted);
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.9rem;
		line-height: 1.6;
	}

	.empty-glyph {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 2.5rem;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		opacity: 0.45;
		margin-bottom: 0.5rem;
	}

	.err {
		padding: 0.85rem 0.95rem;
		background: color-mix(in srgb, var(--color-error) 6%, transparent);
		border-left: 3px solid var(--color-error);
		border-radius: 0 6px 6px 0;
		margin: 0.5rem;
	}

	.err-label {
		font-family: var(--font-mono);
		font-size: 0.58rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-error);
		margin-bottom: 0.2rem;
	}

	.err-msg {
		font-size: 0.82rem;
		color: var(--color-ink);
		margin-bottom: 0.5rem;
	}

	.retry {
		font-family: var(--font-body);
		font-size: 0.72rem;
		padding: 0.3rem 0.7rem;
		border-radius: 999px;
		background: transparent;
		color: var(--color-error);
		border: 1px solid var(--color-error);
		cursor: pointer;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes bounce {
		0%,
		80%,
		100% {
			transform: scale(0.6);
			opacity: 0.4;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}
</style>
