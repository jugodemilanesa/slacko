<script lang="ts">
	import { model, addMessage, advanceState, goToState } from '$lib/stores/chat';

	function confirm() {
		addMessage('user', 'Confirmo, resolver');
		addMessage(
			'assistant',
			'Convirtiendo a **forma estándar**...'
		);
		advanceState();
	}

	function edit() {
		goToState('BUILD_CONSTRAINTS');
		addMessage('user', 'Quiero editar las restricciones');
		addMessage('assistant', 'Dale, modificá las restricciones.');
	}
</script>

<div class="step-enter">
	<div class="p-5 rounded-xl bg-white border border-bot-border space-y-4">
		<h3 class="font-semibold text-ink flex items-center gap-2">
			<span class="w-6 h-6 rounded bg-primary/10 text-primary text-xs flex items-center justify-center">✓</span>
			Modelo completo
		</h3>

		<!-- Función Objetivo -->
		<div>
			<div class="text-xs text-ink-muted uppercase tracking-wider mb-1">Función objetivo</div>
			<div class="font-mono text-sm bg-surface-warm px-3 py-2 rounded-lg">
				{$model.sense === 'maximize' ? 'Max' : 'Min'} Z =
				{$model.variables.map((v) => `${v.coefficient}${v.name}`).join(' + ')}
			</div>
		</div>

		<!-- Variables -->
		<div>
			<div class="text-xs text-ink-muted uppercase tracking-wider mb-1">Variables de decisión</div>
			<div class="text-sm space-y-0.5">
				{#each $model.variables as v}
					<div>
						<span class="font-mono text-primary">{v.name}</span> = {v.label}
					</div>
				{/each}
			</div>
		</div>

		<!-- Restricciones -->
		<div>
			<div class="text-xs text-ink-muted uppercase tracking-wider mb-1">Restricciones</div>
			<div class="space-y-1">
				{#each $model.constraints as c, i}
					<div class="font-mono text-sm">
						<span class="text-ink-muted mr-1">({i + 1})</span>
						{c.coefficients[0]}{$model.variables[0].name} + {c.coefficients[1]}{$model.variables[1].name}
						{c.sign === '<=' ? '≤' : c.sign === '>=' ? '≥' : '='}
						{c.rhs}
						{#if c.label}
							<span class="text-ink-muted ml-2 text-xs">({c.label})</span>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<!-- No negatividad -->
		<div>
			<div class="text-xs text-ink-muted uppercase tracking-wider mb-1">No negatividad</div>
			<div class="font-mono text-sm">{$model.variables.map((v) => v.name).join(', ')} ≥ 0</div>
		</div>
	</div>

	<div class="grid grid-cols-2 gap-3 mt-3">
		<button
			onclick={edit}
			class="py-2.5 border border-bot-border text-ink rounded-lg text-sm font-medium
				hover:bg-surface-warm transition-colors cursor-pointer"
		>
			Editar
		</button>
		<button
			onclick={confirm}
			class="py-2.5 bg-primary text-white rounded-lg text-sm font-medium
				hover:bg-primary-dark transition-colors cursor-pointer"
		>
			Confirmar y resolver
		</button>
	</div>
</div>
