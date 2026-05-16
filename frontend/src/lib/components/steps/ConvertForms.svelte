<script lang="ts">
	import { onMount } from 'svelte';
	import {
		model,
		addMessage,
		advanceState,
		standardFormResult,
		sendAssistantMessage
	} from '$lib/stores/chat';
	import { getStandardForm } from '$lib/api/solver';
	import { get } from 'svelte/store';
	import SlackoTip from '$lib/components/SlackoTip.svelte';

	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			const m = get(model);
			const result = await getStandardForm({
				variables: m.variables.map((v) => v.name),
				objective_coefficients: m.variables.map((v) => v.coefficient),
				sense: m.sense,
				constraints: m.constraints.map((c) => ({
					coefficients: c.coefficients,
					sign: c.sign,
					rhs: c.rhs,
					label: c.label
				}))
			});
			standardFormResult.set(result);
			loading = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error al convertir';
			loading = false;
		}
	});

	async function next() {
		addMessage('user', 'Entendido, resolver');
		advanceState();
		await sendAssistantMessage(
			'Calculando la **región factible**, los **vértices** y el **punto óptimo**…',
			{ delay: 800, expression: 'thinking' }
		);
	}

	const hasArtificials = $derived(
		($standardFormResult?.artificial_variables.length ?? 0) > 0
	);
</script>

<div class="step-enter space-y-3">
	{#if loading}
		<div class="loading">Convirtiendo a forma estándar…</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if $standardFormResult}
		<SlackoTip kind="concept" title="¿Qué es la forma estándar?">
			<p>
				Para resolver el problema necesitamos que <strong>todas las restricciones
				sean igualdades</strong>. Para eso introducimos variables auxiliares:
			</p>
			<ul>
				<li>
					<strong>Slack (s)</strong>: se suma a una restricción <code>≤</code>;
					representa el recurso <em>no utilizado</em>.
				</li>
				<li>
					<strong>Surplus (e)</strong>: se resta a una restricción <code>≥</code>;
					representa el <em>exceso</em> por encima del mínimo.
				</li>
				{#if hasArtificials}
					<li>
						<strong>Artificiales (a)</strong>: se usan en <code>≥</code> y <code>=</code>
						para que el método algebraico (Simplex) tenga un punto de partida.
						<em>No aparecen en el método gráfico</em>: te las muestro acá solo como
						referencia teórica.
					</li>
				{/if}
			</ul>
		</SlackoTip>

		<article class="standard-card">
			<header class="card-head">
				<span class="overline">Forma estándar</span>
				<h3 class="title">Modelo expandido</h3>
			</header>

			<div class="vars-row">
				{#if $standardFormResult.slack_variables.length > 0}
					<div class="var-chip slack">
						<span class="kind">slack</span>
						<span class="names">{$standardFormResult.slack_variables.join(', ')}</span>
					</div>
				{/if}

				{#if $standardFormResult.surplus_variables.length > 0}
					<div class="var-chip surplus">
						<span class="kind">surplus</span>
						<span class="names">{$standardFormResult.surplus_variables.join(', ')}</span>
					</div>
				{/if}

				{#if $standardFormResult.artificial_variables.length > 0}
					<div class="var-chip artificial">
						<span class="kind">artificial</span>
						<span class="names">{$standardFormResult.artificial_variables.join(', ')}</span>
					</div>
				{/if}
			</div>

			<div class="equations">
				<div class="eq-label">Ecuaciones</div>
				<ol class="eq-list">
					{#each $standardFormResult.constraints as c}
						<li>
							{#if c.label}
								<span class="eq-tag">{c.label}</span>
							{/if}
							<code class="eq-text">{c.equation}</code>
						</li>
					{/each}
				</ol>
			</div>
		</article>

		{#if hasArtificials}
			<SlackoTip kind="tip" title="Nota">
				<p>
					Como vamos a resolverlo por <strong>método gráfico</strong> (con sólo dos
					variables originales), las artificiales no nos van a aparecer en el gráfico
					ni en el análisis de vértices — sólo viven en la forma estándar.
				</p>
			</SlackoTip>
		{/if}

		<button onclick={next} class="next-btn">
			Continuar a resolución gráfica
			<span class="arrow">→</span>
		</button>
	{/if}
</div>

<style>
	.loading {
		padding: 1.5rem 1rem;
		text-align: center;
		color: var(--color-ink-muted);
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.95rem;
	}

	.error {
		padding: 0.85rem 1rem;
		background: rgba(212, 72, 72, 0.08);
		border-left: 3px solid var(--color-error, #d44848);
		border-radius: 0 6px 6px 0;
		color: var(--color-error, #d44848);
		font-size: 0.85rem;
	}

	.standard-card {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		padding: 1rem 1.2rem 1.1rem 1.2rem;
	}

	.card-head {
		margin-bottom: 0.85rem;
		padding-bottom: 0.5rem;
		border-bottom: 1px dashed var(--color-bot-border);
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-accent);
		display: block;
		margin-bottom: 0.2rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: 1.15rem;
		margin: 0;
		color: var(--color-ink);
	}

	.vars-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		margin-bottom: 0.85rem;
	}

	.var-chip {
		display: inline-flex;
		align-items: baseline;
		gap: 0.5rem;
		padding: 0.3rem 0.65rem;
		border-radius: 999px;
		border: 1px solid currentColor;
		font-family: var(--font-mono);
		font-size: 0.78rem;
	}

	.var-chip .kind {
		font-size: 0.62rem;
		letter-spacing: 0.16em;
		text-transform: uppercase;
		opacity: 0.7;
	}

	.var-chip.slack {
		color: var(--color-success, #2d9c6f);
		background: rgba(45, 156, 111, 0.06);
	}

	.var-chip.surplus {
		color: var(--color-warning, #d4a853);
		background: rgba(212, 168, 83, 0.08);
	}

	.var-chip.artificial {
		color: var(--color-error, #d44848);
		background: rgba(212, 72, 72, 0.06);
	}

	.equations {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.eq-label {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-bottom: 0.15rem;
	}

	.eq-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.eq-list li {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		padding: 0.4rem 0.6rem;
		background: var(--color-surface-warm, #fff7e8);
		border-radius: 6px;
		border-left: 2px solid var(--color-bot-border);
	}

	.eq-tag {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		flex-shrink: 0;
	}

	.eq-text {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-ink);
	}

	.next-btn {
		width: 100%;
		padding: 0.75rem 1rem;
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: 10px;
		font-family: var(--font-body);
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.18s ease;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}

	.next-btn:hover {
		background: var(--color-primary-dark, #2d3a9a);
		transform: translateY(-1px);
	}

	.arrow {
		transition: transform 0.18s ease;
	}

	.next-btn:hover .arrow {
		transform: translateX(3px);
	}
</style>
