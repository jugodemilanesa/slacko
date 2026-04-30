<script lang="ts">
	import { model, addMessage, advanceState } from '$lib/stores/chat';
	import { get } from 'svelte/store';

	let var1Label = $state('');
	let var1Coeff = $state<number | string>('');
	let var2Label = $state('');
	let var2Coeff = $state<number | string>('');

	function submit() {
		if (!var1Label.trim() || !var2Label.trim() || var1Coeff === '' || var2Coeff === '') return;

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
		const sense = m.sense === 'maximize' ? 'Max' : 'Min';

		addMessage(
			'user',
			`x1 = ${var1Label} (coef: ${c1})\nx2 = ${var2Label} (coef: ${c2})`
		);
		addMessage(
			'assistant',
			`La función objetivo queda: **${sense} Z = ${c1}x1 + ${c2}x2**\n\nAhora vamos con las **restricciones**. Ingresá cada una con su etiqueta, coeficientes, signo y valor límite.`
		);
		advanceState();
	}
</script>

<div class="step-enter space-y-4">
	<div class="grid grid-cols-2 gap-4">
		<!-- Variable 1 -->
		<div class="space-y-2 p-4 rounded-xl bg-surface-warm border border-bot-border">
			<div class="font-mono text-sm font-semibold text-primary">x1</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Nombre / etiqueta</label>
				<input
					type="text"
					bind:value={var1Label}
					placeholder="ej: balones"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm bg-white
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Coeficiente en Z</label>
				<input
					type="number"
					bind:value={var1Coeff}
					placeholder="ej: 2"
					step="any"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm bg-white font-mono
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
		</div>

		<!-- Variable 2 -->
		<div class="space-y-2 p-4 rounded-xl bg-surface-warm border border-bot-border">
			<div class="font-mono text-sm font-semibold text-primary">x2</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Nombre / etiqueta</label>
				<input
					type="text"
					bind:value={var2Label}
					placeholder="ej: ajedrez"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm bg-white
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Coeficiente en Z</label>
				<input
					type="number"
					bind:value={var2Coeff}
					placeholder="ej: 4"
					step="any"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm bg-white font-mono
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
		</div>
	</div>

	<button
		onclick={submit}
		disabled={!var1Label.trim() || !var2Label.trim() || var1Coeff === '' || var2Coeff === ''}
		class="w-full py-2.5 bg-primary text-white rounded-lg text-sm font-medium
			hover:bg-primary-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
	>
		Confirmar variables
	</button>
</div>
