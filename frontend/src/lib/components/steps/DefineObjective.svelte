<script lang="ts">
	import { model, addMessage, advanceState, sendAssistantMessage } from '$lib/stores/chat';

	async function select(sense: 'maximize' | 'minimize') {
		model.update((m) => ({ ...m, sense }));
		addMessage('user', sense === 'maximize' ? 'Maximizar' : 'Minimizar');
		advanceState();
		await sendAssistantMessage(
			`Bien, vamos a **${sense === 'maximize' ? 'maximizar' : 'minimizar'}**. Ahora definí las **variables de decisión** y los **coeficientes** de la función objetivo.`,
			{ delay: 650, expression: 'explain' }
		);
	}
</script>

<div class="step-enter grid grid-cols-2 gap-3">
	<button
		onclick={() => select('maximize')}
		class="p-5 rounded-xl border-2 border-success/20 bg-white hover:border-success hover:shadow-md
			transition-all text-center group cursor-pointer"
	>
		<div class="text-3xl mb-2">↑</div>
		<div class="font-semibold text-ink group-hover:text-success transition-colors">Maximizar</div>
		<div class="text-xs text-ink-muted mt-1">Buscar el mayor valor de Z</div>
	</button>

	<button
		onclick={() => select('minimize')}
		class="p-5 rounded-xl border-2 border-warning/20 bg-white hover:border-warning hover:shadow-md
			transition-all text-center group cursor-pointer"
	>
		<div class="text-3xl mb-2">↓</div>
		<div class="font-semibold text-ink group-hover:text-warning transition-colors">Minimizar</div>
		<div class="text-xs text-ink-muted mt-1">Buscar el menor valor de Z</div>
	</button>
</div>
