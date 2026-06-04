<script lang="ts">
	import Latex from '$lib/components/Latex.svelte';

	let {
		args
	}: {
		args: string; // raw tool-call arguments string (JSON of {text: ...})
	} = $props();

	// `parse_problem` is called with `{text: "..."}` and we don't have the
	// *result* embedded in the tool call — only the summary. So we just show
	// a marginal note that a problem was extracted. The actual model lands
	// in the assistant content as Markdown; this artifact stays minimal.
	// In a future iteration, when the orchestrator persists the structured
	// result in metadata, this can render a full LPModel preview.

	const inputText = $derived.by(() => {
		try {
			const parsed = JSON.parse(args || '{}');
			const t = (parsed.text ?? '') as string;
			return t.length > 240 ? t.slice(0, 220) + '…' : t;
		} catch {
			return '';
		}
	});
</script>

{#if inputText}
	<aside class="artifact" aria-label="Enunciado parseado">
		<div class="rail" aria-hidden="true"></div>
		<div class="body">
			<div class="super-title">
				<span class="glyph" aria-hidden="true">¶</span>
				Enunciado interpretado
			</div>
			<p class="quote">"{inputText}"</p>
			<div class="hint">El modelo extraído aparece arriba — pedí <em>resolver</em> para ver vértices y óptimo.</div>
		</div>
	</aside>
{/if}

<style>
	.artifact {
		display: grid;
		grid-template-columns: 28px 1fr;
		gap: 0.85rem;
		padding: 0.85rem 1rem 0.95rem 0.75rem;
		background: linear-gradient(
			to right,
			color-mix(in srgb, var(--color-primary) 5%, transparent),
			transparent
		);
		border-left: 2px solid var(--color-primary);
		border-radius: 0 8px 8px 0;
		margin-top: 0.7rem;
		animation: fadeIn 0.25s ease-out;
	}

	.rail {
		display: flex;
		justify-content: center;
		padding-top: 0.1rem;
	}

	.rail::before {
		content: '¶';
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-primary);
		font-size: 1.25rem;
		width: 26px;
		height: 26px;
		border-radius: 50%;
		border: 1px solid currentColor;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		background: var(--color-surface-card);
		line-height: 1;
	}

	.super-title {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-primary);
		margin-bottom: 0.4rem;
	}

	.glyph {
		display: none;
	}

	.quote {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.95rem;
		line-height: 1.55;
		color: var(--color-ink-light);
		margin: 0;
		padding-left: 0.4rem;
		border-left: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);
	}

	.hint {
		font-family: var(--font-body);
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		margin-top: 0.5rem;
	}

	.hint em {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-primary);
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
