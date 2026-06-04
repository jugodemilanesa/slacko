<script lang="ts">
	import SlackoTip from './SlackoTip.svelte';
	import SlakingAvatar from './SlakingAvatar.svelte';

	let {
		onContinue,
		sense = 'maximize'
	}: {
		onContinue: () => void;
		sense?: 'maximize' | 'minimize';
	} = $props();

	const goalWord = $derived(sense === 'maximize' ? 'mayor' : 'menor');
</script>

<article class="tutorial">
	<div class="body">
		<header class="lead">
			<div class="super-title">Antes del análisis de vértices</div>
			<h2 class="title">
				<span class="drop">L</span>os vértices, uno por uno
			</h2>
			<p class="kicker">
				Una vez trazada la región factible, el óptimo —si existe— está siempre en
				uno de sus vértices. Te muestro cómo se arma el cuadro.
			</p>
		</header>

		<section class="rule-list">
			<div class="rule-item">
				<span class="dot">①</span>
				<div>
					<strong>Cada vértice nace de la intersección de dos rectas</strong> que
					definen la frontera de la región factible.
				</div>
			</div>
			<div class="rule-item">
				<span class="dot">②</span>
				<div>
					En el cuadro, las <strong>rectas que intersectan en ese vértice</strong>
					tienen su variable <em>slack</em> igual a <code>0</code> (el recurso está
					agotado).
				</div>
			</div>
			<div class="rule-item">
				<span class="dot">③</span>
				<div>
					Las <strong>slack de las otras restricciones</strong> se calculan reemplazando
					<code>(x₁, x₂)</code> del vértice en cada restricción —
					la diferencia con el RHS es la holgura.
				</div>
			</div>
			<div class="rule-item">
				<span class="dot">④</span>
				<div>
					Evaluá <code>Z</code> en cada vértice. El que tenga el valor
					<strong>{goalWord}</strong> es la solución óptima del problema.
				</div>
			</div>
		</section>

		<SlackoTip kind="tip" title="Cómo se ve el cuadro">
			<p>
				Vas a tener algo así: una fila por vértice, columnas para <code>x₁</code>,
				<code>x₂</code>, una columna por cada slack <code>s_i</code> (en 0 cuando
				la recta corresponde al vértice, positiva si sobra), y la columna de
				<code>Z</code>. La fila con <code>Z</code> {goalWord} es la ganadora.
			</p>
		</SlackoTip>

		<SlackoTip kind="question" title="Para pensar">
			<p>
				¿Por qué basta con revisar solo los vértices, y no todos los puntos del
				interior de la región? <em>Pista:</em> la función objetivo es lineal —
				su valor extremo sobre un polígono convexo siempre cae en un vértice.
			</p>
		</SlackoTip>

		<footer class="cta-row">
			<div class="cta-text">
				<SlakingAvatar expression="explain" size="sm" />
				<p>Listo. Acá abajo te muestro el cuadro y marco el vértice óptimo.</p>
			</div>
			<button type="button" class="cta-btn" onclick={onContinue}>
				Ver el cuadro de vértices
				<span class="arrow" aria-hidden="true">→</span>
			</button>
		</footer>
	</div>
</article>

<style>
	.tutorial {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		overflow: hidden;
		box-shadow: 0 1px 0 rgba(26, 26, 46, 0.02),
			0 18px 38px -22px rgba(26, 26, 46, 0.22);
		animation: fadeUp 0.3s ease-out;
	}


	.body {
		padding: 1.75rem 2rem 1.5rem 1.5rem;
	}

	.lead {
		margin-bottom: 1.25rem;
		border-bottom: 1px dashed var(--color-bot-border);
		padding-bottom: 1rem;
	}

	.super-title {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-primary);
		margin-bottom: 0.4rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: clamp(1.6rem, 2.4vw, 2.2rem);
		line-height: 1.05;
		color: var(--color-ink);
		margin: 0 0 0.5rem 0;
	}

	.drop {
		color: var(--color-primary);
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

	.rule-list {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
		margin-bottom: 1rem;
	}

	.rule-item {
		display: grid;
		grid-template-columns: 28px 1fr;
		gap: 0.7rem;
		align-items: start;
		padding: 0.55rem 0;
		font-size: 0.92rem;
		color: var(--color-ink-light);
		line-height: 1.55;
	}

	.rule-item + .rule-item {
		border-top: 1px dotted var(--color-bot-border);
	}

	.dot {
		font-family: var(--font-display);
		font-size: 1.2rem;
		color: var(--color-accent);
		line-height: 1;
		padding-top: 0.05em;
	}

	.rule-item strong {
		color: var(--color-ink);
		font-weight: 600;
	}

	.rule-item em {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-primary);
	}

	code {
		font-family: var(--font-mono);
		font-size: 0.82em;
		background: rgba(26, 26, 46, 0.05);
		padding: 0.05em 0.4em;
		border-radius: 3px;
		color: var(--color-ink);
	}

	.cta-row {
		margin-top: 1rem;
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
		background-color: var(--color-surface-card);
		color: var(--color-ink);
		border: 1px solid var(--color-bot-border);
		padding: 0.7rem 1.2rem;
		border-radius: 999px;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}

	.cta-btn:hover {
		background-color: var(--color-primary);
		color: white;
		border-color: var(--color-primary);
		transform: translateY(-1px);
		box-shadow: 0 6px 14px -6px color-mix(in srgb, var(--color-primary) 40%, transparent);
	}

	.cta-btn:hover .arrow {
		transform: translateX(3px);
	}

	.arrow {
		font-family: var(--font-display);
		transition: transform 0.25s ease-in-out;
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
		.body {
			padding: 1.25rem 1rem 1.1rem 0.9rem;
		}
	}
</style>
