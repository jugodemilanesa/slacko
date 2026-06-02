<script lang="ts">
	import { onMount } from 'svelte';
	import {
		model,
		addMessage,
		advanceState,
		solverResult,
		sendAssistantMessage,
		addTip
	} from '$lib/stores/chat';
	import { solveProblem } from '$lib/api/solver';
	import { get } from 'svelte/store';

	import GraphicalMethodTutorial from '$lib/components/GraphicalMethodTutorial.svelte';
	import VertexAnalysisTutorial from '$lib/components/VertexAnalysisTutorial.svelte';
	import SolutionArtifacts from '$lib/components/SolutionArtifacts.svelte';

	type Phase =
		| 'solving'
		| 'degenerate'
		| 'tutorial-graph'
		| 'graph-shown'
		| 'tutorial-vertex'
		| 'all-shown';

	let phase = $state<Phase>('solving');
	let error = $state('');

	onMount(async () => {
		try {
			const m = get(model);
			const result = await solveProblem({
				objective_coefficients: m.variables.map((v) => v.coefficient),
				sense: m.sense,
				constraints: m.constraints.map((c) => ({
					coefficients: c.coefficients,
					sign: c.sign,
					rhs: c.rhs,
					label: c.label
				}))
			});
			solverResult.set(result);
			const isDegenerate = result.status === 'single_point' || result.status === 'infeasible';
			phase = isDegenerate ? 'degenerate' : 'tutorial-graph';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error al resolver';
		}
	});

	function continueAfterGraphTutorial() {
		phase = 'graph-shown';
	}

	function continueAfterVertexTutorial() {
		phase = 'all-shown';
	}

	function showVertexTutorial() {
		phase = 'tutorial-vertex';
	}

	function round(n: number): string {
		return Number.isInteger(n) ? n.toString() : n.toFixed(2);
	}

	async function next() {
		addMessage('user', 'Ver interpretación');
		const r = get(solverResult);
		const m = get(model);
		advanceState();
		if (r?.optimal_point) {
			const sense = m.sense === 'maximize' ? 'máxima' : 'mínima';
			await sendAssistantMessage(
				`El punto óptimo se encuentra en **${m.variables[0].name} = ${round(r.optimal_point[0])}** (${m.variables[0].label}), **${m.variables[1].name} = ${round(r.optimal_point[1])}** (${m.variables[1].label}), generando un **Z = ${round(r.optimal_value!)}** ${sense}.`,
				{ delay: 900, expression: 'happy' }
			);
		} else {
			await sendAssistantMessage(
				'No se encontró una solución factible para este problema.',
				{ delay: 700, expression: 'sad' }
			);
		}
	}

	$effect(() => {
		addTip('tip', 'Ya tenés la región factible. Para encontrar el óptimo formalmente, tenemos que examinar uno por uno los vértices del polígono.', 'Lo que sigue');
	});
</script>

