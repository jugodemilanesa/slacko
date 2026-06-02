<script lang="ts">
	import { tick } from 'svelte';
	import { resetChat, sendAssistantMessage } from '$lib/stores/chat';
	import type { LPModel, SolverResult } from '$lib/stores/chat';
	import SlakingAvatar from '$lib/components/SlakingAvatar.svelte';
	import Latex from '$lib/components/Latex.svelte';
	import SlackoTip from '$lib/components/SlackoTip.svelte';
	import SolutionArtifacts from '$lib/components/SolutionArtifacts.svelte';
	import {
		objectiveLatex,
		constraintLatex,
		nonNegativityLatex
	} from '$lib/math/formula';

	// --- Tutorial model: balones de fútbol (x1) y juegos de ajedrez (x2) ---
	const model: LPModel = {
		enunciado:
			'Una empresa fabrica balones de fútbol y juegos de ajedrez. Cada balón aporta $2 de utilidad y cada juego de ajedrez aporta $4. Hay tres centros de maquinaria con horas limitadas y dos requisitos extra: producir al menos 15 balones y que los ajedrez representen al menos el 25% de la producción total.',
		sense: 'maximize',
		variables: [
			{ name: 'x1', label: 'balones de fútbol', coefficient: 2 },
			{ name: 'x2', label: 'juegos de ajedrez', coefficient: 4 }
		],
		constraints: [
			{ label: 'Centro A', coefficients: [4, 6], sign: '<=', rhs: 138 },
			{ label: 'Centro B', coefficients: [2, 6], sign: '<=', rhs: 96 },
			{ label: 'Centro C', coefficients: [0, 1], sign: '<=', rhs: 10 },
			{ label: 'Mínimo de balones', coefficients: [1, 0], sign: '>=', rhs: 15 },
			{
				label: 'Mezcla: ajedrez ≥ 25% del total',
				coefficients: [-0.25, 0.75],
				sign: '>=',
				rhs: 0
			}
		]
	};

	// Pre-computed optimal solution and vertices (from the worked example).
	const result: SolverResult = {
		vertices: [
			[15, 5],
			[15, 10],
			[18, 10],
			[21, 9],
			[23, 7.7]
		],
		feasible_vertices: [
			[15, 5],
			[15, 10],
			[18, 10],
			[21, 9],
			[23, 7.7]
		],
		optimal_point: [21, 9],
		optimal_value: 78,
		vertex_analysis: [
			{ x1: 15, x2: 5, z: 50 },
			{ x1: 15, x2: 10, z: 70 },
			{ x1: 18, x2: 10, z: 76 },
			{ x1: 21, x2: 9, z: 78 },
			{ x1: 23, x2: 7.7, z: 76.8 }
		]
	};

	// --- Conversation script. Each item is rendered as a turn (bot or user).
	type Beat =
		| { kind: 'bot'; text: string; expression?: 'happy' | 'thinking' | 'explain' | 'sad'; widget?: Widget }
		| { kind: 'user'; text: string }
		| { kind: 'widget'; widget: Widget };

	type Widget =
		| { type: 'enunciado' }
		| { type: 'variables' }
		| { type: 'objective' }
		| { type: 'constraints' }
		| { type: 'mixing-derivation' }
		| { type: 'standard-form' }
		| { type: 'graph-tutorial' }
		| { type: 'graph' }
		| { type: 'vertex-tutorial' }
		| { type: 'vertices' }
		| { type: 'interpretation' };

	const script: Beat[] = [
		{
			kind: 'bot',
			expression: 'happy',
			text: 'Bienvenido al recorrido guiado. Te voy a llevar por un problema clásico, ya resuelto, para que veas el flujo completo de principio a fin.'
		},
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Acá va el enunciado que vamos a trabajar:',
			widget: { type: 'enunciado' }
		},
		{ kind: 'user', text: 'Listo, ¿lo analizamos?' },
		{
			kind: 'bot',
			expression: 'thinking',
			text: 'Lo primero que nota Slacko: hay dos cantidades a decidir (balones y ajedrez), una utilidad lineal a maximizar y varias restricciones lineales. **Es un problema de Programación Lineal con dos variables** — perfecto para método gráfico.'
		},
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Empecemos por las **variables de decisión**:',
			widget: { type: 'variables' }
		},
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Cada balón aporta $2 y cada ajedrez $4. Queremos maximizar la utilidad, así que la **función objetivo** queda:',
			widget: { type: 'objective' }
		},
		{ kind: 'user', text: '¿Y las restricciones?' },
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Los tres centros de maquinaria nos dan tres restricciones de tipo ≤. Después hay un mínimo de balones (≥) y una de mezcla (proporción).',
			widget: { type: 'constraints' }
		},
		{
			kind: 'bot',
			expression: 'explain',
			text: 'La de mezcla la convertimos a forma de coeficientes así:',
			widget: { type: 'mixing-derivation' }
		},
		{
			kind: 'bot',
			expression: 'thinking',
			text: 'Para resolverlo necesitamos pasar a **forma estándar**, sumando slacks en las ≤ y restando surplus en las ≥:',
			widget: { type: 'standard-form' }
		},
		{ kind: 'user', text: 'Ahora sí, ¿al gráfico?' },
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Antes del gráfico, repasemos cómo se traza cada restricción a mano:',
			widget: { type: 'graph-tutorial' }
		},
		{
			kind: 'bot',
			expression: 'happy',
			text: 'Y así queda la **región factible** con las 5 restricciones y la recta de isoutilidad punteada en el óptimo:',
			widget: { type: 'graph' }
		},
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Vamos al **análisis de vértices**. Cada vértice del polígono es un candidato a óptimo.',
			widget: { type: 'vertex-tutorial' }
		},
		{
			kind: 'bot',
			expression: 'explain',
			text: 'Evaluando Z en cada vértice:',
			widget: { type: 'vertices' }
		},
		{
			kind: 'bot',
			expression: 'happy',
			text: 'El vértice con Z más alto es **(21, 9) con Z = 78**. Esa es la solución óptima.',
			widget: { type: 'interpretation' }
		}
	];

	let revealed = $state(1);
	let scrollEl = $state<HTMLDivElement | null>(null);

	async function reveal() {
		if (revealed >= script.length) return;
		revealed = Math.min(revealed + 1, script.length);
		await tick();
		if (scrollEl) {
			scrollEl.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' });
		}
	}

	async function revealAll() {
		revealed = script.length;
		await tick();
		if (scrollEl) {
			scrollEl.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' });
		}
	}

	async function backToStart() {
		resetChat();
		await sendAssistantMessage(
			'¿Cómo querés trabajar hoy?',
			{ delay: 400, expression: 'happy' }
		);
	}

	const done = $derived(revealed >= script.length);
