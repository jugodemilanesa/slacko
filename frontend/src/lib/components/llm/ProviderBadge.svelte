<script lang="ts">
	let {
		provider
	}: {
		provider?: string;
	} = $props();

	const labels: Record<string, string> = {
		gemini: 'Gemini',
		groq: 'Groq',
		openrouter: 'OpenRouter',
		deterministic: 'sin LLM'
	};

	const display = $derived(provider ? labels[provider] ?? provider : null);
	const isDeterministic = $derived(provider === 'deterministic');
</script>

{#if display}
	<span class="prov" class:det={isDeterministic} title={isDeterministic ? 'Respondido con el matcher determinístico del wiki (sin LLM)' : `Procesado con ${display}`}>
		<span class="rail" aria-hidden="true"></span>
		<span class="lbl">via</span>
		<span class="name">{display}</span>
	</span>
{/if}

<style>
	.prov {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.18em;
		text-transform: lowercase;
		color: var(--color-ink-muted);
		opacity: 0.7;
		transition: opacity 0.18s ease;
		padding: 0.18rem 0.5rem 0.18rem 0;
	}

	.prov:hover {
		opacity: 1;
	}

	.rail {
		width: 14px;
		height: 1px;
		background: linear-gradient(
			to right,
			transparent,
			var(--color-primary),
			var(--color-accent)
		);
	}

	.lbl {
		font-style: italic;
		font-family: var(--font-display);
		font-size: 0.7rem;
		letter-spacing: 0;
		text-transform: none;
		color: var(--color-ink-muted);
	}

	.name {
		color: var(--color-ink-light);
		font-weight: 500;
		letter-spacing: 0.16em;
	}

	.prov.det .rail {
		background: linear-gradient(
			to right,
			transparent,
			var(--color-ink-muted)
		);
	}

	.prov.det .name {
		color: var(--color-ink-muted);
		font-style: italic;
		text-transform: none;
		letter-spacing: 0.08em;
	}
</style>
