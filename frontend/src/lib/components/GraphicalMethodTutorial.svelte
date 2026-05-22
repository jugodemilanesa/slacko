<script lang="ts">
	import type { LPModel } from '$lib/stores/chat';
	import { constraintLatex, objectiveLatex } from '$lib/math/formula';
	import Latex from './Latex.svelte';
	import SlackoTip from './SlackoTip.svelte';
	import SlakingAvatar from './SlakingAvatar.svelte';

	let {
		model,
		onContinue
	}: {
		model: LPModel;
		onContinue: () => void;
	} = $props();

	function fmt(n: number): string {
		if (Number.isInteger(n)) return n.toString();
		return n.toFixed(2).replace(/\.?0+$/, '');
	}

	function intersections(c: { coefficients: number[]; rhs: number }) {
		const a = c.coefficients[0];
		const b = c.coefficients[1];
		const eps = 1e-9;
		const points: { axis: 'x1' | 'x2' | 'parallel'; value: string; tex: string }[] = [];

		if (Math.abs(a) < eps && Math.abs(b) < eps) return points;

		// x2 = 0 → x1 = rhs/a
		if (Math.abs(a) > eps) {
			const x1 = c.rhs / a;
			points.push({
				axis: 'x1',
				value: `(${fmt(x1)},\\,0)`,
				tex: `${fmt(a)}\\,x_1 = ${fmt(c.rhs)} \\;\\Rightarrow\\; x_1 = ${fmt(x1)}`
			});
		} else {
			points.push({
				axis: 'parallel',
				value: 'paralela al eje x_1',
				tex: 'recta paralela al eje x_1'
			});
		}

		// x1 = 0 → x2 = rhs/b
		if (Math.abs(b) > eps) {
			const x2 = c.rhs / b;
			points.push({
				axis: 'x2',
				value: `(0,\\,${fmt(x2)})`,
				tex: `${fmt(b)}\\,x_2 = ${fmt(c.rhs)} \\;\\Rightarrow\\; x_2 = ${fmt(x2)}`
			});
		} else {
			points.push({
				axis: 'parallel',
				value: 'paralela al eje x_2',
				tex: 'recta paralela al eje x_2'
			});
		}

		return points;
	}

	const objLatex = $derived(objectiveLatex(model));
</script>

