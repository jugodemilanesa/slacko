<script lang="ts">
	let {
		toolName,
		args
	}: {
		toolName: 'solve_lp' | 'graph_lp';
		args: string; // raw tool-call arguments string (JSON of {model: {...}})
	} = $props();

	// The orchestrator returns the solver result back to the LLM (so it can
	// narrate it), but doesn't currently persist the structured payload alongside
	// the assistant message. Until that wiring lands, this artifact stays as a
	// pedagogical marker that points the reader to the narrated answer.
	//
	// When we extend the message metadata to include the raw solver output,
	// this component can render <SolutionArtifacts model={...} result={...}
	// variant="compact" /> directly.

	const modelPreview = $derived.by(() => {
		try {
			const parsed = JSON.parse(args || '{}');
			const model = parsed.model ?? {};
			const objective = model.objective?.expression as string | undefined;
			const constraintsCount = Array.isArray(model.constraints) ? model.constraints.length : 0;
			return { objective, constraintsCount };
		} catch {
			return { objective: undefined, constraintsCount: 0 };
		}
	});

	const label = $derived(toolName === 'graph_lp' ? 'Gráfico calculado' : 'Resolución calculada');
</script>

<aside class="artifact" aria-label={label}>
	<div class="rail" aria-hidden="true">
		<span class="orbit"></span>
	</div>
	<div class="body">
		<div class="overline">
			<span>{label}</span>
		</div>
		{#if modelPreview.objective}
			<div class="objective">
				<span class="lbl">obj</span>
				<code>{modelPreview.objective}</code>
			</div>
		{/if}
		{#if modelPreview.constraintsCount > 0}
			<div class="meta">
				<span class="mono">{modelPreview.constraintsCount}</span>
				{modelPreview.constraintsCount === 1 ? 'restricción' : 'restricciones'}
			</div>
		{/if}
		<div class="hint">
			Vértices y punto óptimo narrados arriba — para verlos en gráfico interactivo,
			abrí el modo <em>Paso a paso</em>.
		</div>
	</div>
</aside>

<style>
	.artifact {
		display: grid;
		grid-template-columns: 32px 1fr;
		gap: 0.85rem;
		padding: 0.85rem 1rem 0.95rem 0.75rem;
		background: linear-gradient(
			to right,
			color-mix(in srgb, var(--color-success) 5%, transparent),
			transparent
		);
		border-left: 2px solid var(--color-success);
		border-radius: 0 8px 8px 0;
		margin-top: 0.7rem;
		animation: fadeIn 0.25s ease-out;
	}

	.rail {
		display: flex;
		justify-content: center;
		padding-top: 0.15rem;
	}

	.orbit {
		width: 26px;
		height: 26px;
		border-radius: 50%;
		border: 1px solid var(--color-success);
		background: var(--color-surface-card);
		position: relative;
	}

	.orbit::before,
	.orbit::after {
		content: '';
		position: absolute;
		border-radius: 50%;
	}

	.orbit::before {
		left: 50%;
		top: 50%;
		width: 6px;
		height: 6px;
		background: var(--color-success);
		transform: translate(-50%, -50%);
	}

	.orbit::after {
		left: -3px;
		top: 50%;
		width: 5px;
		height: 5px;
		background: var(--color-accent);
		transform: translateY(-50%);
		box-shadow: 0 0 0 2px var(--color-surface-card);
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-success);
		margin-bottom: 0.4rem;
	}

	.objective {
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
		margin-bottom: 0.4rem;
	}

	.lbl {
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
	}

	.objective code {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-ink);
		background: var(--color-surface-warm);
		padding: 0.15rem 0.5rem;
		border-radius: 4px;
	}

	.meta {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.82rem;
		color: var(--color-ink-light);
		margin-bottom: 0.35rem;
	}

	.mono {
		font-family: var(--font-mono);
		font-style: normal;
		color: var(--color-ink);
		font-weight: 600;
	}

	.hint {
		font-family: var(--font-body);
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		line-height: 1.5;
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
