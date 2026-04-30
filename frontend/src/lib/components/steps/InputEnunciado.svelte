<script lang="ts">
	import { model, addMessage, advanceState } from '$lib/stores/chat';

	let text = $state('');

	function submit() {
		const trimmed = text.trim();
		if (!trimmed) return;

		model.update((m) => ({ ...m, enunciado: trimmed }));
		addMessage('user', trimmed);
		addMessage(
			'assistant',
			'Entendido, tengo el enunciado. Ahora decime: **¿el problema busca Maximizar o Minimizar?**'
		);
		advanceState();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && e.ctrlKey) {
			submit();
		}
	}
</script>

<div class="step-enter">
	<textarea
		bind:value={text}
		onkeydown={handleKeydown}
		placeholder="Pegá o escribí el enunciado del problema acá..."
		rows={5}
		class="w-full px-4 py-3 rounded-xl border border-bot-border bg-white text-ink text-sm
			resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
			placeholder:text-ink-muted/50"
	></textarea>
	<div class="flex items-center justify-between mt-3">
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
</div>
