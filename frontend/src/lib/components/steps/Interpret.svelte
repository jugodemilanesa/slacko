<script lang="ts">
	import {
		model,
		solverResult,
		resetChat,
		sendAssistantMessage,
		addTip
	} from '$lib/stores/chat';
	import { get } from 'svelte/store';
	import SolutionArtifacts from '$lib/components/SolutionArtifacts.svelte';
	import Latex from '$lib/components/Latex.svelte';
	import { computeSlacks, fmt, type SlackInfo } from '$lib/math/slack';
	import { constraintLatex } from '$lib/math/formula';

	async function restart() {
		resetChat();
		await sendAssistantMessage(
			'Hola! Soy **Slacko**, tu tutor de Programación Lineal. ¿Cómo querés trabajar hoy?',
			{ delay: 600, expression: 'happy' }
		);
	}

	const m = get(model);
	const r = get(solverResult);

	const hasSolution = r?.optimal_point != null && r?.optimal_value != null;

	const slackInfo = $derived.by<SlackInfo[]>(() => {
		if (!hasSolution || !r?.optimal_point) return [];
		return computeSlacks(m, r.optimal_point);
	});

	function interpretationParagraph(): string {
		if (!hasSolution || !r?.optimal_point || r.optimal_value === null) {
			return 'No se encontró una solución factible para este problema. Revisá las restricciones.';
		}
		const sense = m.sense === 'maximize' ? 'maximizar' : 'minimizar';
		const senseResult = m.sense === 'maximize' ? 'máximo' : 'mínimo';
		const v1 = m.variables[0];
		const v2 = m.variables[1];
		const x1 = fmt(r.optimal_point[0]);
		const x2 = fmt(r.optimal_point[1]);
		const z = fmt(r.optimal_value);
		return `Para ${sense} la función objetivo, conviene **${x1} unidades de ${v1.label || v1.name}** y **${x2} unidades de ${v2.label || v2.name}**, lo que produce un valor ${senseResult} **Z = ${z}**.`;
	}

	const interpretation = interpretationParagraph();

	function slackVerdict(s: SlackInfo): string {
		if (s.kind === 'slack') {
			return s.binding
				? `recurso agotado (0 de holgura)`
				: `${fmt(s.slack)} unidades sin utilizar`;
		}
		if (s.kind === 'surplus') {
			return s.binding
				? `mínimo justo (0 de exceso)`
				: `${fmt(s.slack)} unidades por encima del mínimo`;
		}
		return s.binding ? 'cumple la igualdad' : `desvío de ${fmt(Math.abs(s.slack))}`;
	}

	$effect(() => {
		addTip('concept', 'Una holgura (slack) positiva en ≤ indica que te sobra ese recurso. Holgura cero significa que la restricción está activa (pasa por el óptimo). Un exceso (surplus) positivo en ≥ indica que producís por encima del mínimo.', '¿Qué nos dicen estos números?');
	});
</script>

