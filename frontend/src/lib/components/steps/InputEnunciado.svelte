<script lang="ts">
	import { model, addMessage, advanceState, sendAssistantMessage } from '$lib/stores/chat';
	import SlackoTip from '$lib/components/SlackoTip.svelte';

	let text = $state('');

	async function submit() {
		const trimmed = text.trim();
		if (!trimmed) return;

		model.update((m) => ({ ...m, enunciado: trimmed }));
		addMessage('user', trimmed);
		advanceState();
		await sendAssistantMessage(
			'Entendido, tengo el enunciado. Ahora decime: **¿el problema busca Maximizar o Minimizar?**',
			{ delay: 800, expression: 'thinking' }
		);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && e.ctrlKey) {
			submit();
		}
	}
</script>

<div class="step-enter space-y-3">
	<textarea
		bind:value={text}
		onkeydown={handleKeydown}
		placeholder="Pegá o escribí el enunciado del problema acá..."
		rows={5}
		class="w-full px-4 py-3 rounded-xl border border-bot-border bg-white text-ink text-sm
			resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
			placeholder:text-ink-muted/50"
	></textarea>
	<div class="flex items-center justify-between">
		<span class="text-xs text-ink-muted">Ctrl+Enter para enviar</span>
		<button
			onclick={submit}
			disabled={!text.trim()}
			class="px-5 py-2 bg-primary text-white rounded-lg text-sm font-medium
				hover:bg-primary-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
		>
			Enviar enunciado
		</button>
	</div>

	<SlackoTip kind="tip" title="Antes de pegarlo, fijate">
		<ul>
			<li>
				¿Están claras las <strong>cantidades a decidir</strong>?
				(ej.: "cuántos balones y cuántos juegos de ajedrez fabricar")
			</li>
			<li>
				¿Hay un objetivo expresado como <em>maximizar</em> o <em>minimizar</em>?
				(utilidad, costo, tiempo, etc.)
			</li>
			<li>
				¿Aparecen <strong>recursos limitados</strong> u <strong>obligaciones mínimas</strong>?
				(horas-máquina, materia prima, mínimos de producción)
			</li>
		</ul>
	</SlackoTip>

	<SlackoTip kind="question" title="Si el enunciado tiene ambigüedades">
		<p>
			Datos como horas o demanda pueden venir <em>por día</em>, <em>por semana</em>
			o <em>por mes</em>. Si no aparece la unidad temporal, asumí la misma para todo
			el problema y dejalo en claro acá.
		</p>
	</SlackoTip>
</div>
