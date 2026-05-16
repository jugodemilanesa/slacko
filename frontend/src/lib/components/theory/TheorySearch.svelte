<script lang="ts">
	let {
		value = $bindable(''),
		onSubmit,
		loading = false
	}: {
		value: string;
		onSubmit: (q: string) => void;
		loading?: boolean;
	} = $props();

	let inputEl = $state<HTMLTextAreaElement | undefined>();

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			submit();
		}
	}

	function submit() {
		const q = value.trim();
		if (!q || loading) return;
		onSubmit(q);
	}

	const placeholders = [
		'¿Qué es la región factible?',
		'¿Cuáles son los supuestos del modelo?',
		'¿Cómo paso de canónica a estándar?',
		'¿Qué es una variable de holgura?',
		'¿Qué pasa si una solución es no acotada?',
		'¿Qué dice el Teorema Fundamental?'
	];
	let placeholderIdx = $state(0);

	$effect(() => {
		const t = setInterval(() => {
			placeholderIdx = (placeholderIdx + 1) % placeholders.length;
		}, 3500);
		return () => clearInterval(t);
	});

	export function focusInput() {
		inputEl?.focus();
	}
</script>

<div class="search-wrap step-enter">
	<div class="rule-top">
		<span class="rule-line" aria-hidden="true"></span>
		<span class="rule-label font-mono">consulta · teoría</span>
		<span class="rule-line" aria-hidden="true"></span>
	</div>

	<h1 class="hero-title">
		El concepto te lo busca <span class="ampersand">&</span> te lo explica.
	</h1>

	<p class="hero-sub">
		Preguntá lo que quieras de Programación Lineal — definiciones, formas, métodos, casos
		especiales. Te respondo con el material de cátedra.
	</p>

	<form
		class="search"
		onsubmit={(e) => {
			e.preventDefault();
			submit();
		}}
	>
		<label class="search-label" for="theory-q">Tu pregunta</label>
		<div class="input-row">
			<textarea
				id="theory-q"
				bind:this={inputEl}
				bind:value
				rows="1"
				class="input"
				placeholder={placeholders[placeholderIdx]}
				onkeydown={handleKey}
				disabled={loading}
				autocomplete="off"
				spellcheck="false"
			></textarea>
			<button type="submit" class="submit" disabled={loading || !value.trim()}>
				{#if loading}
					<span class="spinner" aria-hidden="true"></span>
					<span>Buscando</span>
				{:else}
					<span>Preguntar</span>
					<span class="arrow" aria-hidden="true">→</span>
				{/if}
			</button>
		</div>
		<div class="hint">
			<span class="kbd">Enter</span> para preguntar &nbsp;·&nbsp; <span class="kbd">Shift</span> +
			<span class="kbd">Enter</span> para nueva línea
		</div>
	</form>
</div>

<style>
	.search-wrap {
		max-width: 720px;
		margin: 0 auto;
		text-align: center;
	}

	.rule-top {
		display: flex;
		align-items: center;
		gap: 0.85rem;
		justify-content: center;
		margin-bottom: 0.85rem;
	}

	.rule-line {
		flex: 0 0 60px;
		height: 1px;
		background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
		opacity: 0.6;
	}

	.rule-label {
		font-size: 0.62rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--color-accent);
	}

	.hero-title {
		font-family: var(--font-display);
		font-size: clamp(2.4rem, 5vw, 3.5rem);
		line-height: 1.05;
		letter-spacing: -0.015em;
		color: var(--color-ink);
		margin: 0;
	}

	.ampersand {
		font-style: italic;
		color: var(--color-accent);
	}

	.hero-sub {
		font-family: var(--font-body);
		font-size: 1rem;
		color: var(--color-ink-light);
		line-height: 1.6;
		max-width: 540px;
		margin: 1rem auto 2rem auto;
	}

	.search {
		text-align: left;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		padding: 1rem 1.25rem 1.1rem 1.25rem;
		box-shadow: 0 12px 24px -16px rgba(26, 26, 46, 0.18);
		transition: border-color 0.2s ease, box-shadow 0.2s ease;
	}

	.search:focus-within {
		border-color: var(--color-primary);
		box-shadow: 0 16px 32px -16px rgba(59, 76, 192, 0.25);
	}

	.search-label {
		display: block;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-bottom: 0.5rem;
	}

	.input-row {
		display: flex;
		gap: 0.75rem;
		align-items: stretch;
	}

	.input {
		flex: 1;
		font-family: var(--font-display);
		font-size: 1.35rem;
		line-height: 1.4;
		background: transparent;
		border: none;
		resize: none;
		color: var(--color-ink);
		padding: 0.4rem 0;
		min-height: 2.6rem;
		max-height: 8rem;
		outline: none;
	}

	.input::placeholder {
		color: var(--color-ink-muted);
		font-style: italic;
		opacity: 0.6;
	}

	.submit {
		font-family: var(--font-body);
		font-size: 0.85rem;
		font-weight: 600;
		color: white;
		background: var(--color-primary);
		border: none;
		border-radius: 8px;
		padding: 0.7rem 1.1rem;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		transition: all 0.15s ease;
		align-self: center;
	}

	.submit:hover:not(:disabled) {
		background: var(--color-primary-dark);
		transform: translateY(-1px);
		box-shadow: 0 6px 14px -6px rgba(59, 76, 192, 0.5);
	}

	.submit:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.submit .arrow {
		font-family: var(--font-display);
		font-size: 1.1rem;
		line-height: 1;
		transition: transform 0.15s ease;
	}

	.submit:hover:not(:disabled) .arrow {
		transform: translateX(2px);
	}

	.spinner {
		width: 12px;
		height: 12px;
		border: 1.5px solid rgba(255, 255, 255, 0.4);
		border-top-color: white;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.hint {
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		margin-top: 0.6rem;
	}

	.kbd {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		background: var(--color-surface-warm);
		border: 1px solid var(--color-bot-border);
		padding: 0.05rem 0.35rem;
		border-radius: 3px;
		color: var(--color-ink-light);
	}
</style>
