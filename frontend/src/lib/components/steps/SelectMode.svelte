<script lang="ts">
	import { addMessage, advanceState, goToState, sendAssistantMessage, addTip } from '$lib/stores/chat';

	$effect(() => {
		addTip(
			'tip',
			'Chat con Slacko es la entrada más amplia — usa IA para conversar libremente. Si querés un recorrido guiado paso a paso o repasar conceptos puntuales, elegí los modos determinísticos.',
			'¿Cuál elegir?'
		);
	});

	function selectLLMChat() {
		goToState('LLM_CHAT');
	}

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
	<!-- 1. LLM Chat — the principal entrypoint, distinguished by a gradient
	     indigo→gold ring that telegraphs "trained intelligence + curated wiki" -->
	<button onclick={selectLLMChat} class="llm-card group" type="button">
		<div class="llm-card-inner">
			<div class="llm-icon">
				<span class="llm-glyph">∞</span>
			</div>
			<div class="llm-text">
				<div class="llm-title">
					Chat con Slacko
					<span class="llm-pill">con IA</span>
				</div>
				<div class="llm-sub">
					Conversación libre — preguntale en lenguaje natural lo que necesites
				</div>
			</div>
			<span class="llm-arrow" aria-hidden="true">→</span>
		</div>
	</button>

	<!-- 2. Paso a paso (deterministic guided flow) -->
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

	<!-- 3. Consulta teórica -->
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

	<!-- 4. Tutorial -->
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
</div>

<style>
	/* LLM card — uses a 1px gradient ring (indigo→gold) instead of a flat
	   border. The ring is implemented with a padding+linear-gradient wrapper
	   and an inset white card so the gradient only touches the border. */
	.llm-card {
		position: relative;
		display: block;
		width: 100%;
		padding: 1.5px;
		border-radius: 0.85rem;
		background: linear-gradient(
			135deg,
			var(--color-primary),
			var(--color-accent)
		);
		border: none;
		cursor: pointer;
		transition: transform 0.18s ease, box-shadow 0.18s ease;
		text-align: left;
		font-family: var(--font-body);
	}

	.llm-card:hover {
		transform: translateY(-1px);
		box-shadow:
			0 12px 28px -16px color-mix(in srgb, var(--color-primary) 50%, transparent),
			0 6px 16px -10px color-mix(in srgb, var(--color-accent) 35%, transparent);
	}

	.llm-card-inner {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		background: var(--color-surface-card);
		border-radius: calc(0.85rem - 1.5px);
		padding: 1.05rem 1.15rem 1.05rem 1rem;
		position: relative;
		overflow: hidden;
	}

	.llm-card-inner::before {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(
			135deg,
			color-mix(in srgb, var(--color-primary) 6%, transparent),
			transparent 60%
		);
		opacity: 0.7;
		pointer-events: none;
		transition: opacity 0.22s ease;
	}

	.llm-card:hover .llm-card-inner::before {
		opacity: 1;
	}

	.llm-icon {
		position: relative;
		width: 42px;
		height: 42px;
		border-radius: 0.6rem;
		background: linear-gradient(
			135deg,
			color-mix(in srgb, var(--color-primary) 14%, transparent),
			color-mix(in srgb, var(--color-accent) 14%, transparent)
		);
		display: inline-flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
		transition: background 0.22s ease;
	}

	.llm-card:hover .llm-icon {
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
	}

	.llm-glyph {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 1.55rem;
		line-height: 1;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		color: transparent;
		transition: -webkit-text-fill-color 0.22s ease, color 0.22s ease;
	}

	.llm-card:hover .llm-glyph {
		-webkit-text-fill-color: white;
		color: white;
		background: none;
	}

	.llm-text {
		flex: 1;
		min-width: 0;
		position: relative;
	}

	.llm-title {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font-weight: 600;
		color: var(--color-ink);
		font-size: 0.98rem;
		line-height: 1.2;
	}

	.llm-pill {
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		padding: 0.18rem 0.5rem;
		border-radius: 999px;
		color: white;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		font-weight: 500;
	}

	.llm-sub {
		margin-top: 0.2rem;
		font-size: 0.83rem;
		color: var(--color-ink-muted);
		line-height: 1.4;
	}

	.llm-arrow {
		font-family: var(--font-display);
		font-size: 1.2rem;
		color: var(--color-ink-muted);
		transition: transform 0.18s ease, color 0.18s ease;
		flex-shrink: 0;
		position: relative;
	}

	.llm-card:hover .llm-arrow {
		color: var(--color-primary);
		transform: translateX(3px);
	}
</style>
