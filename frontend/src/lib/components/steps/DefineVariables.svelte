<script lang="ts">
	import { model, addMessage, advanceState, sendAssistantMessage, addTip } from '$lib/stores/chat';
	import { get } from 'svelte/store';
	import Latex from '$lib/components/Latex.svelte';
	import { objectiveLatex } from '$lib/math/formula';

	let var1Label = $state('');
	let var1Coeff = $state('');
	let var2Label = $state('');
	let var2Coeff = $state('');

	function isValidNumber(val: string) {
		if (val.trim() === '') return false;
		return !isNaN(Number(val));
	}

	function isInvalidInput(val: string) {
		if (val.trim() === '') return false;
		return isNaN(Number(val));
	}

	const preview = $derived.by(() => {
		const m = get(model);
		const c1 = isValidNumber(var1Coeff) ? Number(var1Coeff) : 0;
		const c2 = isValidNumber(var2Coeff) ? Number(var2Coeff) : 0;
		const draftModel = {
			...m,
			variables: [
				{ name: 'x1', label: var1Label, coefficient: c1 },
				{ name: 'x2', label: var2Label, coefficient: c2 }
			]
		};
		return objectiveLatex(draftModel);
	});

	async function submit() {
		if (!var1Label.trim() || !var2Label.trim() || !isValidNumber(var1Coeff) || !isValidNumber(var2Coeff)) return;

		const c1 = Number(var1Coeff);
		const c2 = Number(var2Coeff);

		model.update((m) => ({
			...m,
			variables: [
				{ name: 'x1', label: var1Label.trim(), coefficient: c1 },
				{ name: 'x2', label: var2Label.trim(), coefficient: c2 }
			]
		}));

		const m = get(model);

		addMessage(
			'user',
			`x1 = ${var1Label} (coef: ${c1})\nx2 = ${var2Label} (coef: ${c2})`
		);
		advanceState();
		await sendAssistantMessage(
			`La función objetivo queda: $${objectiveLatex(m)}$\n\nAhora vamos con las **restricciones**. Ingresá cada una con su etiqueta, coeficientes, signo y valor límite.`,
			{ delay: 750, expression: 'happy' }
		);
	}

	$effect(() => {
		addTip('concept', 'Una variable de decisión representa una cantidad desconocida que el problema nos pide determinar — típicamente cuánto fabricar, cuánto usar, o cuánto asignar.', '¿Qué es una variable de decisión?');
		addTip('tip', 'Usá punto como separador decimal (ej: 0.25, no 0,25). Si el coeficiente es entero, no hace falta .0.', 'Sobre los decimales');
	});
</script>

<div class="step-enter space-y-3">
	<div class="grid grid-cols-2 gap-4">
		<!-- Variable 1 -->
		<div class="space-y-2 p-4 rounded-xl bg-surface-warm border border-bot-border">
			<div class="font-mono text-sm font-semibold text-primary">x1</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1" for="var1-label">
					Nombre / etiqueta
				</label>
				<input
					id="var1-label"
					type="text"
					bind:value={var1Label}
					placeholder="ej: balones"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm bg-surface-card text-ink
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1" for="var1-coef">
					Coeficiente en Z
				</label>
				<input
					id="var1-coef"
					type="text"
					bind:value={var1Coeff}
					placeholder="ej: 2"
					inputmode="decimal"
					class="w-full px-3 py-2 rounded-lg border text-sm font-mono focus:outline-none focus:ring-2 transition-colors
						{isInvalidInput(var1Coeff) ? 'border-red-500/60 bg-red-500/10 text-red-500 focus:border-red-500 focus:ring-red-500/20' : 'border-bot-border bg-surface-card text-ink focus:ring-primary/30'}"
				/>
			</div>
		</div>

		<!-- Variable 2 -->
		<div class="space-y-2 p-4 rounded-xl bg-surface-warm border border-bot-border">
			<div class="font-mono text-sm font-semibold text-primary">x2</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1" for="var2-label">
					Nombre / etiqueta
				</label>
				<input
					id="var2-label"
					type="text"
					bind:value={var2Label}
					placeholder="ej: ajedrez"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm bg-surface-card text-ink
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1" for="var2-coef">
					Coeficiente en Z
				</label>
				<input
					id="var2-coef"
					type="text"
					bind:value={var2Coeff}
					placeholder="ej: 4"
					inputmode="decimal"
					class="w-full px-3 py-2 rounded-lg border text-sm font-mono focus:outline-none focus:ring-2 transition-colors
						{isInvalidInput(var2Coeff) ? 'border-red-500/60 bg-red-500/10 text-red-500 focus:border-red-500 focus:ring-red-500/20' : 'border-bot-border bg-surface-card text-ink focus:ring-primary/30'}"
				/>
			</div>
		</div>
	</div>

	<!-- LaTeX preview -->
	<div class="formula-preview">
		<div class="formula-label">
			<span class="dot" aria-hidden="true">◆</span>
			Función objetivo
		</div>
		<Latex expr={preview} display />

		{#if var1Label.trim() || var2Label.trim()}
			<div class="mt-3 pt-3 border-t border-bot-border/50 text-sm">
				{#if var1Label.trim()}
					<div class="flex items-center gap-1.5 mb-1.5">
						<Latex expr="x_1" /> 
						<span class="text-ink-muted">: {var1Label.trim()}</span>
					</div>
				{/if}
				{#if var2Label.trim()}
					<div class="flex items-center gap-1.5">
						<Latex expr="x_2" /> 
						<span class="text-ink-muted">: {var2Label.trim()}</span>
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<button
		onclick={submit}
		disabled={!var1Label.trim() || !var2Label.trim() || !isValidNumber(var1Coeff) || !isValidNumber(var2Coeff)}
		class="w-full py-2.5 bg-primary text-white rounded-lg text-sm font-medium
			hover:bg-primary-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
	>
		Confirmar variables
	</button>


</div>

<style>
	.formula-preview {
		background: var(--color-surface-warm);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		padding: 0.75rem 1rem 0.85rem 1rem;
		position: relative;
		overflow: hidden;
	}

	.formula-preview::before {
		content: '';
		position: absolute;
		inset: 0;
		border-left: 3px solid var(--color-accent);
		pointer-events: none;
	}

	.formula-label {
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: 0.25rem;
		display: flex;
		align-items: center;
		gap: 0.35rem;
	}

	.dot {
		font-size: 0.55rem;
	}
</style>
