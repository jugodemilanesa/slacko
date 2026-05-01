<script lang="ts">
	import type { ConceptDetail, ConceptSummary } from '$lib/api/theory';
	import MarkdownBody from './MarkdownBody.svelte';

	let {
		concept,
		related = [],
		onSelectRelated,
		onBack,
		showBack = false,
		categoryTitle = ''
	}: {
		concept: ConceptDetail;
		related?: ConceptSummary[];
		onSelectRelated: (id: string) => void;
		onBack?: () => void;
		showBack?: boolean;
		categoryTitle?: string;
	} = $props();

	let showAliases = $state(false);

	const dropCap = $derived(concept.title.charAt(0).toUpperCase());
	const titleRest = $derived(concept.title.slice(1));
</script>

<article class="concept-card step-enter">
	<!-- Marginalia / spine -->
	<aside class="spine">
		<div class="spine-mark"></div>
		<div class="spine-meta">
			<div class="spine-label">Concepto</div>
			<div class="spine-id">{concept.id}</div>
		</div>
	</aside>

	<div class="card-body">
		<header class="card-header">
			<div class="flex items-start justify-between gap-4 flex-wrap">
				<div class="flex items-center gap-2 flex-wrap">
					{#if categoryTitle}
						<span class="category-pill">{categoryTitle}</span>
					{:else}
						<span class="category-pill">{concept.category.replace(/-/g, ' ')}</span>
					{/if}
					{#if showBack && onBack}
						<button
							type="button"
							class="back-btn"
							onclick={onBack}
						>
							<span aria-hidden="true">←</span> Volver
						</button>
					{/if}
				</div>
				<button
					type="button"
					class="aliases-toggle"
					onclick={() => (showAliases = !showAliases)}
					aria-expanded={showAliases}
				>
					{showAliases ? 'Ocultar' : 'Ver'} alias
				</button>
			</div>

			<h1 class="title">
				<span class="drop-cap">{dropCap}</span><span class="title-rest">{titleRest}</span>
			</h1>

			<p class="lede">{concept.summary}</p>

			{#if showAliases}
				<div class="aliases" role="region" aria-label="Aliases">
					<div class="aliases-label">También podés preguntar</div>
					<div class="aliases-list">
						{#each concept.aliases as alias}
							<span class="alias-chip">{alias}</span>
						{/each}
					</div>
				</div>
			{/if}
		</header>

		<hr class="rule" />

		<div class="card-content">
			<MarkdownBody content={concept.content} />
		</div>

		{#if related.length > 0}
			<footer class="related">
				<div class="related-header">
					<span class="ornament" aria-hidden="true">❦</span>
					<span class="related-label">Te puede interesar también</span>
				</div>
				<div class="related-list">
					{#each related as r}
						<button
							type="button"
							class="related-card"
							onclick={() => onSelectRelated(r.id)}
						>
							<div class="related-title">{r.title}</div>
							<div class="related-summary">{r.summary}</div>
							<div class="related-arrow" aria-hidden="true">→</div>
						</button>
					{/each}
				</div>
			</footer>
		{/if}
	</div>
</article>

<style>
	.concept-card {
		position: relative;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		display: grid;
		grid-template-columns: 56px 1fr;
		overflow: hidden;
		box-shadow: 0 1px 0 rgba(26, 26, 46, 0.02), 0 12px 32px -16px rgba(26, 26, 46, 0.18);
	}

	.spine {
		background: linear-gradient(180deg, rgba(212, 168, 83, 0.08), rgba(59, 76, 192, 0.05));
		border-right: 1px solid var(--color-bot-border);
		padding: 1.5rem 0.75rem;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}

	.spine-mark {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--color-accent);
		box-shadow: 0 0 0 4px rgba(212, 168, 83, 0.15);
		margin: 0 auto;
	}

	.spine-meta {
		writing-mode: vertical-rl;
		transform: rotate(180deg);
		text-align: center;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
	}

	.spine-label {
		color: var(--color-ink-muted);
		margin-bottom: 0.5rem;
	}

	.spine-id {
		color: var(--color-ink-light);
	}

	.card-body {
		padding: 2rem 2.25rem 2rem 1.75rem;
	}

	.card-header {
		margin-bottom: 1rem;
	}

	.category-pill {
		display: inline-block;
		font-family: var(--font-mono);
		font-size: 0.65rem;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		color: var(--color-accent);
		background: rgba(212, 168, 83, 0.08);
		border: 1px solid rgba(212, 168, 83, 0.3);
		padding: 0.25rem 0.6rem;
		border-radius: 999px;
	}

	.back-btn {
		font-family: var(--font-body);
		font-size: 0.75rem;
		color: var(--color-ink-muted);
		padding: 0.25rem 0.6rem;
		border-radius: 999px;
		border: 1px solid var(--color-bot-border);
		cursor: pointer;
		transition: all 0.15s ease;
		background: transparent;
	}

	.back-btn:hover {
		color: var(--color-ink);
		border-color: var(--color-primary);
		background: rgba(59, 76, 192, 0.05);
	}

	.aliases-toggle {
		font-family: var(--font-body);
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		cursor: pointer;
		background: transparent;
		border: none;
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		transition: color 0.15s ease;
		text-decoration: underline;
		text-decoration-style: dotted;
		text-underline-offset: 3px;
	}

	.aliases-toggle:hover {
		color: var(--color-primary);
	}

	.title {
		font-family: var(--font-display);
		font-size: clamp(2.2rem, 4vw, 3rem);
		line-height: 1;
		color: var(--color-ink);
		margin: 0.85rem 0 0.5rem 0;
		letter-spacing: -0.01em;
		position: relative;
	}

	.drop-cap {
		display: inline;
	}

	.title-rest {
		display: inline;
	}

	/* On wider screens we float a true drop-cap */
	@media (min-width: 720px) {
		.title {
			margin-top: 1.2rem;
		}
		.drop-cap {
			font-size: 5.5rem;
			line-height: 0.85;
			color: var(--color-accent);
			float: left;
			padding-right: 0.5rem;
			padding-top: 0.05em;
			font-weight: 400;
		}
		.title-rest {
			padding-top: 1.45rem;
			display: block;
		}
	}

	.lede {
		font-family: var(--font-body);
		font-size: 1.075rem;
		line-height: 1.65;
		color: var(--color-ink-light);
		margin: 0.5rem 0 1.25rem 0;
		font-style: italic;
	}

	.aliases {
		background: var(--color-surface-warm);
		border-left: 2px solid var(--color-accent);
		padding: 0.75rem 1rem;
		border-radius: 0 6px 6px 0;
		margin-bottom: 1rem;
		animation: fadeIn 0.25s ease-out;
	}

	.aliases-label {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-bottom: 0.4rem;
	}

	.aliases-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.alias-chip {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		color: var(--color-ink-light);
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		padding: 0.15rem 0.55rem;
		border-radius: 4px;
	}

	.rule {
		border: none;
		height: 1px;
		background: linear-gradient(
			90deg,
			transparent,
			rgba(212, 168, 83, 0.4),
			transparent
		);
		margin: 1.25rem 0 1.5rem 0;
	}

	.card-content {
		clear: both;
	}

	.related {
		margin-top: 2.5rem;
		padding-top: 1.5rem;
		border-top: 1px dashed var(--color-bot-border);
	}

	.related-header {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		margin-bottom: 1rem;
	}

	.ornament {
		font-family: var(--font-display);
		color: var(--color-accent);
		font-size: 1.1rem;
	}

	.related-label {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
	}

	.related-list {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 0.75rem;
	}

	.related-card {
		position: relative;
		text-align: left;
		background: var(--color-surface);
		border: 1px solid var(--color-bot-border);
		border-radius: 8px;
		padding: 0.85rem 1rem;
		cursor: pointer;
		transition: all 0.18s ease;
		overflow: hidden;
	}

	.related-card::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		width: 2px;
		background: var(--color-accent);
		transform: scaleY(0);
		transition: transform 0.18s ease;
		transform-origin: top;
	}

	.related-card:hover {
		border-color: var(--color-primary);
		transform: translateY(-1px);
		box-shadow: 0 6px 16px -8px rgba(26, 26, 46, 0.15);
	}

	.related-card:hover::before {
		transform: scaleY(1);
	}

	.related-title {
		font-family: var(--font-display);
		font-size: 1rem;
		color: var(--color-ink);
		margin-bottom: 0.25rem;
	}

	.related-summary {
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		line-height: 1.45;
		display: -webkit-box;
		line-clamp: 2;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.related-arrow {
		position: absolute;
		top: 0.85rem;
		right: 0.85rem;
		color: var(--color-ink-muted);
		opacity: 0;
		transition: opacity 0.18s, transform 0.18s;
		font-family: var(--font-display);
	}

	.related-card:hover .related-arrow {
		opacity: 1;
		transform: translateX(2px);
		color: var(--color-primary);
	}

	@media (max-width: 640px) {
		.concept-card {
			grid-template-columns: 36px 1fr;
		}
		.card-body {
			padding: 1.5rem 1.25rem;
		}
		.spine {
			padding: 1rem 0.4rem;
		}
		.spine-meta {
			font-size: 0.5rem;
		}
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}
</style>
