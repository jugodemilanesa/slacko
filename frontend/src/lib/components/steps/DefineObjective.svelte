<script lang="ts">
	import { model, addMessage, advanceState, sendAssistantMessage } from '$lib/stores/chat';
	import SlackoTip from '$lib/components/SlackoTip.svelte';

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

<div class="step-enter space-y-3">
	<div class="grid grid-cols-2 gap-3">
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

	<SlackoTip kind="tip" title="¿Cómo decidir?">
		<ul>
			<li>
				Pensá qué <strong>palabra clave</strong> aparece en el enunciado:
				<em>maximizar</em>, <em>obtener la mayor ganancia</em>, <em>aprovechar al máximo</em>
				son señales de <strong>Max</strong>.
			</li>
			<li>
				<em>Minimizar costo</em>, <em>reducir el tiempo</em>, <em>al menor desperdicio</em>
				son señales de <strong>Min</strong>.
			</li>
			<li>
				En la duda: <strong>ganancia / utilidad / producción → Max</strong>;
				<strong>costo / tiempo / pérdida → Min</strong>.
			</li>
		</ul>
	</SlackoTip>

	<SlackoTip kind="concept" title="¿Por qué importa esto antes?">
		<p>
			El sentido (Max/Min) cambia cómo se mueve la <em>recta de isoutilidad</em>
			sobre la región factible. En Max la alejás del origen; en Min, la acercás. Es
			la primera decisión del método gráfico.
		</p>
	</SlackoTip>
</div>
