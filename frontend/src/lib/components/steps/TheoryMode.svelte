<script lang="ts">
	import { onMount, tick } from 'svelte';
	import {
		queryTheory,
		getConcept,
		listCategories,
		type TheoryCategory
	} from '$lib/api/theory';
	import {
		lastQuery,
		isLoading,
		queryError,
		queryHistory,
		turns,
		pushHistory,
		pushQueryTurn,
		pushConceptTurn,
		clearTheory
	} from '$lib/stores/theory';
	import { resetChat } from '$lib/stores/chat';

	import TheorySearch from '$lib/components/theory/TheorySearch.svelte';
	import ConceptCard from '$lib/components/theory/ConceptCard.svelte';
	import EmptyResult from '$lib/components/theory/EmptyResult.svelte';
	import CategoryBrowser from '$lib/components/theory/CategoryBrowser.svelte';
	import SlakingAvatar from '$lib/components/SlakingAvatar.svelte';

	import type { Expression } from '$lib/stores/chat';

	let question = $state('');
	let categories = $state<TheoryCategory[]>([]);
	let stackEl = $state<HTMLDivElement | null>(null);

	onMount(async () => {
		try {
			const res = await listCategories();
			categories = res.categories;
		} catch {
			// silent — browser still works
		}
	});

	function categoryTitle(catId: string): string {
		return categories.find((c) => c.id === catId)?.title ?? catId.replace(/-/g, ' ');
	}

	async function scrollToBottom() {
		await tick();
		if (stackEl) {
			stackEl.scrollTo({ top: stackEl.scrollHeight, behavior: 'smooth' });
		}
	}

	async function runQuery(q: string) {
		const trimmed = q.trim();
		if (!trimmed) return;
		isLoading.set(true);
		queryError.set(null);
		lastQuery.set(trimmed);
		question = '';
		await scrollToBottom();
		try {
			const [res] = await Promise.all([
				queryTheory(trimmed),
				new Promise((r) => setTimeout(r, 450))
			]);
			pushQueryTurn(trimmed, res);
			pushHistory(trimmed, res);
			await scrollToBottom();
		} catch (e) {
			queryError.set(e instanceof Error ? e.message : 'Error al buscar');
		} finally {
			isLoading.set(false);
		}
	}

	async function openConcept(id: string, fromId: string | null = null) {
		isLoading.set(true);
		queryError.set(null);
		await scrollToBottom();
		try {
			const [res] = await Promise.all([
				getConcept(id),
				new Promise((r) => setTimeout(r, 300))
			]);
			pushConceptTurn(res.concept, res.related, fromId);
			await scrollToBottom();
		} catch (e) {
			queryError.set(e instanceof Error ? e.message : 'Error al cargar concepto');
		} finally {
			isLoading.set(false);
		}
	}

	function backToStart() {
		clearTheory();
		resetChat();
	}

	const hasTurns = $derived($turns.length > 0);

	const slakingExpression: Expression = $derived.by(() => {
		if ($isLoading) return 'thinking';
		if ($queryError) return 'sad';
		if (!hasTurns) return 'happy';
		const last = $turns[$turns.length - 1];
		if (last.kind === 'query' && !last.response.matched) return 'sad';
		return 'explain';
	});

	const slakingMessage = $derived.by(() => {
		if ($isLoading) return 'Estoy buscando en la bibliografía…';
		if ($queryError) return 'Algo salió mal con la búsqueda.';
		if (!hasTurns) return '¿Sobre qué tema querés repasar?';
		const last = $turns[$turns.length - 1];
		if (last.kind === 'query' && !last.response.matched) {
			return 'No encontré exactamente eso. Probá con otra forma o explorá las sugerencias.';
		}
		return 'Seguí preguntando o explorá los conceptos relacionados.';
	});

	function formatTime(ts: number): string {
		const d = new Date(ts);
		return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}
</script>

