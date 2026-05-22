<script lang="ts">
	import { getConcept, type ConceptDetail } from '$lib/api/theory';
	import MarkdownBody from '$lib/components/theory/MarkdownBody.svelte';

	let {
		citation
	}: {
		citation: string;
	} = $props();

	// Citations look like "wiki/concepts/region-factible.md" — extract the slug
	// and infer a display title from it (the actual title comes from the API).
	const conceptId = $derived.by(() => {
		const m = citation.match(/concepts\/([^/.]+)/);
		return m ? m[1] : citation;
	});

	const inferredTitle = $derived(
		conceptId.replace(/-/g, ' ').replace(/^./, (c) => c.toUpperCase())
	);

	let open = $state(false);
	let loading = $state(false);
	let concept = $state<ConceptDetail | null>(null);
	let error = $state<string | null>(null);

	async function show() {
		open = true;
		if (concept || loading) return;
		loading = true;
		error = null;
		try {
			const res = await getConcept(conceptId);
			concept = res.concept;
		} catch (e) {
			error = e instanceof Error ? e.message : 'No pude cargar el concepto.';
		} finally {
			loading = false;
		}
	}

	function close() {
		open = false;
	}

	function handleEscape(e: KeyboardEvent) {
		if (e.key === 'Escape' && open) close();
	}
</script>

<svelte:window onkeydown={handleEscape} />

<button type="button" class="cite" onclick={show} title="Abrir concepto del wiki">
	<span class="cite-glyph" aria-hidden="true">§</span>
	<span class="cite-title">{concept?.title ?? inferredTitle}</span>
</button>

{#if open}
	<div
		class="backdrop"
		role="button"
		tabindex="-1"
		aria-label="Cerrar"
		onclick={close}
		onkeydown={(e) => e.key === 'Enter' && close()}
	></div>
	<div class="drawer" role="dialog" aria-modal="true" aria-label="Concepto del wiki">
		<header class="head">
			<div>
				<div class="overline">Concepto del wiki</div>
				<h2 class="title">{concept?.title ?? inferredTitle}</h2>
				{#if concept?.category}
					<div class="cat">{concept.category.replace(/-/g, ' ')}</div>
				{/if}
			</div>
			<button type="button" class="close" onclick={close} aria-label="Cerrar">×</button>
		</header>

		<div class="body">
			{#if loading}
				<div class="status">
					<span class="dot"></span><span class="dot"></span><span class="dot"></span>
				</div>
			{:else if error}
				<div class="err" role="alert">
					<div class="err-label">No se pudo cargar</div>
					<div class="err-msg">{error}</div>
				</div>
			{:else if concept}
				{#if concept.summary}
					<p class="summary"><em>{concept.summary}</em></p>
				{/if}
				<MarkdownBody content={concept.content} />
				{#if concept.aliases && concept.aliases.length > 0}
					<details class="aliases">
						<summary>También aparece como…</summary>
						<ul>
							{#each concept.aliases as alias}
								<li>{alias}</li>
							{/each}
						</ul>
					</details>
				{/if}
			{/if}
		</div>
	</div>
{/if}

<style>
	.cite {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.2rem 0.65rem 0.2rem 0.55rem;
		border-radius: 999px;
		background: color-mix(in srgb, var(--color-accent) 6%, var(--color-surface-card));
		border: 1px solid color-mix(in srgb, var(--color-accent) 35%, transparent);
		color: var(--color-ink);
		font-family: var(--font-body);
		font-size: 0.75rem;
		cursor: pointer;
		transition: all 0.18s ease;
		line-height: 1.4;
		white-space: nowrap;
	}

	.cite:hover {
		border-color: var(--color-accent);
		background: color-mix(in srgb, var(--color-accent) 14%, var(--color-surface-card));
		transform: translateY(-1px);
	}

	.cite-glyph {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-accent);
		font-size: 1rem;
		line-height: 1;
	}

	.cite-title {
		font-style: italic;
		font-family: var(--font-display);
		font-size: 0.92rem;
		color: var(--color-ink);
	}

	/* Drawer ---------------------------------------------------------------- */
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(26, 26, 46, 0.45);
		backdrop-filter: blur(3px);
		-webkit-backdrop-filter: blur(3px);
		z-index: 60;
		border: none;
		cursor: pointer;
		animation: fadeIn 0.18s ease-out;
	}

	.drawer {
		position: fixed;
		top: 0;
		right: 0;
		bottom: 0;
		width: min(520px, 94vw);
		background: var(--color-surface-card);
		border-left: 1px solid var(--color-bot-border);
		box-shadow: -28px 0 64px -28px rgba(26, 26, 46, 0.4);
		z-index: 61;
		display: flex;
		flex-direction: column;
		animation: slideIn 0.28s cubic-bezier(0.32, 0.72, 0, 1);
	}

	.head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		padding: 1.5rem 1.5rem 1rem 1.5rem;
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
		font-size: 1.75rem;
		line-height: 1.1;
		color: var(--color-ink);
		margin: 0;
		letter-spacing: -0.01em;
	}

	.cat {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-top: 0.4rem;
	}

	.close {
		font-family: var(--font-display);
		font-size: 1.8rem;
		line-height: 1;
		background: transparent;
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink-muted);
		width: 36px;
		height: 36px;
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

	.body {
		flex: 1;
		overflow-y: auto;
		padding: 1.25rem 1.5rem 2.25rem 1.5rem;
	}

	.summary {
		font-family: var(--font-display);
		font-size: 1.05rem;
		line-height: 1.6;
		color: var(--color-ink-light);
		margin: 0 0 1.25rem 0;
		padding-left: 0.85rem;
		border-left: 2px solid var(--color-accent);
	}

	.summary em {
		font-style: italic;
	}

	.status {
		display: flex;
		gap: 6px;
		padding: 1rem 0;
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

	.err {
		padding: 0.85rem 1rem;
		background: color-mix(in srgb, var(--color-error) 6%, transparent);
		border-left: 3px solid var(--color-error);
		border-radius: 0 8px 8px 0;
	}

	.err-label {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-error);
		margin-bottom: 0.2rem;
	}

	.err-msg {
		color: var(--color-ink);
		font-size: 0.88rem;
	}

	.aliases {
		margin-top: 1.5rem;
		padding-top: 1rem;
		border-top: 1px dashed var(--color-bot-border);
	}

	.aliases summary {
		cursor: pointer;
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.88rem;
		color: var(--color-ink-muted);
		list-style: none;
	}

	.aliases summary::before {
		content: '+ ';
		font-family: var(--font-mono);
		color: var(--color-accent);
	}

	.aliases[open] summary::before {
		content: '− ';
	}

	.aliases ul {
		margin-top: 0.6rem;
		padding-left: 1rem;
		font-size: 0.85rem;
		color: var(--color-ink-light);
		font-family: var(--font-display);
		font-style: italic;
	}

	.aliases li {
		margin-bottom: 0.3rem;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes slideIn {
		from {
			transform: translateX(100%);
		}
		to {
			transform: translateX(0);
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
