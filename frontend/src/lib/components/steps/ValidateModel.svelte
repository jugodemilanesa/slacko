<script lang="ts">
	import {
		model,
		addMessage,
		advanceState,
		goToState,
		sendAssistantMessage,
		addTip
	} from '$lib/stores/chat';
	import Latex from '$lib/components/Latex.svelte';
	import {
		objectiveLatex,
		constraintLatex,
		nonNegativityLatex
	} from '$lib/math/formula';

	async function confirm() {
		addMessage('user', 'Confirmo, resolver');
		advanceState();
		await sendAssistantMessage('Convirtiendo a **forma estándar**...', {
			delay: 700,
			expression: 'thinking'
		});
	}

	async function edit() {
		addMessage('user', 'Quiero editar las restricciones');
		goToState('BUILD_CONSTRAINTS');
		await sendAssistantMessage(
			'Dale, podés editar cualquier restricción con el lápiz, o quitarla con la cruz. Las que ya cargaste quedan intactas.',
			{ delay: 500, expression: 'idle' }
		);
	}

	$effect(() => {
		addTip('warning', 'Antes de confirmar, chequeá: ¿los coeficientes coinciden con el enunciado? ¿cada restricción tiene el signo correcto? ¿no falta ninguna restricción implícita?', 'Antes de confirmar, chequeá esto');
	});
</script>

<div class="step-enter">
	<article class="model-card">
		<header class="head">
			<span class="overline">Modelo completo</span>
			<h2 class="title"><span class="drop">A</span>ntes de resolver</h2>
			<p class="kicker">Revisalo bien — vas a poder editarlo si algo no cuadra.</p>
		</header>

		<section class="block">
			<div class="block-label">
				<span class="block-glyph">f</span>
				Función objetivo
			</div>
			<div class="formula">
				<Latex expr={objectiveLatex($model)} display />
			</div>
		</section>

		<section class="block">
			<div class="block-label">
				<span class="block-glyph">x</span>
				Variables de decisión
			</div>
			<ul class="var-list">
				{#each $model.variables as v}
					<li>
						<span class="var-name">{v.name}</span>
						<span class="var-eq">=</span>
						<span class="var-label">{v.label || 'sin nombre'}</span>
					</li>
				{/each}
			</ul>
		</section>

		<section class="block">
			<div class="block-label">
				<span class="block-glyph">R</span>
				Restricciones
			</div>
			<ol class="constraint-list">
				{#each $model.constraints as c, i}
					<li>
						<span class="r-tag">R{i + 1}</span>
						<span class="r-eq">
							<Latex expr={constraintLatex(c, $model.variables)} />
						</span>
						{#if c.label}
							<span class="r-label">— {c.label}</span>
						{/if}
					</li>
				{/each}
			</ol>
		</section>

		<section class="block">
			<div class="block-label">
				<span class="block-glyph">⊕</span>
				No negatividad
			</div>
			<div class="formula muted">
				<Latex expr={nonNegativityLatex($model.variables)} display />
			</div>
		</section>
	</article>

	<div class="actions">
		<button onclick={edit} class="btn-secondary">
			Editar
		</button>
		<button onclick={confirm} class="btn-primary">
			Confirmar y resolver
		</button>
	</div>
</div>

<style>
	.model-card {
		background: var(--color-surface-card, #fffaf2);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		padding: 1.4rem 1.6rem 1.4rem 1.4rem;
		margin-bottom: 0.85rem;
		position: relative;
	}

	.model-card::before {
		content: '';
		position: absolute;
		inset: 0 auto 0 0;
		width: 3px;
		background: var(--color-primary);
		border-radius: 14px 0 0 14px;
	}

	.head {
		margin-bottom: 1rem;
		padding-bottom: 0.65rem;
		border-bottom: 1px dashed var(--color-bot-border);
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-primary);
		display: block;
		margin-bottom: 0.25rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: 1.55rem;
		line-height: 1.05;
		margin: 0 0 0.3rem 0;
		color: var(--color-ink);
	}

	.drop {
		color: var(--color-primary);
		font-size: 1.4em;
		float: left;
		line-height: 0.85;
		padding-right: 0.18em;
	}

	.kicker {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.92rem;
		margin: 0;
		clear: both;
	}

	.block {
		padding: 0.6rem 0;
		border-bottom: 1px dotted var(--color-bot-border);
	}

	.block:last-child {
		border-bottom: none;
	}

	.block-label {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-bottom: 0.35rem;
	}

	.block-glyph {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 18px;
		height: 18px;
		border-radius: 3px;
		background: rgba(59, 76, 192, 0.08);
		color: var(--color-primary);
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.75rem;
		letter-spacing: 0;
	}

	.formula {
		padding: 0.5rem 0.75rem;
		background: var(--color-surface-card);
		border-radius: 6px;
		border: 1px solid var(--color-bot-border);
	}

	.formula.muted {
		background: transparent;
		border-color: transparent;
		padding: 0.25rem 0;
	}

	.var-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		font-family: var(--font-body);
		font-size: 0.92rem;
	}

	.var-name {
		font-family: var(--font-mono);
		color: var(--color-primary);
		font-weight: 600;
	}

	.var-eq {
		color: var(--color-ink-muted);
		margin: 0 0.4rem;
	}

	.var-label {
		font-style: italic;
		color: var(--color-ink);
	}

	.constraint-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
	}

	.constraint-list li {
		display: flex;
		align-items: baseline;
		gap: 0.55rem;
		padding: 0.35rem 0.6rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-left: 3px solid var(--color-primary);
		border-radius: 0 6px 6px 0;
		flex-wrap: wrap;
	}

	.r-tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--color-primary);
		letter-spacing: 0.1em;
	}

	.r-eq {
		font-size: 0.95rem;
	}

	.r-label {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.82rem;
		margin-left: auto;
	}

	.actions {
		display: grid;
		grid-template-columns: 1fr 2fr;
		gap: 0.6rem;
	}

	.btn-secondary {
		padding: 0.75rem 1rem;
		background: transparent;
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		color: var(--color-ink);
		font-family: var(--font-body);
		font-size: 0.88rem;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.btn-secondary:hover {
		border-color: var(--color-ink);
		background: var(--color-surface-warm);
	}

	.btn-primary {
		padding: 0.75rem 1rem;
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: 10px;
		font-family: var(--font-body);
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.btn-primary:hover {
		background: var(--color-primary-dark, #2d3a9a);
		transform: translateY(-1px);
		box-shadow: 0 6px 16px -8px color-mix(in srgb, var(--color-primary) 50%, transparent);
	}
</style>