<div class="step-enter space-y-4">
	{#if error}
		<div class="error-banner">
			<span class="overline">No pudimos resolver</span>
			<p>{error}</p>
		</div>
	{:else if phase === 'solving'}
		<div class="solving">
			<div class="dots">
				<span></span><span></span><span></span>
			</div>
			<p class="solving-text">Resolviendo el problema…</p>
		</div>
	{:else if $solverResult && phase === 'degenerate'}
		<div class="degenerate-banner">
			<span class="degen-icon" aria-hidden="true">⚠</span>
			<div class="degen-body">
				<span class="degen-label">
					{$solverResult.status === 'infeasible' ? 'Región factible vacía' : 'Región factible degenerada'}
				</span>
				<p class="degen-msg">
					{#if $solverResult.warning}
						{$solverResult.warning}
					{:else if $solverResult.status === 'infeasible'}
						Las restricciones son incompatibles: no existe ningún punto que las satisfaga todas a la vez. Revisá si alguna demanda mínima supera la disponibilidad total.
					{:else}
						La región factible colapsó a un único punto. Revisá los valores del lado derecho de las restricciones —especialmente aquellas con RHS = 0.
					{/if}
				</p>
				<p class="degen-hint">
					Corregí las restricciones y volvé a ejecutar el modelo para obtener una solución válida.
				</p>
			</div>
		</div>

		{#if $solverResult.feasible_vertices.length > 0}
			<SolutionArtifacts model={get(model)} result={$solverResult} show="graph" />
		{/if}
	{:else if $solverResult}
		{#if phase === 'tutorial-graph'}
			<GraphicalMethodTutorial
				model={get(model)}
				onContinue={continueAfterGraphTutorial}
			/>
		{:else}
			<!-- Tutorial collapsed reference -->
			<details class="tutorial-collapsed">
				<summary>
					<span class="overline">Lección 01 · Método gráfico</span>
					<span class="see">Ver de nuevo</span>
				</summary>
				<div class="tutorial-collapsed-body">
					<GraphicalMethodTutorial
						model={get(model)}
						onContinue={continueAfterGraphTutorial}
					/>
				</div>
			</details>

			<!-- The graph -->
			<SolutionArtifacts
				model={get(model)}
				result={$solverResult}
				show="graph"
			/>

			{#if phase === 'graph-shown'}
					<button class="cta-btn" onclick={showVertexTutorial}>
						Aprender el análisis de vértices
						<span class="arrow">→</span>
					</button>
			{:else if phase === 'tutorial-vertex'}
				<VertexAnalysisTutorial
					sense={get(model).sense}
					onContinue={continueAfterVertexTutorial}
				/>
			{:else if phase === 'all-shown'}
				<details class="tutorial-collapsed">
					<summary>
						<span class="overline">Lección 02 · Vértices</span>
						<span class="see">Ver de nuevo</span>
					</summary>
					<div class="tutorial-collapsed-body">
						<VertexAnalysisTutorial
							sense={get(model).sense}
							onContinue={continueAfterVertexTutorial}
						/>
					</div>
				</details>

				<SolutionArtifacts
					model={get(model)}
					result={$solverResult}
					show="vertices"
				/>

				<button onclick={next} class="primary-cta">
					Ver interpretación final
					<span class="arrow">→</span>
				</button>
			{/if}
		{/if}
	{/if}
</div>

<style>
	.solving {
		padding: 3rem 1rem;
		text-align: center;
		color: var(--color-ink-muted);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.solving-text {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 1rem;
		margin: 0;
	}

	.dots {
		display: flex;
		gap: 8px;
	}

	.dots span {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--color-accent);
		animation: bounce 1.2s infinite ease-in-out;
		opacity: 0.4;
	}

	.dots span:nth-child(2) {
		animation-delay: 0.15s;
	}
	.dots span:nth-child(3) {
		animation-delay: 0.3s;
	}

	.error-banner {
		padding: 1rem 1.2rem;
		background: rgba(212, 72, 72, 0.06);
		border-left: 3px solid var(--color-error, #d44848);
		border-radius: 0 8px 8px 0;
		font-family: var(--font-body);
	}

	.error-banner .overline {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-error, #d44848);
		display: block;
		margin-bottom: 0.25rem;
	}

	.error-banner p {
		margin: 0;
		color: var(--color-ink);
		font-size: 0.9rem;
	}

	.degenerate-banner {
		display: flex;
		gap: 0.9rem;
		padding: 1rem 1.1rem;
		background: rgba(212, 168, 83, 0.08);
		border: 1px solid rgba(212, 168, 83, 0.45);
		border-radius: 10px;
	}

	.degen-icon {
		font-size: 1.25rem;
		line-height: 1.3;
		color: #c8891a;
		flex-shrink: 0;
	}

	.degen-body {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.degen-label {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: #c8891a;
		font-weight: 600;
	}

	.degen-msg {
		margin: 0;
		color: var(--color-ink);
		font-size: 0.88rem;
		line-height: 1.5;
	}

	.degen-hint {
		margin: 0;
		color: var(--color-ink-muted);
		font-size: 0.8rem;
		font-style: italic;
	}

	.tutorial-collapsed {
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		background: var(--color-surface-card);
	}

	.tutorial-collapsed summary {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.6rem 0.95rem;
		cursor: pointer;
		list-style: none;
	}

	.tutorial-collapsed summary::-webkit-details-marker {
		display: none;
	}

	.tutorial-collapsed .overline {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-accent);
	}

	.tutorial-collapsed .see {
		font-family: var(--font-body);
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		font-style: italic;
	}

	.tutorial-collapsed[open] .see {
		color: var(--color-primary);
	}

	.tutorial-collapsed-body {
		padding: 0.65rem 0.65rem 0.85rem 0.65rem;
		border-top: 1px solid var(--color-bot-border);
	}

	.cta-btn {
		align-self: flex-start;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.65rem 1.2rem;
		background-color: var(--color-surface-card);
		color: var(--color-ink);
		border: 1px solid var(--color-bot-border);
		border-radius: 999px;
		font-family: var(--font-body);
		font-size: 0.85rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.cta-btn:hover {
		background-color: var(--color-primary);
		color: white;
		border-color: var(--color-primary);
		transform: translateY(-1px);
	}

	.primary-cta {
		width: 100%;
		padding: 0.8rem 1.2rem;
		background: var(--color-accent);
		color: var(--color-ink);
		border: 1px solid var(--color-accent);
		border-radius: 12px;
		font-family: var(--font-body);
		font-size: 0.92rem;
		font-weight: 600;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		transition: all 0.25s ease-in-out;
	}

	.primary-cta:hover {
		background: var(--color-ink);
		color: var(--color-surface-card);
		transform: translateY(-1px);
		box-shadow: 0 8px 22px -10px color-mix(in srgb, var(--color-ink) 40%, transparent);
	}

	.arrow {
		font-family: var(--font-display);
		transition: transform 0.25s ease-in-out;
	}

	.cta-btn:hover .arrow,
	.primary-cta:hover .arrow {
		transform: translateX(3px);
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
</style>
