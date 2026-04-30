<script lang="ts">
	import { model, solverResult, resetChat } from '$lib/stores/chat';
	import { get } from 'svelte/store';

	const m = get(model);
	const r = get(solverResult);

	function buildInterpretation(): string {
		if (!r?.optimal_point || r.optimal_value === null) {
			return 'No se encontró una solución factible para este problema. Revisá las restricciones.';
		}

		const sense = m.sense === 'maximize' ? 'maximizar' : 'minimizar';
		const senseResult = m.sense === 'maximize' ? 'máximo' : 'mínimo';
		const v1 = m.variables[0];
		const v2 = m.variables[1];
		const x1 = Number.isInteger(r.optimal_point[0])
			? r.optimal_point[0]
			: r.optimal_point[0].toFixed(2);
		const x2 = Number.isInteger(r.optimal_point[1])
			? r.optimal_point[1]
			: r.optimal_point[1].toFixed(2);
		const z = Number.isInteger(r.optimal_value)
			? r.optimal_value
			: r.optimal_value.toFixed(2);

		return `Para ${sense} la función objetivo, se deben producir/asignar **${x1} unidades de ${v1.label}** (${v1.name}) y **${x2} unidades de ${v2.label}** (${v2.name}), obteniendo un valor ${senseResult} de **Z = ${z}**.`;
	}

	const interpretation = buildInterpretation();
</script>

<div class="step-enter">
	<div class="p-5 rounded-xl bg-white border border-bot-border space-y-4">
		<div class="flex items-center gap-2 mb-2">
			<div class="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center text-accent font-bold">
				★
			</div>
			<h3 class="font-semibold text-ink">Interpretación del resultado</h3>
		</div>

		<p class="text-sm leading-relaxed text-ink">
			{@html interpretation
				.replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary">$1</strong>')
				.replace(/\n/g, '<br/>')}
		</p>

		{#if r?.optimal_point}
			<div class="grid grid-cols-3 gap-3 mt-3">
				{#each m.variables as v, i}
					<div class="p-3 rounded-lg bg-surface-warm text-center">
						<div class="text-xs text-ink-muted">{v.label}</div>
						<div class="font-mono text-lg font-bold text-primary mt-0.5">
							{r.optimal_point[i] % 1 === 0
								? r.optimal_point[i]
								: r.optimal_point[i].toFixed(2)}
						</div>
						<div class="text-xs text-ink-muted font-mono">{v.name}</div>
					</div>
				{/each}
				<div class="p-3 rounded-lg bg-accent/10 text-center">
					<div class="text-xs text-ink-muted">Valor óptimo</div>
					<div class="font-mono text-lg font-bold text-accent mt-0.5">
						{r.optimal_value! % 1 === 0 ? r.optimal_value : r.optimal_value!.toFixed(2)}
					</div>
					<div class="text-xs text-ink-muted font-mono">Z</div>
				</div>
			</div>
		{/if}
	</div>

	<button
		onclick={resetChat}
		class="w-full mt-3 py-2.5 border border-bot-border text-ink rounded-lg text-sm font-medium
			hover:bg-surface-warm transition-colors cursor-pointer"
	>
		Resolver otro problema
	</button>
</div>
