<script lang="ts">
	import { model, currentState } from '$lib/stores/chat';

	let { open = true }: { open?: boolean } = $props();
</script>

{#if open}
	<aside
		class="w-72 bg-sidebar text-white/90 flex flex-col overflow-y-auto border-r border-white/5 shrink-0"
	>
		<div class="p-5 border-b border-white/10">
			<h2 class="font-display text-xl text-accent">Modelo LP</h2>
			<p class="text-xs text-white/40 mt-1">Se actualiza a medida que avanzás</p>
		</div>

		<div class="p-5 space-y-5 text-sm flex-1">
			<!-- Enunciado -->
			{#if $model.enunciado}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-white/40 mb-2">Enunciado</h3>
					<p class="text-white/70 text-xs leading-relaxed line-clamp-4">{$model.enunciado}</p>
				</section>
			{/if}

			<!-- Objetivo -->
			{#if $model.variables[0].label}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-white/40 mb-2">
						Función objetivo
					</h3>
					<div class="font-mono text-accent-light text-sm">
						{$model.sense === 'maximize' ? 'Max' : 'Min'} Z =
						{$model.variables.map((v) => `${v.coefficient}${v.name}`).join(' + ')}
					</div>
				</section>
			{/if}

			<!-- Variables -->
			{#if $model.variables[0].label}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-white/40 mb-2">Variables</h3>
					<div class="space-y-1">
						{#each $model.variables as v}
							<div class="flex items-center gap-2">
								<span class="font-mono text-primary-light">{v.name}</span>
								<span class="text-white/30">=</span>
								<span class="text-white/70">{v.label}</span>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- Restricciones -->
			{#if $model.constraints.length > 0}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-white/40 mb-2">
						Restricciones
					</h3>
					<div class="space-y-1.5">
						{#each $model.constraints as c, i}
							<div class="font-mono text-xs text-white/70">
								<span class="text-white/40 mr-1">{i + 1}.</span>
								{c.coefficients
									.map(
										(coef, j) =>
											`${j > 0 && coef >= 0 ? '+ ' : ''}${coef}${$model.variables[j]?.name || `x${j + 1}`}`
									)
									.join(' ')}
								{c.sign}
								{c.rhs}
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- No negatividad -->
			{#if $model.variables[0].label}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-white/40 mb-2">
						No negatividad
					</h3>
					<div class="font-mono text-xs text-white/70">
						{$model.variables.map((v) => v.name).join(', ')} ≥ 0
					</div>
				</section>
			{/if}
		</div>

		<div class="p-4 border-t border-white/10 text-[0.7rem] text-white/30">
			Paso actual: <span class="text-accent">{$currentState.replace(/_/g, ' ')}</span>
		</div>
	</aside>
{/if}