<div class="theory-mode">
	<div class="content">
		<div class="slacko-strip" role="status" aria-live="polite">
			<SlakingAvatar expression={slakingExpression} size="lg" ring floating />
			<div class="slacko-bubble">
				{slakingMessage}
			</div>
			{#if hasTurns}
				<button type="button" class="clear-btn" onclick={() => clearTheory()}>
					Limpiar chat
				</button>
			{/if}
		</div>

		<div class="chat-stack" bind:this={stackEl} aria-live="polite">
			{#if !hasTurns}
				<div class="prompt-empty">
					<div class="ornament-row" aria-hidden="true">
						<span class="dot"></span>
						<span class="line"></span>
						<span class="diamond">◆</span>
						<span class="line"></span>
						<span class="dot"></span>
					</div>
					<p class="prompt-msg">
						Escribí una pregunta abajo o explorá el temario por categoría.
					</p>
				</div>
			{:else}
				{#each $turns as turn (turn.id)}
					{#if turn.kind === 'query'}
						<div class="turn user-turn">
							<div class="bubble user-bubble">
								<div class="meta">
									<span class="meta-label">Vos</span>
									<span class="meta-time">{formatTime(turn.timestamp)}</span>
								</div>
								<p class="user-text">{turn.question}</p>
							</div>
						</div>
						<div class="turn bot-turn">
							<div class="bot-avatar">
								<SlakingAvatar
									expression={turn.response.matched ? 'explain' : 'sad'}
									size="sm"
								/>
							</div>
							<div class="bot-body">
								{#if turn.response.matched}
									<ConceptCard
										concept={turn.response.concept}
										related={turn.response.related}
										categoryTitle={categoryTitle(turn.response.concept.category)}
										onSelectRelated={(id) => openConcept(id, turn.response.matched ? turn.response.concept.id : null)}
									/>
								{:else}
									<EmptyResult
										message={turn.response.message}
										suggestions={turn.response.suggestions}
										question={turn.question}
										onSelect={(id) => openConcept(id, null)}
									/>
								{/if}
							</div>
						</div>
					{:else}
						<div class="turn user-turn">
							<div class="bubble user-bubble subtle">
								<div class="meta">
									<span class="meta-label">Vos</span>
									<span class="meta-time">{formatTime(turn.timestamp)}</span>
								</div>
								<p class="user-text">Quiero ver: <strong>{turn.concept.title}</strong></p>
							</div>
						</div>
						<div class="turn bot-turn">
							<div class="bot-avatar">
								<SlakingAvatar expression="explain" size="sm" />
							</div>
							<div class="bot-body">
								<ConceptCard
									concept={turn.concept}
									related={turn.related}
									categoryTitle={categoryTitle(turn.concept.category)}
									onSelectRelated={(id) => openConcept(id, turn.concept.id)}
								/>
							</div>
						</div>
					{/if}
				{/each}

				{#if $isLoading}
					<div class="turn bot-turn">
						<div class="bot-avatar">
							<SlakingAvatar expression="thinking" size="sm" />
						</div>
						<div class="bot-body">
							<div class="typing">
								<span></span><span></span><span></span>
							</div>
						</div>
					</div>
				{/if}
			{/if}
		</div>

		{#if $queryError}
			<div class="error-banner">
				<span class="error-label">Algo falló:</span> {$queryError}
			</div>
		{/if}

		<div class="composer">
			<TheorySearch
				bind:value={question}
				loading={$isLoading}
				onSubmit={runQuery}
			/>
		</div>

		<footer class="end-cta">
			<div class="end-rule" aria-hidden="true"></div>
			<button type="button" class="end-btn" onclick={backToStart}>
				← Volver al inicio
			</button>
			<p class="end-hint">¿Querés resolver un problema? Empezá un flujo nuevo.</p>
		</footer>
	</div>

	<aside class="side">
		<div class="side-inner">
			<CategoryBrowser onSelect={(id) => openConcept(id, null)} />
		</div>
	</aside>
</div>

<style>
	.theory-mode {
		display: grid;
		grid-template-columns: minmax(0, 1fr) 280px;
		gap: 2.5rem;
		max-width: 1180px;
		margin: 0 auto;
		padding: 2rem 1.5rem 4rem 1.5rem;
		align-items: start;
	}

	.content {
		min-width: 0;
		display: flex;
		flex-direction: column;
	}

	.slacko-strip {
		display: flex;
		align-items: center;
		gap: 0.9rem;
		margin-bottom: 1rem;
		padding: 0.75rem 1rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
	}

	.slacko-bubble {
		font-family: var(--font-display);
		font-size: 0.95rem;
		color: var(--color-ink);
		font-style: italic;
		line-height: 1.4;
		flex: 1;
	}

	.clear-btn {
		font-family: var(--font-body);
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		background: transparent;
		border: 1px solid var(--color-bot-border);
		padding: 0.35rem 0.7rem;
		border-radius: 999px;
		cursor: pointer;
		transition: all 0.15s ease;
		white-space: nowrap;
	}

	.clear-btn:hover {
		color: var(--color-error);
		border-color: var(--color-error);
	}

	.chat-stack {
		max-height: calc(100vh - 22rem);
		min-height: 320px;
		overflow-y: auto;
		padding: 0.5rem 0.25rem 1rem 0.25rem;
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
		scroll-behavior: smooth;
	}

	.chat-stack::-webkit-scrollbar {
		width: 8px;
	}
	.chat-stack::-webkit-scrollbar-track {
		background: transparent;
	}
	.chat-stack::-webkit-scrollbar-thumb {
		background: var(--color-bot-border);
		border-radius: 4px;
	}
	.chat-stack::-webkit-scrollbar-thumb:hover {
		background: var(--color-ink-muted);
	}

	.turn {
		display: flex;
		gap: 0.6rem;
		animation: fadeUp 0.25s ease-out;
	}

	.user-turn {
		justify-content: flex-end;
	}

	.bot-turn {
		align-items: flex-start;
	}

	.bot-avatar {
		flex-shrink: 0;
		padding-top: 0.25rem;
	}

	.bot-body {
		flex: 1;
		min-width: 0;
	}

	.bubble {
		max-width: 70%;
		background: var(--color-primary);
		color: white;
		padding: 0.7rem 1rem;
		border-radius: 14px 14px 4px 14px;
		box-shadow: 0 4px 14px -8px rgba(26, 26, 46, 0.25);
	}

	.user-bubble.subtle {
		background: var(--color-surface-warm);
		color: var(--color-ink);
		border: 1px solid var(--color-bot-border);
	}

	.meta {
		display: flex;
		justify-content: space-between;
		gap: 0.75rem;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		opacity: 0.8;
		margin-bottom: 0.3rem;
	}

	.user-text {
		margin: 0;
		font-size: 0.95rem;
		line-height: 1.5;
		word-break: break-word;
	}

	.typing {
		display: inline-flex;
		gap: 6px;
		padding: 0.85rem 1.1rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px 14px 14px 4px;
		width: fit-content;
	}

	.typing span {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: var(--color-ink-muted);
		animation: bounce 1.2s infinite ease-in-out both;
	}

	.typing span:nth-child(2) {
		animation-delay: 0.15s;
	}
	.typing span:nth-child(3) {
		animation-delay: 0.3s;
	}

	.error-banner {
		margin-top: 0.75rem;
		padding: 0.75rem 1rem;
		background: rgba(212, 72, 72, 0.07);
		border-left: 3px solid var(--color-error);
		border-radius: 0 6px 6px 0;
		font-size: 0.85rem;
		color: var(--color-error);
	}

	.error-label {
		font-weight: 600;
	}

	.composer {
		margin-top: 1rem;
		padding-top: 1rem;
		border-top: 1px solid var(--color-bot-border);
		position: sticky;
		bottom: 0;
		background: var(--color-surface, transparent);
	}

	.prompt-empty {
		text-align: center;
		padding: 3rem 1rem;
		color: var(--color-ink-muted);
	}

	.ornament-row {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.6rem;
		color: var(--color-accent);
		margin-bottom: 1rem;
		opacity: 0.7;
	}

	.dot {
		width: 4px;
		height: 4px;
		border-radius: 50%;
		background: currentColor;
	}

	.line {
		width: 28px;
		height: 1px;
		background: currentColor;
	}

	.diamond {
		font-family: var(--font-display);
		font-size: 0.75rem;
	}

	.prompt-msg {
		font-family: var(--font-display);
		font-size: 1.05rem;
		font-style: italic;
		color: var(--color-ink-muted);
		margin: 0;
	}

	.end-cta {
		margin-top: 2rem;
		text-align: center;
	}

	.end-rule {
		width: 80px;
		height: 1px;
		background: var(--color-bot-border);
		margin: 0 auto 1.5rem auto;
	}

	.end-btn {
		font-family: var(--font-body);
		font-size: 0.85rem;
		color: var(--color-ink-light);
		background: transparent;
		border: 1px solid var(--color-bot-border);
		padding: 0.55rem 1.1rem;
		border-radius: 999px;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.end-btn:hover {
		color: var(--color-primary);
		border-color: var(--color-primary);
		background: rgba(59, 76, 192, 0.04);
	}

	.end-hint {
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		margin: 0.6rem 0 0 0;
		font-style: italic;
	}

	.side {
		position: sticky;
		top: 1rem;
	}

	.side-inner {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		padding: 1.5rem;
		max-height: calc(100vh - 8rem);
		overflow-y: auto;
	}

	@keyframes fadeUp {
		from {
			opacity: 0;
			transform: translateY(6px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0.6);
			opacity: 0.4;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	@media (max-width: 920px) {
		.theory-mode {
			grid-template-columns: 1fr;
			gap: 1.5rem;
			padding: 1.25rem;
		}
		.side {
			position: static;
		}
		.side-inner {
			max-height: none;
		}
		.bubble {
			max-width: 85%;
		}
		.chat-stack {
			max-height: 60vh;
		}
	}
</style>
