<script lang="ts">
	import { addMessage, advanceState, goToState } from '$lib/stores/chat';

	function selectGuided() {
		addMessage('user', 'Quiero resolver paso a paso');
		addMessage(
			'assistant',
			'Perfecto, vamos a ir armando el modelo juntos. Para empezar, **pegá el enunciado del problema** que querés resolver.'
		);
		advanceState();
	}

	function selectTheory() {
		goToState('THEORY_QUERY');
	}
</script>

<div class="step-enter space-y-3">
	<button
		onclick={selectGuided}
		class="w-full p-5 rounded-xl border-2 border-primary/20 bg-white hover:border-primary hover:shadow-md
			transition-all text-left group cursor-pointer"
	>
		<div class="flex items-center gap-3">
			<div
				class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary text-lg group-hover:bg-primary group-hover:text-white transition-colors"
			>
				1→
			</div>
			<div>
				<div class="font-semibold text-ink">Paso a paso</div>
				<div class="text-sm text-ink-muted">Te guío para armar tu modelo desde cero</div>
			</div>
		</div>
	</button>

	<button
		onclick={selectTheory}
		class="w-full p-5 rounded-xl border-2 border-accent/30 bg-white hover:border-accent hover:shadow-md
			transition-all text-left group cursor-pointer"
	>
		<div class="flex items-center gap-3">
			<div
				class="w-10 h-10 rounded-lg bg-accent/15 flex items-center justify-center text-accent text-lg
					group-hover:bg-accent group-hover:text-white transition-colors font-display"
			>
				§
			</div>
			<div>
				<div class="font-semibold text-ink">Consulta teórica</div>
				<div class="text-sm text-ink-muted">Repasá conceptos clave de PL — definiciones, formas, casos</div>
			</div>
		</div>
	</button>

	<button
		disabled
		class="w-full p-5 rounded-xl border-2 border-ink/5 bg-surface-warm text-left opacity-50 cursor-not-allowed"
	>
		<div class="flex items-center gap-3">
			<div
				class="w-10 h-10 rounded-lg bg-ink/5 flex items-center justify-center text-ink-muted text-lg"
			>
				⚡
			</div>
			<div>
				<div class="font-semibold text-ink-light">Revisar mi modelo</div>
				<div class="text-sm text-ink-muted">Próximamente</div>
			</div>
		</div>
	</button>
</div>
