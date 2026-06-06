<script lang="ts">
	import katex from 'katex';
	import 'katex/dist/katex.min.css';

	let {
		expr,
		display = false,
		ariaLabel
	}: {
		expr: string;
		display?: boolean;
		ariaLabel?: string;
	} = $props();

	const html = $derived.by(() => {
		try {
			return katex.renderToString(expr, {
				displayMode: display,
				throwOnError: false,
				strict: 'ignore',
				output: 'html'
			});
		} catch {
			// Escapamos expr en el fallback (se inyecta vía {@html}).
			const safe = expr
				.replace(/&/g, '&amp;')
				.replace(/</g, '&lt;')
				.replace(/>/g, '&gt;');
			return `<span class="latex-fallback">${safe}</span>`;
		}
	});
</script>

{#if display}
	<div class="latex-block" aria-label={ariaLabel ?? expr}>
		{@html html}
	</div>
{:else}
	<span class="latex-inline" aria-label={ariaLabel ?? expr}>
		{@html html}
	</span>
{/if}

<style>
	.latex-block {
		display: flex;
		justify-content: center;
		padding: 0.5rem 0;
		font-size: 1.1rem;
		color: var(--color-ink, #1a1a2e);
		overflow-x: auto;
	}

	.latex-inline {
		display: inline-block;
		color: var(--color-ink, #1a1a2e);
	}

	.latex-fallback {
		font-family: var(--font-mono, monospace);
		background: rgba(212, 72, 72, 0.06);
		padding: 0.1em 0.4em;
		border-radius: 3px;
		font-size: 0.85em;
		color: var(--color-error, #d44848);
	}

	:global(.katex) {
		font-size: 1.05em;
	}

	.latex-inline :global(.katex) {
		font-size: 1em;
	}
</style>
