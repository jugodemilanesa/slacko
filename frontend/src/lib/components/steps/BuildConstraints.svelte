<script lang="ts">
	import { model, addMessage, advanceState, type Constraint } from '$lib/stores/chat';
	import { get } from 'svelte/store';

	let label = $state('');
	let coeff1 = $state<number | string>('');
	let coeff2 = $state<number | string>('');
	let sign = $state<'<=' | '>=' | '='>('<=');
	let rhs = $state<number | string>('');

	let localConstraints: Constraint[] = $state([]);

	function addConstraint() {
		if (!label.trim() || coeff1 === '' || coeff2 === '' || rhs === '') return;

		const c: Constraint = {
			label: label.trim(),
			coefficients: [Number(coeff1), Number(coeff2)],
			sign,
			rhs: Number(rhs)
		};

		localConstraints = [...localConstraints, c];
		model.update((m) => ({ ...m, constraints: [...localConstraints] }));

		// Reset form
		label = '';
		coeff1 = '';
		coeff2 = '';
		sign = '<=';
		rhs = '';
	}

	function removeConstraint(index: number) {
		localConstraints = localConstraints.filter((_, i) => i !== index);
		model.update((m) => ({ ...m, constraints: [...localConstraints] }));
	}

	function finish() {
		if (localConstraints.length === 0) return;

		const m = get(model);
		const lines = localConstraints
			.map(
				(c, i) =>
					`${i + 1}. ${c.label}: ${c.coefficients[0]}${m.variables[0].name} + ${c.coefficients[1]}${m.variables[1].name} ${c.sign} ${c.rhs}`
			)
			.join('\n');

		addMessage('user', lines);
		addMessage(
			'assistant',
			'Revisá el modelo completo antes de resolver. Si está todo bien, confirmá para continuar.'
		);
		advanceState();
	}

	let canAdd = $derived(
		label.trim() !== '' && coeff1 !== '' && coeff2 !== '' && rhs !== ''
	);
</script>

<div class="step-enter space-y-4">
	<!-- Restricciones ya ingresadas -->
	{#if localConstraints.length > 0}
		<div class="space-y-2">
			{#each localConstraints as c, i}
				{@const m = get(model)}
				<div
					class="flex items-center justify-between px-3 py-2 rounded-lg bg-surface-warm border border-bot-border text-sm"
				>
					<div>
						<span class="text-ink-muted">{c.label}:</span>
						<span class="font-mono ml-2">
							{c.coefficients[0]}{m.variables[0]?.name || 'x1'} + {c.coefficients[1]}{m.variables[1]?.name || 'x2'}
							{c.sign}
							{c.rhs}
						</span>
					</div>
					<button
						onclick={() => removeConstraint(i)}
						class="text-error/60 hover:text-error text-xs cursor-pointer"
					>
						quitar
					</button>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Formulario -->
	<div class="p-4 rounded-xl bg-white border border-bot-border space-y-3">
		<div>
			<label class="text-xs text-ink-muted block mb-1">Nombre de la restricción</label>
			<input
				type="text"
				bind:value={label}
				placeholder="ej: Máquina A, Mano de obra..."
				class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm
					focus:outline-none focus:ring-2 focus:ring-primary/30"
			/>
		</div>

		<div class="grid grid-cols-5 gap-2 items-end">
			<div>
				<label class="text-xs text-ink-muted block mb-1">Coef x1</label>
				<input
					type="number"
					bind:value={coeff1}
					placeholder="0"
					step="any"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm font-mono
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Coef x2</label>
				<input
					type="number"
					bind:value={coeff2}
					placeholder="0"
					step="any"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm font-mono
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Signo</label>
				<select
					bind:value={sign}
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm font-mono
						focus:outline-none focus:ring-2 focus:ring-primary/30 bg-white"
				>
					<option value="<=">≤</option>
					<option value=">=">≥</option>
					<option value="=">=</option>
				</select>
			</div>
			<div>
				<label class="text-xs text-ink-muted block mb-1">Valor (RHS)</label>
				<input
					type="number"
					bind:value={rhs}
					placeholder="0"
					step="any"
					class="w-full px-3 py-2 rounded-lg border border-bot-border text-sm font-mono
						focus:outline-none focus:ring-2 focus:ring-primary/30"
				/>
			</div>
			<button
				onclick={addConstraint}
				disabled={!canAdd}
				class="py-2 bg-ink/10 text-ink rounded-lg text-sm font-medium
					hover:bg-ink/20 transition-colors disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
			>
				+ Agregar
			</button>
		</div>
	</div>

	{#if localConstraints.length > 0}
		<button
			onclick={finish}
			class="w-full py-2.5 bg-primary text-white rounded-lg text-sm font-medium
				hover:bg-primary-dark transition-colors cursor-pointer"
		>
			Listo, revisar modelo ({localConstraints.length} restriccion{localConstraints.length > 1
				? 'es'
				: ''})
		</button>
	{/if}
</div>