</script>

<div class="tutorial-mode">
	<header class="tutorial-header">
		<div class="header-inner">
			<div class="header-left">
				<SlakingAvatar expression="explain" size="lg" ring floating />
				<div>
					<div class="overline">Tutorial · Ejemplo resuelto</div>
					<h1 class="title">
						<span class="drop">B</span>alones y ajedrez
					</h1>
					<p class="kicker">
						Un problema clásico de mezcla y producción con 2 variables, 5 restricciones y
						optimum en un vértice interior.
					</p>
				</div>
			</div>
			<div class="header-right">
				<div class="progress">
					<span class="progress-label">
						{revealed} / {script.length}
					</span>
					<div class="progress-bar" aria-hidden="true">
						<div
							class="progress-fill"
							style="width: {(revealed / script.length) * 100}%"
						></div>
					</div>
				</div>
				<button type="button" class="ghost-btn" onclick={revealAll} disabled={done}>
					Ver todo
				</button>
				<button type="button" class="ghost-btn" onclick={backToStart}>
					← Volver
				</button>
			</div>
		</div>
	</header>

	<div class="chat-stack" bind:this={scrollEl}>
		{#each script.slice(0, revealed) as beat, i (i)}
			{#if beat.kind === 'bot'}
				<div class="turn bot">
					<div class="avatar">
						<SlakingAvatar expression={beat.expression ?? 'explain'} size="sm" />
					</div>
					<div class="bot-content">
						<div class="bot-bubble">
							<p>
								{@html beat.text.replace(
									/\*\*(.*?)\*\*/g,
									'<strong>$1</strong>'
								)}
							</p>
						</div>
						{#if beat.widget}
							<div class="widget">
								{#if beat.widget.type === 'enunciado'}
									<article class="enunciado-card">
										<div class="card-overline">Enunciado</div>
										<p>{model.enunciado}</p>
									</article>
								{:else if beat.widget.type === 'variables'}
									<div class="vars-grid">
										{#each model.variables as v, vi}
											<div class="var-card">
												<div class="var-name">
													<Latex
														expr={vi === 0 ? 'x_1' : 'x_2'}
													/>
												</div>
												<div class="var-desc">
													cantidad de {v.label} a fabricar
												</div>
												<div class="var-coef">coef. en Z: {v.coefficient}</div>
											</div>
										{/each}
									</div>
								{:else if beat.widget.type === 'objective'}
									<div class="formula-card">
										<Latex expr={objectiveLatex(model)} display />
									</div>
								{:else if beat.widget.type === 'constraints'}
									<ol class="constraint-list">
										{#each model.constraints as c, ci}
											<li>
												<span class="r-tag">R{ci + 1}</span>
												<span class="r-eq">
													<Latex
														expr={constraintLatex(c, model.variables)}
													/>
												</span>
												<span class="r-label">— {c.label}</span>
											</li>
										{/each}
										<li class="non-neg">
											<span class="r-tag">+</span>
											<span class="r-eq">
												<Latex expr={nonNegativityLatex(model.variables)} />
											</span>
											<span class="r-label">— no negatividad</span>
										</li>
									</ol>
								{:else if beat.widget.type === 'mixing-derivation'}
									<SlackoTip kind="concept" title="De proporción a coeficientes">
										<p>El enunciado dice:</p>
										<div class="inline-tex">
											<Latex
												expr={`x_2 \\geq 0.25\\,(x_1 + x_2)`}
												display
											/>
										</div>
										<p>Distribuyendo y pasando al mismo lado:</p>
										<div class="inline-tex">
											<Latex
												expr={`x_2 - 0.25\\,x_1 - 0.25\\,x_2 \\geq 0 \\;\\Rightarrow\\; -0.25\\,x_1 + 0.75\\,x_2 \\geq 0`}
												display
											/>
										</div>
									</SlackoTip>
								{:else if beat.widget.type === 'standard-form'}
									<div class="standard-grid">
										<div class="std-row">
											<span class="r-tag">R1</span>
											<Latex expr="4x_1 + 6x_2 + s_1 = 138" />
										</div>
										<div class="std-row">
											<span class="r-tag">R2</span>
											<Latex expr="2x_1 + 6x_2 + s_2 = 96" />
										</div>
										<div class="std-row">
											<span class="r-tag">R3</span>
											<Latex expr="x_2 + s_3 = 10" />
										</div>
										<div class="std-row">
											<span class="r-tag">R4</span>
											<Latex expr="x_1 - e_4 = 15" />
										</div>
										<div class="std-row">
											<span class="r-tag">R5</span>
											<Latex
												expr={`-0.25\\,x_1 + 0.75\\,x_2 - e_5 = 0`}
											/>
										</div>
									</div>
								{:else if beat.widget.type === 'graph-tutorial'}
									<div class="mini-tutorial">
										<div class="mini-step">
											<span class="num">i.</span>
											<p>
												Para cada restricción, hacemos
												<code>x_1=0</code> y luego <code>x_2=0</code> para encontrar
												los puntos donde corta a los ejes.
											</p>
										</div>
										<div class="mini-step">
											<span class="num">ii.</span>
											<p>
												Trazamos cada recta y nos quedamos con el semiplano que
												satisface la desigualdad.
											</p>
										</div>
										<div class="mini-step">
											<span class="num">iii.</span>
											<p>
												La intersección de todos los semiplanos es la <strong
													>región factible</strong
												>. Para Max, la recta de isoutilidad se aleja del origen
												hasta el último vértice de contacto.
											</p>
										</div>
									</div>
								{:else if beat.widget.type === 'graph'}
									<SolutionArtifacts {model} {result} show="graph" variant="full" />
								{:else if beat.widget.type === 'vertex-tutorial'}
									<SlackoTip kind="tip" title="Cómo se completa el cuadro">
										<ul>
											<li>
												En cada vértice, las <strong>dos rectas que se cruzan</strong>
												tienen su slack en cero.
											</li>
											<li>
												Las otras slacks se obtienen reemplazando
												<code>(x_1, x_2)</code> en cada restricción.
											</li>
											<li>
												Evaluamos <code>Z = 2x_1 + 4x_2</code> en cada fila y
												nos quedamos con el valor más alto.
											</li>
										</ul>
									</SlackoTip>
								{:else if beat.widget.type === 'vertices'}
									<SolutionArtifacts
										{model}
										{result}
										show="vertices"
										variant="full"
									/>
								{:else if beat.widget.type === 'interpretation'}
									<div class="final-card">
										<div class="final-grid">
											<div class="kpi">
												<div class="kpi-label">Balones</div>
												<div class="kpi-value">21</div>
												<div class="kpi-meta">x_1</div>
											</div>
											<div class="kpi">
												<div class="kpi-label">Ajedrez</div>
												<div class="kpi-value">9</div>
												<div class="kpi-meta">x_2</div>
											</div>
											<div class="kpi z">
												<div class="kpi-label">Utilidad óptima</div>
												<div class="kpi-value">$78</div>
												<div class="kpi-meta">Z</div>
											</div>
										</div>
										<p class="closing">
											Conviene fabricar <strong>21 balones y 9 juegos de
											ajedrez</strong>. Los centros A y B quedan exactamente saturados
											(slack = 0); el centro C tiene <strong>1 hora ociosa</strong>;
											se fabrican <strong>6 balones por encima del mínimo</strong>;
											y los ajedrez representan un poco más del 25% de la producción
											total.
										</p>
									</div>
								{/if}
							</div>
						{/if}
					</div>
				</div>
			{:else if beat.kind === 'user'}
				<div class="turn user">
					<div class="user-bubble">
						<span class="meta">Vos</span>
						<p>{beat.text}</p>
					</div>
				</div>
			{/if}
		{/each}

		{#if done}
			<div class="end-card">
				<div class="end-ornament" aria-hidden="true">❦</div>
				<p class="end-msg">
					Llegaste al final del recorrido. Ahora podés intentar uno propio en
					<em>Paso a paso</em>.
				</p>
				<div class="end-actions">
					<button class="primary-btn" onclick={backToStart}>
						Resolver mi propio problema
					</button>
				</div>
			</div>
		{/if}
	</div>

	{#if !done}
		<div class="composer">
			<button class="next-btn" onclick={reveal}>
				Siguiente
				<span class="arrow">↓</span>
			</button>
			<p class="composer-hint">
				Tomate tu tiempo para leer cada paso. Cuando estés listo, avanzá.
			</p>
		</div>
	{/if}
</div>

<style>
	.tutorial-mode {
		max-width: 880px;
		margin: 0 auto;
		padding: 1.5rem 1.25rem 2rem 1.25rem;
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.tutorial-header {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		padding: 1.1rem 1.4rem;
		margin-bottom: 1rem;
		position: relative;
		overflow: hidden;
	}

	.tutorial-header::before {
		content: '';
		position: absolute;
		inset: 0 auto 0 0;
		width: 4px;
		background: linear-gradient(
			180deg,
			var(--color-accent),
			var(--color-primary)
		);
	}

	.header-inner {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: 1.25rem;
		align-items: center;
	}

	.header-left {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: 0.15rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: 1.65rem;
		line-height: 1;
		margin: 0 0 0.2rem 0;
		color: var(--color-ink);
	}

	.drop {
		color: var(--color-accent);
		font-size: 1.4em;
		float: left;
		line-height: 0.85;
		padding-right: 0.18em;
	}

	.kicker {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.88rem;
		margin: 0;
		clear: both;
	}

	.header-right {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.5rem;
	}

	.progress {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.25rem;
	}

	.progress-label {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		letter-spacing: 0.18em;
		color: var(--color-ink-muted);
	}

	.progress-bar {
		width: 120px;
		height: 3px;
		background: var(--color-bot-border);
		border-radius: 2px;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(
			to right,
			var(--color-primary),
			var(--color-accent)
		);
		transition: width 0.35s ease;
	}

	.ghost-btn {
		font-family: var(--font-body);
		font-size: 0.75rem;
		color: var(--color-ink-muted);
		background: transparent;
		border: 1px solid var(--color-bot-border);
		padding: 0.35rem 0.8rem;
		border-radius: 999px;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.ghost-btn:hover:not(:disabled) {
		color: var(--color-ink);
		border-color: var(--color-ink);
	}

	.ghost-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.chat-stack {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		max-height: calc(100vh - 16rem);
		overflow-y: auto;
		padding: 0.5rem 0.25rem 1rem 0.25rem;
		scroll-behavior: smooth;
	}

	.chat-stack::-webkit-scrollbar {
		width: 8px;
	}
	.chat-stack::-webkit-scrollbar-track {
		background: transparent;
	}
	.chat-stack::-webkit-scrollbar-thumb {
		background: var(--color-bot-border);
		border-radius: 4px;
	}

	.turn {
		display: flex;
		gap: 0.6rem;
		animation: fadeUp 0.32s ease-out;
	}

	.turn.user {
		justify-content: flex-end;
	}

	.turn.bot {
		align-items: flex-start;
	}

	.avatar {
		flex-shrink: 0;
		padding-top: 0.2rem;
	}

	.bot-content {
		flex: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.bot-bubble {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px 14px 14px 4px;
		padding: 0.75rem 1rem;
	}

	.bot-bubble p {
		margin: 0;
		font-family: var(--font-body);
		font-size: 0.92rem;
		line-height: 1.55;
		color: var(--color-ink);
	}

	.bot-bubble :global(strong) {
		color: var(--color-primary);
		font-weight: 600;
	}

	.user-bubble {
		max-width: 70%;
		background: var(--color-primary);
		color: white;
		padding: 0.65rem 1rem;
		border-radius: 14px 14px 4px 14px;
		box-shadow: 0 4px 14px -8px rgba(26, 26, 46, 0.25);
	}

	.user-bubble .meta {
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		opacity: 0.8;
		display: block;
		margin-bottom: 0.2rem;
	}

	.user-bubble p {
		margin: 0;
		font-size: 0.9rem;
		line-height: 1.45;
	}

	.widget {
		animation: fadeUp 0.4s ease-out 0.05s both;
	}

	/* Widgets */
	.enunciado-card {
		background: linear-gradient(
			180deg,
			var(--color-surface-warm, #fff7e8),
			var(--color-surface-card, #fffaf2)
		);
		border: 1px solid var(--color-bot-border);
		border-left: 3px solid var(--color-accent);
		border-radius: 0 8px 8px 0;
		padding: 0.85rem 1rem 0.95rem 1rem;
	}

	.card-overline {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: 0.35rem;
	}

	.enunciado-card p {
		font-family: var(--font-display);
		font-size: 0.98rem;
		line-height: 1.65;
		color: var(--color-ink);
		margin: 0;
	}

	.vars-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.6rem;
	}

	.var-card {
		padding: 0.75rem 0.9rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
	}

	.var-name {
		font-size: 1.1rem;
		color: var(--color-primary);
	}

	.var-desc {
		font-family: var(--font-body);
		font-size: 0.85rem;
		color: var(--color-ink-light);
		line-height: 1.4;
	}

	.var-coef {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		color: var(--color-accent);
	}

	.formula-card {
		padding: 0.85rem 1rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		border-left: 3px solid var(--color-accent);
	}

	.constraint-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.constraint-list li {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		padding: 0.45rem 0.75rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-left: 3px solid var(--color-primary);
		border-radius: 0 6px 6px 0;
		flex-wrap: wrap;
	}

	.constraint-list li.non-neg {
		border-left-color: var(--color-accent);
		background: var(--color-surface-warm);
	}

	.r-tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--color-primary);
		letter-spacing: 0.1em;
		min-width: 24px;
	}

	.r-eq {
		font-size: 0.9rem;
	}

	.r-label {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.78rem;
		margin-left: auto;
	}

	.standard-grid {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		padding: 0.75rem;
		background: var(--color-surface-warm, #fff7e8);
		border-radius: 8px;
		border: 1px dashed var(--color-bot-border);
	}

	.std-row {
		display: flex;
		align-items: baseline;
		gap: 0.7rem;
		padding: 0.3rem 0.5rem;
	}

	.std-row + .std-row {
		border-top: 1px dotted var(--color-bot-border);
		padding-top: 0.45rem;
	}

	.inline-tex {
		padding: 0.4rem 0;
	}

	.mini-tutorial {
		display: flex;
		flex-direction: column;
		gap: 0.45rem;
		padding: 0.85rem 1rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
	}

	.mini-step {
		display: grid;
		grid-template-columns: 28px 1fr;
		gap: 0.5rem;
		font-family: var(--font-body);
		font-size: 0.88rem;
		line-height: 1.55;
		color: var(--color-ink-light);
	}

	.mini-step + .mini-step {
		border-top: 1px dotted var(--color-bot-border);
		padding-top: 0.45rem;
	}

	.mini-step .num {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-accent);
		font-size: 1rem;
	}

	.mini-step p {
		margin: 0;
	}

	.mini-step code {
		font-family: var(--font-mono);
		font-size: 0.82em;
		background: rgba(26, 26, 46, 0.05);
		padding: 0.05em 0.4em;
		border-radius: 3px;
	}

	.final-card {
		background: linear-gradient(
			180deg,
			rgba(212, 168, 83, 0.12),
			rgba(212, 168, 83, 0.02)
		);
		border: 1px solid rgba(212, 168, 83, 0.4);
		border-radius: 12px;
		padding: 1rem 1.1rem 1.1rem 1.1rem;
		display: flex;
		flex-direction: column;
		gap: 0.8rem;
	}

	.final-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.6rem;
	}

	.kpi {
		text-align: center;
		padding: 0.6rem 0.5rem 0.7rem 0.5rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
	}

	.kpi.z {
		background: var(--color-ink);
		color: var(--color-surface-card);
		border-color: var(--color-ink);
	}

	.kpi-label {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.75rem;
		color: var(--color-ink-muted);
		margin-bottom: 0.25rem;
	}

	.kpi.z .kpi-label {
		color: color-mix(in srgb, var(--color-surface-card) 70%, transparent);
	}

	.kpi-value {
		font-family: var(--font-mono);
		font-size: 1.55rem;
		font-weight: 700;
		color: var(--color-primary);
		line-height: 1;
	}

	.kpi.z .kpi-value {
		color: var(--color-accent);
		font-size: 1.85rem;
	}

	.kpi-meta {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-top: 0.2rem;
	}

	.kpi.z .kpi-meta {
		color: color-mix(in srgb, var(--color-surface-card) 50%, transparent);
	}

	.closing {
		font-family: var(--font-body);
		font-size: 0.9rem;
		line-height: 1.6;
		color: var(--color-ink);
		margin: 0;
	}

	.closing strong {
		color: var(--color-primary);
		font-weight: 600;
	}

	.end-card {
		text-align: center;
		padding: 2rem 1.5rem 2.25rem 1.5rem;
		background: var(--color-surface-card);
		border: 1px dashed var(--color-bot-border);
		border-radius: 14px;
		margin-top: 0.5rem;
	}

	.end-ornament {
		font-family: var(--font-display);
		font-size: 1.6rem;
		color: var(--color-accent);
		margin-bottom: 0.5rem;
	}

	.end-msg {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-light);
		margin: 0 0 1rem 0;
	}

	.end-actions {
		display: flex;
		justify-content: center;
	}

	.primary-btn {
		padding: 0.7rem 1.2rem;
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: 10px;
		font-family: var(--font-body);
		font-size: 0.88rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.18s ease;
	}

	.primary-btn:hover {
		background: var(--color-primary-dark, #2d3a9a);
		transform: translateY(-1px);
	}

	.composer {
		margin-top: 0.8rem;
		padding-top: 0.85rem;
		border-top: 1px solid var(--color-bot-border);
		text-align: center;
	}

	.next-btn {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.7rem 1.5rem;
		background: var(--color-ink);
		color: var(--color-surface-card);
		border: none;
		border-radius: 999px;
		font-family: var(--font-body);
		font-size: 0.85rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.next-btn:hover {
		background: var(--color-primary);
		transform: translateY(-2px);
		box-shadow: 0 8px 22px -10px color-mix(in srgb, var(--color-primary) 50%, transparent);
	}

	.next-btn .arrow {
		font-family: var(--font-display);
		transition: transform 0.25s ease-in-out;
	}

	.next-btn:hover .arrow {
		transform: translateX(3px);
	}

	.composer-hint {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		margin: 0.5rem 0 0 0;
	}

	@keyframes fadeUp {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 720px) {
		.header-inner {
			grid-template-columns: 1fr;
		}
		.header-right {
			align-items: flex-start;
		}
		.vars-grid,
		.final-grid {
			grid-template-columns: 1fr;
		}
		.user-bubble {
			max-width: 85%;
		}
		.r-label {
			margin-left: 0;
			width: 100%;
		}
	}
</style>
