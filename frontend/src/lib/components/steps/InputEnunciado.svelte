<script lang="ts">
	import { model, addMessage, advanceState, sendAssistantMessage, addTip } from '$lib/stores/chat';

	$effect(() => {
		addTip('tip', 'Antes de pegar el enunciado, verificá: ¿están claras las cantidades a decidir? ¿hay un objetivo que maximizar o minimizar? ¿aparecen recursos limitados?', 'Antes de pegarlo, fijate');
		addTip('question', 'Datos como horas o demanda pueden venir por día, por semana o por mes. Si no aparece la unidad temporal, asumí la misma para todo el problema.', 'Si el enunciado tiene ambigüedades');
	});

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
		class="w-full px-4 py-3 rounded-xl border border-bot-border bg-surface-card text-ink text-sm
			resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
			placeholder:text-ink-muted/50"
	></textarea>
	<div class="flex items-center justify-between">
		<span class="composer-hint">
			<span><span class="key">Ctrl</span><span class="key-plus">+</span><span class="key">Enter</span> para enviar</span>
		</span>
		<button
			onclick={submit}
			disabled={!text.trim()}
			class="ml-auto px-5 py-2 bg-primary text-white rounded-lg text-sm font-medium
				hover:bg-primary-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
		>
			Enviar enunciado
		</button>
	</div>
</div>

<style>
	.composer-hint {
		display: inline-flex;
		align-items: center;
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.72rem;
		color: var(--color-ink-muted);
	}

	.key {
		font-family: var(--font-mono);
		font-style: normal;
		font-size: 0.6rem;
		padding: 0.08rem 0.38rem;
		border: 1px solid var(--color-bot-border);
		border-radius: 4px;
		background: var(--color-surface-card);
		color: var(--color-ink);
		margin: 0 0.15rem;
	}

	.key-plus {
		font-style: normal;
		font-family: var(--font-mono);
	}

	@media (max-width: 700px) {
		.composer-hint {
			display: none;
		}
	}
</style>
