<script lang="ts">
	import { model } from '$lib/stores/chat';

	let { open = true }: { open?: boolean } = $props();
</script>

<aside
	class="model-sidebar text-ink shrink-0"
	class:closed={!open}
>
	<div class="sidebar-content">
		<div class="p-5 border-b border-bot-border">
			<h2 class="font-display text-xl text-accent">Modelo LP</h2>
			<p class="text-xs text-ink-muted mt-1">Se actualiza a medida que avanzás</p>
		</div>

		<div class="p-5 space-y-5 text-sm flex-1">
			<!-- Enunciado -->
			{#if $model.enunciado}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-ink-muted mb-2 font-mono">Enunciado</h3>
					<p class="text-ink-light text-xs leading-relaxed line-clamp-4">{$model.enunciado}</p>
				</section>
			{/if}

			<!-- Objetivo -->
			{#if $model.variables[0].label}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-ink-muted mb-2 font-mono">
						Función objetivo
					</h3>
					<div class="font-mono text-accent text-sm font-semibold">
						{$model.sense === 'maximize' ? 'Max' : 'Min'} Z =
						{$model.variables.map((v) => `${v.coefficient}${v.name}`).join(' + ')}
					</div>
				</section>
			{/if}

			<!-- Variables -->
			{#if $model.variables[0].label}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-ink-muted mb-2 font-mono">Variables</h3>
					<div class="space-y-1">
						{#each $model.variables as v}
							<div class="flex items-center gap-2">
								<span class="font-mono text-primary font-semibold">{v.name}</span>
								<span class="text-ink-muted/50">=</span>
								<span class="text-ink-light">{v.label}</span>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- Restricciones -->
			{#if $model.constraints.length > 0}
				<section>
					<h3 class="text-[0.7rem] uppercase tracking-wider text-ink-muted mb-2 font-mono">
						Restricciones
					</h3>
					<div class="space-y-1.5">
						{#each $model.constraints as c, i}
							<div class="font-mono text-xs text-ink-light">
								<span class="text-ink-muted mr-1">{i + 1}.</span>
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
					<h3 class="text-[0.7rem] uppercase tracking-wider text-ink-muted mb-2 font-mono">
						No negatividad
					</h3>
					<div class="font-mono text-xs text-ink-light">
						{$model.variables.map((v) => v.name).join(', ')} ≥ 0
					</div>
				</section>
			{/if}
		</div>
	</div>
</aside>

<style>
	.model-sidebar {
		width: 18rem; /* 288px (w-72) */
		background-color: var(--color-surface-card);
		display: flex;
		flex-direction: column;
		overflow: hidden;
		border-right: 1px solid var(--color-bot-border);
		transition: width 0.25s ease-in-out, border-color 0.25s ease-in-out, background-color 0.25s ease-in-out, color 0.25s ease-in-out;
	}

	.model-sidebar.closed {
		width: 0;
		border-right-color: transparent;
	}

	.sidebar-content {
		width: 18rem;
		height: 100%;
		display: flex;
		flex-direction: column;
		overflow-y: auto;
		flex-shrink: 0;
	}
</style>