<div class="step-enter space-y-4">
	<!-- Persistent artifacts: graph + vertex table stay visible -->
	{#if hasSolution && r}
		<SolutionArtifacts
			model={m}
			result={r}
			show="both"
			variant="compact"
		/>
	{/if}

	<!-- The interpretation card -->
	<article class="interp">
		<header class="interp-head">
			<span class="overline">Interpretación</span>
			<h2 class="title">
				<span class="drop">L</span>a recomendación
			</h2>
		</header>

		<p class="prose">
			{@html interpretation
				.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
				.replace(/\n/g, '<br/>')}
		</p>

		{#if hasSolution && r?.optimal_point}
			<div class="kpi-grid">
				{#each m.variables as v, i}
					<div class="kpi">
						<div class="kpi-label">{v.label || v.name}</div>
						<div class="kpi-value">{fmt(r.optimal_point[i])}</div>
						<div class="kpi-meta">{v.name}</div>
					</div>
				{/each}
				<div class="kpi kpi-z">
					<div class="kpi-label">Valor óptimo</div>
					<div class="kpi-value">{fmt(r.optimal_value!)}</div>
					<div class="kpi-meta">Z</div>
				</div>
			</div>
		{/if}

		{#if hasSolution && slackInfo.length > 0}
			<section class="slack-section">
				<header class="slack-head">
					<span class="head-glyph">‡</span>
					<h3>Recursos y holguras</h3>
					<span class="head-rule"></span>
				</header>
				<p class="slack-intro">
					Reemplazando el punto óptimo en cada restricción, así queda cada recurso:
				</p>

				<ul class="slack-list">
					{#each slackInfo as s, i}
						<li class="slack-row" data-kind={s.kind} data-binding={s.binding}>
							<div class="slack-marker" aria-hidden="true">
								{#if s.kind === 'slack'}
									<span class="kind-tag slack-tag">s</span>
								{:else if s.kind === 'surplus'}
									<span class="kind-tag surplus-tag">e</span>
								{:else}
									<span class="kind-tag eq-tag">=</span>
								{/if}
							</div>

							<div class="slack-body">
								<div class="slack-top">
									<span class="r-label">{s.constraintLabel}</span>
									<span class="r-eq">
										<Latex
											expr={constraintLatex(
												m.constraints[i],
												m.variables
											)}
										/>
									</span>
								</div>
								<div class="slack-stat">
									<span class="lhs">
										<Latex expr={`\\text{lhs} = ${fmt(s.lhs)}`} />
									</span>
									<span class="sep" aria-hidden="true">·</span>
									<span class="verdict" class:bound={s.binding}>
										{slackVerdict(s)}
									</span>
								</div>
							</div>

							<div class="slack-value" class:zero={s.binding}>
								{fmt(s.slack)}
							</div>
						</li>
					{/each}
				</ul>
			</section>
		{/if}
	</article>

	<button onclick={restart} class="restart-btn">
		← Resolver otro problema
	</button>
</div>

<style>
	.interp {
		background: var(--color-surface-card, #fffaf2);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		padding: 1.5rem 1.75rem 1.6rem 1.5rem;
		position: relative;
	}

	.interp::before {
		content: '';
		position: absolute;
		inset: 0 auto 0 0;
		width: 3px;
		background: var(--color-accent);
		border-radius: 14px 0 0 14px;
	}

	.interp-head {
		margin-bottom: 0.85rem;
		border-bottom: 1px dashed var(--color-bot-border);
		padding-bottom: 0.65rem;
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-accent);
		display: block;
		margin-bottom: 0.25rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: 1.75rem;
		line-height: 1.05;
		color: var(--color-ink);
		margin: 0;
	}

	.drop {
		color: var(--color-accent);
		font-size: 1.45em;
		float: left;
		line-height: 0.85;
		padding-right: 0.18em;
	}

	.prose {
		font-family: var(--font-body);
		font-size: 0.95rem;
		line-height: 1.7;
		color: var(--color-ink-light);
		margin: 0 0 0.85rem 0;
		clear: both;
	}

	.prose :global(strong) {
		color: var(--color-primary);
		font-weight: 600;
	}

	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 0.65rem;
		margin-bottom: 1rem;
	}

	.kpi {
		text-align: center;
		padding: 0.75rem 0.6rem 0.85rem 0.6rem;
		background: var(--color-surface-warm, #fff7e8);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		position: relative;
	}

	.kpi.kpi-z {
		background: linear-gradient(
			180deg,
			rgba(212, 168, 83, 0.15),
			rgba(212, 168, 83, 0.05)
		);
		border-color: rgba(212, 168, 83, 0.4);
	}

	.kpi-label {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		margin-bottom: 0.2rem;
	}

	.kpi-value {
		font-family: var(--font-mono);
		font-size: 1.6rem;
		font-weight: 700;
		color: var(--color-primary);
		line-height: 1;
	}

	.kpi.kpi-z .kpi-value {
		color: var(--color-accent);
		font-size: 1.85rem;
	}

	.kpi-meta {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-top: 0.2rem;
	}

	.slack-section {
		margin-top: 0.5rem;
	}

	.slack-head {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		margin-bottom: 0.45rem;
	}

	.head-glyph {
		color: var(--color-accent);
		font-family: var(--font-display);
		font-size: 1.1rem;
		line-height: 1;
	}

	.slack-head h3 {
		font-family: var(--font-display);
		font-size: 1.05rem;
		margin: 0;
		color: var(--color-ink);
	}

	.head-rule {
		flex: 1;
		height: 1px;
		background: linear-gradient(to right, var(--color-bot-border), transparent);
	}

	.slack-intro {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.88rem;
		margin: 0 0 0.6rem 0;
	}

	.slack-list {
		list-style: none;
		padding: 0;
		margin: 0 0 0.85rem 0;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.slack-row {
		display: grid;
		grid-template-columns: 30px 1fr auto;
		gap: 0.65rem;
		align-items: center;
		padding: 0.55rem 0.85rem 0.6rem 0.55rem;
		background: white;
		border: 1px solid var(--color-bot-border);
		border-left: 3px solid transparent;
		border-radius: 0 8px 8px 0;
	}

	.slack-row[data-kind='slack'] {
		border-left-color: var(--color-success, #2d9c6f);
	}

	.slack-row[data-kind='surplus'] {
		border-left-color: var(--color-warning, #d4a853);
	}

	.slack-row[data-kind='equality'] {
		border-left-color: var(--color-primary);
	}

	.slack-row[data-binding='true'] {
		background: linear-gradient(
			to right,
			rgba(212, 168, 83, 0.08),
			rgba(212, 168, 83, 0)
		);
	}

	.slack-marker {
		text-align: center;
	}

	.kind-tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 700;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 22px;
		height: 22px;
		border-radius: 50%;
		border: 1px solid currentColor;
	}

	.slack-tag {
		color: var(--color-success, #2d9c6f);
	}

	.surplus-tag {
		color: var(--color-warning, #d4a853);
	}

	.eq-tag {
		color: var(--color-primary);
	}

	.slack-body {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
		min-width: 0;
	}

	.slack-top {
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
		flex-wrap: wrap;
	}

	.r-label {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink);
		font-size: 0.85rem;
	}

	.r-eq {
		font-size: 0.85rem;
	}

	.slack-stat {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		font-size: 0.78rem;
		color: var(--color-ink-muted);
	}

	.sep {
		opacity: 0.5;
	}

	.verdict {
		color: var(--color-ink-light);
	}

	.verdict.bound {
		color: var(--color-accent);
		font-weight: 600;
	}

	.slack-value {
		font-family: var(--font-mono);
		font-weight: 700;
		font-size: 1.05rem;
		color: var(--color-ink);
		padding: 0.2rem 0.55rem;
		border-radius: 6px;
		background: var(--color-surface-warm);
	}

	.slack-value.zero {
		color: var(--color-accent);
		background: rgba(212, 168, 83, 0.15);
	}

	.restart-btn {
		width: 100%;
		padding: 0.75rem 1rem;
		background: transparent;
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		color: var(--color-ink-muted);
		font-family: var(--font-body);
		font-size: 0.85rem;
		cursor: pointer;
		transition: all 0.18s ease;
	}

	.restart-btn:hover {
		color: var(--color-ink);
		border-color: var(--color-ink);
		background: var(--color-surface-warm);
	}

	@media (max-width: 640px) {
		.interp {
			padding: 1.15rem 1rem 1.15rem 0.85rem;
		}
		.slack-row {
			grid-template-columns: 26px 1fr;
		}
		.slack-value {
			grid-column: 2;
			justify-self: end;
		}
	}
</style>
