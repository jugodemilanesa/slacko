<script lang="ts">
	import { onMount } from 'svelte';
	import { model, addMessage, advanceState, standardFormResult } from '$lib/stores/chat';
	import { getStandardForm } from '$lib/api/solver';
	import { get } from 'svelte/store';

	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			const m = get(model);
			const result = await getStandardForm({
				variables: m.variables.map((v) => v.name),
				objective_coefficients: m.variables.map((v) => v.coefficient),
				sense: m.sense,
				constraints: m.constraints.map((c) => ({
					coefficients: c.coefficients,
					sign: c.sign,
					rhs: c.rhs,
					label: c.label
				}))
			});
			standardFormResult.set(result);
			loading = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error al convertir';
			loading = false;
		}
	});

	function next() {
		addMessage('user', 'Entendido, resolver');
		addMessage('assistant', 'Calculando la **región factible**, los **vértices** y el **punto óptimo**...');
		advanceState();
	}
</script>

<div class="step-enter">
	{#if loading}
		<div class="p-6 text-center text-ink-muted">
			<div class="animate-pulse">Convirtiendo a forma estándar...</div>
		</div>
	{:else if error}
		<div class="p-4 bg-error/10 text-error rounded-xl text-sm">{error}</div>
	{:else if $standardFormResult}
		<div class="p-5 rounded-xl bg-white border border-bot-border space-y-4">
			<h3 class="font-semibold text-ink">Forma estándar</h3>

			{#if $standardFormResult.slack_variables.length > 0}
				<div>
					<div class="text-xs text-ink-muted mb-1">Variables de holgura (slack)</div>
					<div class="font-mono text-sm text-success">
						{$standardFormResult.slack_variables.join(', ')}
					</div>
				</div>
			{/if}

			{#if $standardFormResult.surplus_variables.length > 0}
				<div>
					<div class="text-xs text-ink-muted mb-1">Variables de exceso (surplus)</div>
					<div class="font-mono text-sm text-warning">
						{$standardFormResult.surplus_variables.join(', ')}
					</div>
				</div>
			{/if}

			{#if $standardFormResult.artificial_variables.length > 0}
				<div>
					<div class="text-xs text-ink-muted mb-1">Variables artificiales</div>
					<div class="font-mono text-sm text-error">
						{$standardFormResult.artificial_variables.join(', ')}
					</div>
				</div>
			{/if}

			<div>
				<div class="text-xs text-ink-muted mb-2">Ecuaciones</div>
				<div class="space-y-1.5">
					{#each $standardFormResult.constraints as c}
						<div
							class="font-mono text-sm bg-surface-warm px-3 py-2 rounded-lg flex items-center gap-2"
						>
							{#if c.label}
								<span class="text-ink-muted text-xs shrink-0">({c.label})</span>
							{/if}
							<span>{c.equation}</span>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<button
			onclick={next}
			class="w-full mt-3 py-2.5 bg-primary text-white rounded-lg text-sm font-medium
				hover:bg-primary-dark transition-colors cursor-pointer"
		>
			Continuar a resolución gráfica
		</button>
	{/if}
</div>
