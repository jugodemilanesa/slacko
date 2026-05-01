<script lang="ts">
	import { onMount } from 'svelte';
	import {
		queryTheory,
		getConcept,
		listCategories,
		type TheoryCategory,
		type ConceptDetail,
		type ConceptSummary,
		type QueryResponse
	} from '$lib/api/theory';
	import {
		lastQuery,
		lastResponse,
		selectedConcept,
		selectedConceptRelated,
		isLoading,
		queryError,
		queryHistory,
		pushHistory,
		clearTheory
	} from '$lib/stores/theory';
	import { resetChat } from '$lib/stores/chat';

	import TheorySearch from '$lib/components/theory/TheorySearch.svelte';
	import ConceptCard from '$lib/components/theory/ConceptCard.svelte';
	import EmptyResult from '$lib/components/theory/EmptyResult.svelte';
	import CategoryBrowser from '$lib/components/theory/CategoryBrowser.svelte';
	import TheoryHistory from '$lib/components/theory/TheoryHistory.svelte';

	let question = $state('');
	let categories = $state<TheoryCategory[]>([]);

	$effect(() => {
		question = $lastQuery;
	});

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

	async function runQuery(q: string) {
		isLoading.set(true);
		queryError.set(null);
		try {
			const res = await queryTheory(q);
			lastQuery.set(q);
			lastResponse.set(res);
			pushHistory(q, res);
			// Clear any previously navigated concept so the result card shows.
			selectedConcept.set(null);
			selectedConceptRelated.set([]);
		} catch (e) {
			queryError.set(e instanceof Error ? e.message : 'Error al buscar');
		} finally {
			isLoading.set(false);
		}
	}

	async function openConcept(id: string) {
		isLoading.set(true);
		queryError.set(null);
		try {
			const res = await getConcept(id);
			selectedConcept.set(res.concept);
			selectedConceptRelated.set(res.related);
		} catch (e) {
			queryError.set(e instanceof Error ? e.message : 'Error al cargar concepto');
		} finally {
			isLoading.set(false);
		}
	}

	function backToResult() {
		selectedConcept.set(null);
		selectedConceptRelated.set([]);
	}

	function backToStart() {
		clearTheory();
		resetChat();
	}

	function selectFromHistory(question_: string, conceptId: string | null) {
		if (conceptId) {
			openConcept(conceptId);
		} else {
			runQuery(question_);
		}
	}

	const matchedResp = $derived.by(() => {
		const r = $lastResponse;
		return r && r.matched ? r : null;
	});

	const unmatchedResp = $derived.by(() => {
		const r = $lastResponse;
		return r && !r.matched ? r : null;
	});

	const showingDetail = $derived($selectedConcept !== null);
</script>

<div class="theory-mode">
	<div class="content">
		<TheorySearch
			bind:value={question}
			loading={$isLoading}
			onSubmit={runQuery}
		/>

		<div class="history-bar">
			<TheoryHistory
				history={$queryHistory}
				onSelect={(e) => selectFromHistory(e.question, e.matchedConceptId)}
			/>
		</div>

		{#if $queryError}
			<div class="error-banner">
				<span class="error-label">Algo falló:</span> {$queryError}
			</div>
		{/if}

		<div class="result-area">
			{#if showingDetail && $selectedConcept}
				{#key $selectedConcept.id}
					<ConceptCard
						concept={$selectedConcept}
						related={$selectedConceptRelated}
						categoryTitle={categoryTitle($selectedConcept.category)}
						onSelectRelated={openConcept}
						onBack={backToResult}
						showBack={!!$lastResponse}
					/>
				{/key}
			{:else if matchedResp}
				{#key matchedResp.concept.id}
					<ConceptCard
						concept={matchedResp.concept}
						related={matchedResp.related}
						categoryTitle={categoryTitle(matchedResp.concept.category)}
						onSelectRelated={openConcept}
					/>
				{/key}
			{:else if unmatchedResp}
				<EmptyResult
					message={unmatchedResp.message}
					suggestions={unmatchedResp.suggestions}
					question={$lastQuery}
					onSelect={openConcept}
				/>
			{:else}
				<div class="prompt-empty">
					<div class="ornament-row" aria-hidden="true">
						<span class="dot"></span>
						<span class="line"></span>
						<span class="diamond">◆</span>
						<span class="line"></span>
						<span class="dot"></span>
					</div>
					<p class="prompt-msg">
						Escribí una pregunta arriba o explorá el temario por categoría.
					</p>
				</div>
			{/if}
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
			<CategoryBrowser onSelect={openConcept} />
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
	}

	.history-bar {
		margin-top: 1rem;
		min-height: 1.5rem;
	}

	.error-banner {
		margin-top: 1rem;
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

	.result-area {
		margin-top: 2rem;
		min-height: 200px;
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
		margin-top: 4rem;
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
	}
</style>