<article class="tutorial">
	<aside class="spine">
		<div class="spine-rule"></div>
		<div class="spine-meta">Lección</div>
		<div class="spine-num">01</div>
	</aside>

	<div class="body">
		<header class="lead">
			<div class="overline">Antes de ver el gráfico</div>
			<h2 class="title">
				<span class="drop">M</span>étodo gráfico, paso a paso
			</h2>
			<p class="kicker">
				Antes de que dibuje yo, te explico cómo lo harías a mano para que entiendas
				lo que vas a ver.
			</p>
		</header>

		<section class="step">
			<div class="step-marker">
				<span class="num">i</span>
			</div>
			<div class="step-content">
				<h3 class="step-title">Cada restricción se traza como recta</h3>
				<p>
					Para graficar una restricción la igualamos (consideramos su <em>slack</em>
					en cero) y buscamos los dos puntos donde corta a los ejes:
				</p>
				<ul class="bullets">
					<li>Hacé <code>x₁ = 0</code> para obtener el corte con el eje vertical.</li>
					<li>Hacé <code>x₂ = 0</code> para obtener el corte con el eje horizontal.</li>
					<li>Uní ambos puntos: esa es tu recta.</li>
				</ul>

				<SlackoTip kind="concept" title="¿Por qué slack = 0?">
					<p>
						Una restricción del tipo <code>a₁x₁ + a₂x₂ ≤ b</code> con su variable
						slack queda como <code>a₁x₁ + a₂x₂ + s = b</code>. La <em>frontera</em>
						(la recta misma) corresponde a <code>s = 0</code>: ahí el recurso está
						justo agotado.
					</p>
				</SlackoTip>
			</div>
		</section>

		<section class="step">
			<div class="step-marker">
				<span class="num">ii</span>
			</div>
			<div class="step-content">
				<h3 class="step-title">Cortes con los ejes de tus restricciones</h3>
				<p>
					Con los números <strong>de tu problema</strong>, los cortes son:
				</p>

				<ol class="worked">
					{#each model.constraints as c, i}
						{@const pts = intersections(c)}
						<li>
							<div class="worked-head">
								<span class="r-tag">R{i + 1}</span>
								<span class="r-label">{c.label || `Restricción ${i + 1}`}</span>
								<span class="r-eq"><Latex expr={constraintLatex(c, model.variables)} /></span>
							</div>
							<div class="worked-body">
								{#each pts as p}
									<div class="point-row">
										<span class="point-bullet" aria-hidden="true">◆</span>
										<Latex expr={p.tex} />
										{#if p.axis !== 'parallel'}
											<span class="point-coord">
												<Latex expr={p.value} />
											</span>
										{/if}
									</div>
								{/each}
							</div>
						</li>
					{/each}
				</ol>
			</div>
		</section>

		<section class="step">
			<div class="step-marker">
				<span class="num">iii</span>
			</div>
			<div class="step-content">
				<h3 class="step-title">Función objetivo: recta de isoutilidad</h3>
				<p>
					Tu función objetivo es:
				</p>
				<Latex expr={objLatex} display />
				<p>
					La idea es trazarla para un valor cualquiera de <em>Z</em> (por ejemplo
					<code>Z = 0</code>) y luego desplazarla en paralelo —
					{model.sense === 'maximize' ? 'alejándola' : 'acercándola'} del origen — hasta
					tocar el último (o primer) vértice de la región factible.
				</p>

				<SlackoTip kind="tip" title="Cómo desplazar la recta">
					<p>
						Despejá <code>x₂</code> en función de <code>x₁</code>: te queda una recta con pendiente
						fija. Cambiando solo el término independiente (probá Z = 0, Z = 10, Z = 20…)
						la recta se mueve manteniendo su inclinación.
					</p>
				</SlackoTip>
			</div>
		</section>

		<section class="step">
			<div class="step-marker">
				<span class="num">iv</span>
			</div>
			<div class="step-content">
				<h3 class="step-title">La región factible es la intersección</h3>
				<p>
					Cada desigualdad define un semiplano. La <strong>región factible</strong>
					es donde se cumplen todas a la vez — el polígono sombreado que vas a ver.
				</p>

				<SlackoTip kind="warning" title="Las desigualdades importan">
					<p>
						Para decidir de qué lado de cada recta cae el semiplano, probá con el origen
						<code>(0, 0)</code>: si satisface la desigualdad, sombreá ese lado;
						si no, el opuesto.
					</p>
				</SlackoTip>
			</div>
		</section>

		<footer class="cta-row">
			<div class="cta-text">
				<SlakingAvatar expression="explain" size="sm" />
				<p>Cuando estés listo, te muestro el gráfico con la región factible coloreada.</p>
			</div>
			<button type="button" class="cta-btn" onclick={onContinue}>
				Mostrame el gráfico
				<span class="arrow" aria-hidden="true">→</span>
			</button>
		</footer>
	</div>
</article>

<style>
	.tutorial {
		display: grid;
		grid-template-columns: 64px 1fr;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		overflow: hidden;
		box-shadow: 0 1px 0 rgba(26, 26, 46, 0.02),
			0 18px 38px -22px rgba(26, 26, 46, 0.22);
		animation: fadeUp 0.3s ease-out;
	}

	.spine {
		background: linear-gradient(
			180deg,
			rgba(212, 168, 83, 0.1),
			rgba(59, 76, 192, 0.05) 60%,
			rgba(212, 168, 83, 0.08)
		);
		border-right: 1px solid var(--color-bot-border);
		padding: 1.5rem 0.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.5rem;
	}

	.spine-rule {
		width: 1px;
		flex: 1;
		background: var(--color-accent);
		opacity: 0.35;
		margin-top: 0.5rem;
	}

	.spine-meta {
		writing-mode: vertical-rl;
		transform: rotate(180deg);
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--color-accent);
	}

	.spine-num {
		font-family: var(--font-display);
		font-size: 1.6rem;
		color: var(--color-accent);
		opacity: 0.8;
		line-height: 1;
	}

	.body {
		padding: 1.75rem 2rem 1.5rem 1.5rem;
	}

	.lead {
		margin-bottom: 1.5rem;
		border-bottom: 1px dashed var(--color-bot-border);
		padding-bottom: 1rem;
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: 0.4rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: clamp(1.6rem, 2.4vw, 2.2rem);
		line-height: 1.05;
		color: var(--color-ink);
		margin: 0 0 0.5rem 0;
		letter-spacing: -0.01em;
	}

	.drop {
		color: var(--color-accent);
		font-size: 1.45em;
		float: left;
		line-height: 0.85;
		padding-right: 0.18em;
	}

	.kicker {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-light);
		font-size: 1rem;
		margin: 0;
		line-height: 1.5;
	}

	.step {
		display: grid;
		grid-template-columns: 44px 1fr;
		gap: 0.85rem;
		padding: 1.1rem 0;
		border-bottom: 1px dashed var(--color-bot-border);
	}
	.step:last-of-type {
		border-bottom: none;
	}

	.step-marker {
		display: flex;
		justify-content: center;
		padding-top: 0.1rem;
	}

	.num {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 1.05rem;
		color: var(--color-accent);
		width: 30px;
		height: 30px;
		border-radius: 50%;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		border: 1px solid var(--color-accent);
		background: var(--color-surface-warm, #fffaf2);
		letter-spacing: 0;
	}

	.step-title {
		font-family: var(--font-display);
		font-size: 1.15rem;
		color: var(--color-ink);
		margin: 0 0 0.4rem 0;
		line-height: 1.2;
	}

	.step-content p {
		font-family: var(--font-body);
		font-size: 0.92rem;
		line-height: 1.6;
		color: var(--color-ink-light);
		margin: 0 0 0.65rem 0;
	}

	.step-content code {
		font-family: var(--font-mono);
		font-size: 0.85em;
		background: rgba(26, 26, 46, 0.05);
		padding: 0.05em 0.4em;
		border-radius: 3px;
		color: var(--color-ink);
	}

	.bullets {
		margin: 0.25rem 0 0.85rem 0;
		padding-left: 1.1rem;
		font-size: 0.9rem;
		color: var(--color-ink-light);
	}
	.bullets li {
		margin-bottom: 0.25rem;
	}

	.worked {
		list-style: none;
		padding: 0;
		margin: 0.4rem 0 0.85rem 0;
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.worked > li {
		background: var(--color-surface-warm, #fffaf2);
		border: 1px solid var(--color-bot-border);
		border-left: 3px solid var(--color-primary);
		border-radius: 0 6px 6px 0;
		padding: 0.7rem 0.9rem 0.8rem 0.85rem;
	}

	.worked-head {
		display: flex;
		align-items: baseline;
		gap: 0.55rem;
		flex-wrap: wrap;
		margin-bottom: 0.4rem;
	}

	.r-tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--color-primary);
		letter-spacing: 0.1em;
	}

	.r-label {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.85rem;
	}

	.r-eq {
		margin-left: auto;
	}

	.worked-body {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		padding-left: 0.3rem;
	}

	.point-row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		flex-wrap: wrap;
		font-size: 0.88rem;
	}

	.point-bullet {
		color: var(--color-accent);
		font-size: 0.55rem;
	}

	.point-coord {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-primary);
		margin-left: auto;
		padding: 0.1rem 0.5rem;
		background: rgba(59, 76, 192, 0.06);
		border-radius: 4px;
	}

	.cta-row {
		margin-top: 1.25rem;
		padding-top: 1rem;
		border-top: 1px solid var(--color-bot-border);
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.cta-text {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex: 1;
		min-width: 200px;
	}

	.cta-text p {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-light);
		margin: 0;
		font-size: 0.9rem;
	}

	.cta-btn {
		font-family: var(--font-body);
		font-size: 0.85rem;
		font-weight: 500;
		background: var(--color-ink);
		color: white;
		border: none;
		padding: 0.7rem 1.2rem;
		border-radius: 999px;
		cursor: pointer;
		transition: all 0.18s ease;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.cta-btn:hover {
		background: var(--color-primary);
		transform: translateY(-1px);
		box-shadow: 0 6px 14px -6px rgba(59, 76, 192, 0.4);
	}

	.cta-btn:hover .arrow {
		transform: translateX(3px);
	}

	.arrow {
		font-family: var(--font-display);
		transition: transform 0.18s ease;
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

	@media (max-width: 640px) {
		.tutorial {
			grid-template-columns: 40px 1fr;
		}
		.body {
			padding: 1.25rem 1rem 1.1rem 0.9rem;
		}
		.spine {
			padding: 1rem 0.3rem;
		}
		.r-eq {
			margin-left: 0;
			width: 100%;
		}
		.point-coord {
			margin-left: 0;
		}
	}
</style>
