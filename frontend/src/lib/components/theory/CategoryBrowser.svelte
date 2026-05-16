<script lang="ts">
	import { onMount } from 'svelte';
	import {
		listCategories,
		listConcepts,
		type ConceptSummary,
		type TheoryCategory
	} from '$lib/api/theory';

	let { onSelect }: { onSelect: (conceptId: string) => void } = $props();

	let categories = $state<TheoryCategory[]>([]);
	let conceptsByCategory = $state<Record<string, ConceptSummary[]>>({});
	let expanded = $state<Record<string, boolean>>({});
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			const res = await listCategories();
			categories = res.categories;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error al cargar categorías';
		} finally {
			loading = false;
		}
	});

	async function toggle(catId: string) {
		expanded[catId] = !expanded[catId];
		if (expanded[catId] && !conceptsByCategory[catId]) {
			try {
				const res = await listConcepts(catId);
				conceptsByCategory[catId] = res.concepts;
			} catch (e) {
				error = e instanceof Error ? e.message : 'Error al cargar conceptos';
			}
		}
	}
</script>

<aside class="category-browser">
	<header class="mb-5">
		<div class="text-[0.65rem] tracking-[0.18em] uppercase text-ink-muted font-medium font-mono">
			Índice
		</div>
		<h2 class="font-display text-2xl text-ink mt-1 leading-tight">Por temas</h2>
		<p class="text-xs text-ink-muted mt-1.5 leading-relaxed">
			Recorré el temario por categoría.
		</p>
	</header>

	{#if loading}
		<div class="space-y-2">
			{#each Array(6) as _, i}
				<div class="h-7 bg-surface-warm/60 rounded animate-pulse" style="animation-delay: {i * 60}ms"></div>
			{/each}
		</div>
	{:else if error}
		<div class="text-sm text-error">{error}</div>
	{:else}
		<ol class="space-y-1 toc">
			{#each categories as cat, i}
				<li class="toc-item">
					<button
						type="button"
						class="toc-row group"
						class:open={expanded[cat.id]}
						onclick={() => toggle(cat.id)}
					>
						<span class="toc-num font-mono">{String(i + 1).padStart(2, '0')}</span>
						<span class="toc-title">{cat.title}</span>
						<span class="toc-leader" aria-hidden="true"></span>
						<span class="toc-count font-mono">{cat.concept_count}</span>
						<span
							class="toc-caret"
							style="transform: rotate({expanded[cat.id] ? '90' : '0'}deg)"
						>›</span>
					</button>
					{#if expanded[cat.id]}
						<ul class="toc-children">
							{#each conceptsByCategory[cat.id] ?? [] as concept (concept.id)}
								<li>
									<button
										type="button"
										class="toc-child"
										onclick={() => onSelect(concept.id)}
									>
										<span class="dot" aria-hidden="true">·</span>
										<span class="title">{concept.title}</span>
									</button>
								</li>
							{/each}
						</ul>
					{/if}
				</li>
			{/each}
		</ol>
	{/if}
</aside>

<style>
	.category-browser {
		font-feature-settings: 'liga' 1, 'kern' 1;
	}

	.toc-row {
		width: 100%;
		display: grid;
		grid-template-columns: auto 1fr auto auto auto;
		align-items: baseline;
		gap: 0.5rem;
		padding: 0.5rem 0;
		text-align: left;
		cursor: pointer;
		border-bottom: 1px solid transparent;
		transition: border-color 0.2s ease;
	}

	.toc-row:hover {
		border-bottom-color: rgba(212, 168, 83, 0.4);
	}

	.toc-row.open {
		border-bottom-color: rgba(212, 168, 83, 0.5);
	}

	.toc-num {
		font-size: 0.7rem;
		color: var(--color-accent);
		letter-spacing: 0.05em;
		font-weight: 500;
	}

	.toc-title {
		font-family: var(--font-display);
		font-size: 1.0625rem;
		color: var(--color-ink);
		line-height: 1.2;
	}

	.toc-row:hover .toc-title {
		color: var(--color-primary-dark);
	}

	.toc-leader {
		display: block;
		min-width: 1rem;
		height: 1px;
		background-image: radial-gradient(circle, var(--color-ink-muted) 0.6px, transparent 0.6px);
		background-size: 4px 4px;
		background-repeat: repeat-x;
		background-position: 0 50%;
		opacity: 0.45;
		transform: translateY(-3px);
	}

	.toc-count {
		font-size: 0.75rem;
		color: var(--color-ink-muted);
		min-width: 1.4em;
		text-align: right;
	}

	.toc-caret {
		font-family: var(--font-display);
		font-size: 1.1rem;
		color: var(--color-ink-muted);
		transition: transform 0.25s ease;
		display: inline-block;
		line-height: 1;
	}

	.toc-row:hover .toc-caret {
		color: var(--color-accent);
	}

	.toc-children {
		list-style: none;
		padding: 0.25rem 0 0.5rem 1.85rem;
		margin: 0;
		animation: toc-expand 0.3s ease-out;
	}

	@keyframes toc-expand {
		from {
			opacity: 0;
			transform: translateY(-4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.toc-child {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		width: 100%;
		text-align: left;
		padding: 0.3rem 0;
		font-size: 0.875rem;
		color: var(--color-ink-light);
		cursor: pointer;
		transition: color 0.15s ease, transform 0.15s ease;
	}

	.toc-child:hover {
		color: var(--color-primary);
		transform: translateX(2px);
	}

	.toc-child .dot {
		color: var(--color-accent);
		opacity: 0.6;
		font-size: 1.2em;
		line-height: 0.8;
	}

	.toc-child .title {
		flex: 1;
	}
</style>
