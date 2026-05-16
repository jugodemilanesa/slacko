<script lang="ts">
	import { addMessage, advanceState, goToState, sendAssistantMessage } from '$lib/stores/chat';
	import SlackoTip from '$lib/components/SlackoTip.svelte';

	async function selectGuided() {
		addMessage('user', 'Quiero resolver paso a paso');
		advanceState();
		await sendAssistantMessage(
			'Perfecto, vamos a ir armando el modelo juntos. Para empezar, **pegá el enunciado del problema** que querés resolver.',
			{ delay: 700, expression: 'explain' }
		);
	}

	function selectTheory() {
		goToState('THEORY_QUERY');
	}

	function selectTutorial() {
		goToState('TUTORIAL');
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
		onclick={selectTutorial}
		class="w-full p-5 rounded-xl border-2 border-ink/15 bg-white hover:border-ink hover:shadow-md
			transition-all text-left group cursor-pointer"
	>
		<div class="flex items-center gap-3">
			<div
				class="w-10 h-10 rounded-lg bg-ink/8 flex items-center justify-center text-ink text-lg
					group-hover:bg-ink group-hover:text-white transition-colors font-display"
			>
				✦
			</div>
			<div>
				<div class="font-semibold text-ink">Tutorial</div>
				<div class="text-sm text-ink-muted">
					Recorré un ejemplo ya resuelto conmigo, paso a paso
				</div>
			</div>
		</div>
	</button>

	<SlackoTip kind="tip" title="¿Cuál elegir?">
		<p>
			Si tenés un enunciado entre manos y querés <strong>resolverlo</strong>, elegí
			<em>Paso a paso</em>. Si necesitás <strong>repasar un concepto</strong> antes
			(qué es una variable slack, qué pasa si no hay solución factible, etc.), entrá
			a <em>Consulta teórica</em>.
		</p>
	</SlackoTip>
</div>
