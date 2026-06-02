<script lang="ts">
	import { onMount, onDestroy, tick } from 'svelte';

	import SlakingAvatar from '$lib/components/SlakingAvatar.svelte';
	import ChatBubbleLLM from '$lib/components/llm/ChatBubbleLLM.svelte';
	import ProviderBadge from '$lib/components/llm/ProviderBadge.svelte';
	import LLMSessionSidebar from '$lib/components/llm/LLMSessionSidebar.svelte';

	import {
		messages,
		status,
		lastError,
		session,
		isThinking,
		start,
		send,
		reset
	} from '$lib/stores/llmChat';

	let composerValue = $state('');
	let stackEl = $state<HTMLDivElement | null>(null);
	let textareaEl = $state<HTMLTextAreaElement | null>(null);
	let sidebarOpen = $state(false);

	const SUGGESTIONS = [
		'¿Qué es la región factible y por qué siempre es convexa?',
		'Quiero resolver: una fábrica produce X que deja $2 e Y que deja $4...',
		'Explicame qué es una variable de holgura con un ejemplo.'
	];

	onMount(() => {
		start();
	});

	onDestroy(() => {
		// We intentionally do NOT call reset() here — leaving the socket open
		// across re-mounts (eg user switches sub-mode and comes back) would be
		// nicer, but Svelte tears the component down. Closing is fine: cached
		// session id stays in localStorage so the next start() rejoins.
		reset();
	});

	const lastAssistantProvider = $derived.by(() => {
		const arr = $messages;
		for (let i = arr.length - 1; i >= 0; i--) {
			if (arr[i].role === 'assistant' && arr[i].provider) return arr[i].provider;
		}
		return undefined;
	});

	const lastAssistantModel = $derived.by(() => {
		const arr = $messages;
		for (let i = arr.length - 1; i >= 0; i--) {
			if (arr[i].role === 'assistant' && arr[i].model) return arr[i].model;
		}
		return undefined;
	});

	const hasMessages = $derived($messages.length > 0);

	const statusBadge = $derived.by(() => {
		switch ($status) {
			case 'connecting':
				return { label: 'Conectando', tone: 'muted' as const };
			case 'reconnecting':
				return { label: 'Reconectando', tone: 'warning' as const };
			case 'error':
				return { label: 'Sin conexión', tone: 'error' as const };
			case 'thinking':
				return { label: 'Pensando', tone: 'accent' as const };
			default:
				return null;
		}
	});

	async function scrollToBottom() {
		await tick();
		if (stackEl) {
			stackEl.scrollTo({ top: stackEl.scrollHeight, behavior: 'smooth' });
		}
	}

	$effect(() => {
		// re-run on any message change
		const _ = $messages.length;
		void _;
		scrollToBottom();
	});

	function autosize() {
		if (!textareaEl) return;
		textareaEl.style.height = 'auto';
		const next = Math.min(textareaEl.scrollHeight, 168); // ~6 lines
		textareaEl.style.height = next + 'px';
	}

	function onInput() {
		autosize();
	}

	function submit() {
		const text = composerValue.trim();
		if (!text || $isThinking || $status === 'connecting' || $status === 'reconnecting') return;
		send(text);
		composerValue = '';
		if (textareaEl) {
			textareaEl.style.height = 'auto';
			textareaEl.focus();
		}
	}

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			submit();
		}
	}

	function pickSuggestion(text: string) {
		composerValue = text;
		if (textareaEl) {
			textareaEl.focus();
			tick().then(autosize);
		}
	}

	function newChat() {
		reset();
		composerValue = '';
		start();
	}

	function retry() {
		reset();
		start();
	}
</script>

<div class="llm-page" class:has-messages={hasMessages}>
	<!-- Background ornament: paper wash + faint vertical rule -->
	<div class="paper-bg" aria-hidden="true"></div>

	<!-- Sticky header (only while chatting) -->
	{#if hasMessages}
		<header class="lh-header">
			<div class="lh-inner">
				<div class="lh-left">
					<button
						type="button"
						class="hist-btn"
						onclick={() => (sidebarOpen = true)}
						aria-label="Abrir historial de chats"
						title="Historial"
					>
						<span aria-hidden="true">☰</span>
					</button>
					<span class="chip">
						<span class="chip-rail" aria-hidden="true"></span>
						<span class="chip-glyph" aria-hidden="true">∞</span>
						Modo conversación
					</span>
					{#if $session?.title}
						<span class="title">{$session.title}</span>
					{/if}
					{#if statusBadge}
						<span class="status-pill" data-tone={statusBadge.tone}>
							<span class="status-dot"></span>
							{statusBadge.label}
						</span>
					{/if}
				</div>

				<div class="lh-right">
					<ProviderBadge provider={lastAssistantProvider} model={lastAssistantModel} />
					<button type="button" class="lh-btn ghost" onclick={newChat} title="Empezar un chat nuevo">
						<span class="btn-glyph">+</span>
						Nuevo chat
					</button>
				</div>
			</div>
		</header>
	{/if}

	<!-- Main scroll area -->
	<div class="lh-scroll" bind:this={stackEl}>
		<div class="lh-column">
			{#if !hasMessages}
				<!-- Idle hero -->
				<section class="hero" aria-label="Bienvenida al chat con Slacko">
					<div class="hero-overline">
						<span class="ov-dot"></span>
						Chat con Slacko
						<span class="ov-dot"></span>
					</div>

					<div class="hero-avatar-wrap">
						<SlakingAvatar expression="happy" size="xl" ring floating />
					</div>

					<h1 class="hero-title">
						<span class="drop">S</span>oy <em>Slacko.</em>
					</h1>

					<svg class="hero-arc" viewBox="0 0 320 60" aria-hidden="true">
						<defs>
							<linearGradient id="arc-grad" x1="0%" y1="0%" x2="100%" y2="0%">
								<stop offset="0%" stop-color="var(--color-primary)" />
								<stop offset="100%" stop-color="var(--color-accent)" />
							</linearGradient>
						</defs>
						<path
							d="M5 40 Q 80 5, 160 30 T 315 40"
							fill="none"
							stroke="url(#arc-grad)"
							stroke-width="1.2"
							stroke-linecap="round"
							opacity="0.55"
						/>
						<circle cx="160" cy="30" r="2.5" fill="var(--color-accent)" />
					</svg>

					<p class="hero-kicker">
						Preguntame lo que necesites de Programación Lineal — teoría, enunciados para
						resolver, formas canónicas. Voy a buscar en la <em>wiki curada</em> y, cuando
						haga falta, razono con el modelo.
					</p>

					<div class="suggestions">
						<div class="sug-overline">Probá con…</div>
						<div class="sug-list">
							{#each SUGGESTIONS as s, i (i)}
								<button type="button" class="sug" onclick={() => pickSuggestion(s)}>
									<span class="sug-glyph" aria-hidden="true">"</span>
									{s}
									<span class="sug-arrow" aria-hidden="true">→</span>
								</button>
							{/each}
						</div>
					</div>

					{#if statusBadge && statusBadge.tone !== 'accent'}
						<div class="hero-status" data-tone={statusBadge.tone}>
							<span class="status-dot"></span>
							{statusBadge.label}…
						</div>
					{/if}
				</section>
			{:else}
				<!-- Message stack -->
				{#each $messages as msg (msg.id)}
					<ChatBubbleLLM
						role={msg.role}
						content={msg.content}
						provider={msg.provider}
						toolCalls={msg.toolCalls}
						citations={msg.citations}
						error={msg.error}
					/>
				{/each}

				{#if $isThinking}
					<div class="thinking">
						<SlakingAvatar expression="thinking" size="sm" />
						<div class="typing">
							<span></span><span></span><span></span>
						</div>
						<span class="thinking-label"><em>Slacko</em> está pensando…</span>
					</div>
				{/if}
			{/if}

			{#if $lastError && $status === 'error'}
				<div class="err-banner" role="alert">
					<div class="err-glyph" aria-hidden="true">!</div>
					<div class="err-content">
						<div class="err-label">No pude conectar con Slacko</div>
						<div class="err-msg">{$lastError}</div>
					</div>
					<button type="button" class="retry" onclick={retry}>Reintentar</button>
				</div>
			{/if}
		</div>
	</div>

	<!-- History sidebar (drawer) -->
	<LLMSessionSidebar bind:open={sidebarOpen} />

	<!-- Composer -->
	<div class="composer">
		<div class="composer-inner">
			<div class="composer-rule" aria-hidden="true"></div>
			<div class="composer-box">
				<textarea
					bind:this={textareaEl}
					bind:value={composerValue}
					oninput={onInput}
					onkeydown={handleKey}
					placeholder="Escribí tu mensaje…"
					rows="1"
					disabled={$status === 'connecting' || $status === 'reconnecting' || $status === 'error'}
					aria-label="Mensaje para Slacko"
				></textarea>
				<button
					type="button"
					class="send"
					onclick={submit}
					disabled={!composerValue.trim() || $isThinking || $status !== 'open'}
					aria-label="Enviar"
				>
					<span class="send-glyph">→</span>
				</button>
			</div>
			<div class="composer-hint">
				<span><span class="key">Enter</span> para enviar</span>
				<span class="hint-sep">·</span>
				<span><span class="key">Shift</span><span class="key-plus">+</span><span class="key">Enter</span> para nueva línea</span>
			</div>
		</div>
	</div>
</div>

<style>
	/* Layout shell --------------------------------------------------------- */
	.llm-page {
		position: relative;
		display: flex;
		flex-direction: column;
		min-height: 100%;
		isolation: isolate;
	}

	.paper-bg {
		position: absolute;
		inset: 0;
		z-index: -1;
		background:
			radial-gradient(
				ellipse 70% 35% at 50% 0%,
				color-mix(in srgb, var(--color-primary) 6%, transparent) 0%,
				transparent 70%
			),
			radial-gradient(
				ellipse 60% 70% at 100% 100%,
				color-mix(in srgb, var(--color-accent) 5%, transparent) 0%,
				transparent 60%
			);
		pointer-events: none;
	}

	.paper-bg::after {
		content: '';
		position: absolute;
		inset: 0;
		background-image: linear-gradient(
			to right,
			color-mix(in srgb, var(--color-accent) 4%, transparent) 1px,
			transparent 1px
		);
		background-size: 72px 100%;
		opacity: 0.4;
		mask-image: linear-gradient(to bottom, transparent, black 40%, transparent);
	}

	/* Header --------------------------------------------------------------- */
	.lh-header {
		position: sticky;
		top: 0;
		z-index: 5;
		padding: 0.55rem 1.5rem;
		background-color: color-mix(in srgb, var(--color-surface) 92%, transparent);
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
		border-bottom: 1px solid var(--color-bot-border);
	}

	.lh-inner {
		max-width: 920px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.lh-left {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-wrap: wrap;
		min-width: 0;
	}

	.hist-btn {
		width: 32px;
		height: 32px;
		border-radius: 8px;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink-muted);
		cursor: pointer;
		font-family: var(--font-mono);
		font-size: 0.85rem;
		line-height: 1;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		flex-shrink: 0;
	}

	.hist-btn:hover {
		color: var(--color-primary);
		border-color: var(--color-primary);
	}

	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-ink);
		padding: 0.3rem 0.7rem 0.3rem 0.5rem;
		border-radius: 999px;
		background: var(--color-surface-card);
		border: 1px solid transparent;
		position: relative;
	}

	.chip::before {
		content: '';
		position: absolute;
		inset: -1px;
		border-radius: inherit;
		padding: 1px;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		-webkit-mask:
			linear-gradient(#000 0 0) content-box,
			linear-gradient(#000 0 0);
		mask:
			linear-gradient(#000 0 0) content-box,
			linear-gradient(#000 0 0);
		-webkit-mask-composite: xor;
		mask-composite: exclude;
		pointer-events: none;
	}

	.chip-rail {
		width: 4px;
		height: 4px;
		border-radius: 50%;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		animation: pulse 2.4s infinite ease-in-out;
	}

	.chip-glyph {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-accent);
		font-size: 0.95rem;
		line-height: 1;
	}

	.title {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.92rem;
		color: var(--color-ink);
		max-width: 320px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.status-pill {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-mono);
		font-size: 0.58rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		padding: 0.22rem 0.65rem;
		border-radius: 999px;
		background: var(--color-surface-warm);
		color: var(--color-ink-muted);
	}

	.status-pill[data-tone='accent'] {
		background: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface-card));
		color: var(--color-accent);
	}

	.status-pill[data-tone='warning'] {
		background: color-mix(in srgb, var(--color-warning) 12%, var(--color-surface-card));
		color: var(--color-warning);
	}

	.status-pill[data-tone='error'] {
		background: color-mix(in srgb, var(--color-error) 10%, var(--color-surface-card));
		color: var(--color-error);
	}

	.status-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: currentColor;
		animation: pulse 1.4s infinite ease-in-out;
	}

	.lh-right {
		display: flex;
		align-items: center;
		gap: 0.65rem;
	}

	.lh-btn {
		font-family: var(--font-body);
		font-size: 0.78rem;
		padding: 0.42rem 0.9rem;
		border-radius: 999px;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		border: 1px solid var(--color-bot-border);
		background: var(--color-surface-card);
		color: var(--color-ink);
	}

	.lh-btn:hover {
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.btn-glyph {
		font-family: var(--font-mono);
		font-size: 0.9rem;
		color: var(--color-accent);
		line-height: 1;
	}

	/* Scroll + column ------------------------------------------------------ */
	.lh-scroll {
		flex: 1;
		overflow-y: auto;
		scroll-behavior: smooth;
	}

	.lh-scroll::-webkit-scrollbar {
		width: 8px;
	}
	.lh-scroll::-webkit-scrollbar-thumb {
		background: var(--color-bot-border);
		border-radius: 4px;
	}
	.lh-scroll::-webkit-scrollbar-thumb:hover {
		background: var(--color-ink-muted);
	}

	.lh-column {
		max-width: 920px;
		margin: 0 auto;
		padding: 1.5rem 1.5rem 45vh 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	/* Hero ---------------------------------------------------------------- */
	.hero {
		position: relative;
		text-align: center;
		padding: 3rem 1.25rem 1rem 1.25rem;
		animation: fadeUp 0.5s ease-out;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.hero-overline {
		display: inline-flex;
		align-items: center;
		gap: 0.65rem;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.3em;
		text-transform: uppercase;
		color: var(--color-accent);
		margin-bottom: 1.5rem;
	}

	.ov-dot {
		width: 4px;
		height: 4px;
		border-radius: 50%;
		background: currentColor;
		opacity: 0.7;
	}

	.hero-avatar-wrap {
		margin-bottom: 1rem;
		display: inline-flex;
		position: relative;
	}

	.hero-avatar-wrap::after {
		content: '';
		position: absolute;
		inset: -8px;
		border-radius: 50%;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		opacity: 0.18;
		filter: blur(14px);
		z-index: -1;
	}

	.hero-title {
		font-family: var(--font-display);
		font-size: clamp(1.9rem, 3vw, 2.4rem);
		line-height: 1.1;
		margin: 0 0 0.5rem 0;
		font-weight: 400;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		-webkit-background-clip: text;
		background-clip: text;
		-webkit-text-fill-color: transparent;
		color: transparent;
		display: inline-block;
	}

	.hero-title em {
		font-style: italic;
	}

	.hero-title .drop {
		font-style: italic;
		font-size: 1.2em;
	}

	.hero-arc {
		display: block;
		width: 220px;
		height: 32px;
		margin: 0.2rem auto 1rem auto;
	}

	.hero-kicker {
		font-family: var(--font-display);
		font-size: 1.05rem;
		line-height: 1.65;
		color: var(--color-ink-light);
		font-style: italic;
		max-width: 540px;
		margin: 0 0 2rem 0;
	}

	.hero-kicker em {
		color: var(--color-primary);
		font-style: italic;
	}

	.suggestions {
		width: 100%;
		max-width: 580px;
		text-align: left;
	}

	.sug-overline {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.22em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-bottom: 0.7rem;
		text-align: center;
	}

	.sug-list {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	.sug {
		display: flex;
		align-items: center;
		gap: 0.7rem;
		padding: 0.75rem 1rem 0.8rem 0.85rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		font-family: var(--font-body);
		font-size: 0.88rem;
		color: var(--color-ink);
		text-align: left;
		cursor: pointer;
		line-height: 1.45;
		width: 100%;
	}

	.sug:hover {
		border-color: var(--color-accent);
		transform: translateY(-1px);
		box-shadow: 0 6px 16px -10px rgba(212, 168, 83, 0.5);
	}

	.sug-glyph {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-accent);
		font-size: 1.5rem;
		line-height: 0.8;
		flex-shrink: 0;
		margin-top: -0.15rem;
	}

	.sug-arrow {
		margin-left: auto;
		font-family: var(--font-display);
		color: var(--color-ink-muted);
		transition: transform 0.18s ease;
		flex-shrink: 0;
	}

	.sug:hover .sug-arrow {
		color: var(--color-primary);
		transform: translateX(3px);
	}

	.hero-status {
		margin-top: 1.5rem;
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
	}

	.hero-status[data-tone='warning'] {
		color: var(--color-warning);
	}

	.hero-status[data-tone='error'] {
		color: var(--color-error);
	}

	/* Thinking indicator -------------------------------------------------- */
	.thinking {
		display: grid;
		grid-template-columns: 48px auto auto;
		gap: 0.65rem;
		align-items: center;
		animation: fadeUp 0.25s ease-out;
	}

	.typing {
		display: inline-flex;
		gap: 6px;
		padding: 0.7rem 0.95rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px 14px 14px 4px;
		width: fit-content;
	}

	.typing span {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: var(--color-ink-muted);
		animation: bounce 1.2s infinite ease-in-out both;
	}

	.typing span:nth-child(2) {
		animation-delay: 0.15s;
	}
	.typing span:nth-child(3) {
		animation-delay: 0.3s;
	}

	.thinking-label {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.85rem;
		color: var(--color-ink-muted);
	}

	.thinking-label em {
		color: var(--color-primary);
	}

	/* Error banner -------------------------------------------------------- */
	.err-banner {
		display: grid;
		grid-template-columns: 36px 1fr auto;
		gap: 0.85rem;
		padding: 0.85rem 1rem 0.95rem 0.85rem;
		background: color-mix(in srgb, var(--color-error) 6%, transparent);
		border-left: 3px solid var(--color-error);
		border-radius: 0 8px 8px 0;
		align-items: center;
	}

	.err-glyph {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		border: 1px solid var(--color-error);
		color: var(--color-error);
		font-family: var(--font-display);
		font-weight: 700;
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}

	.err-content {
		min-width: 0;
	}

	.err-label {
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-error);
		margin-bottom: 0.1rem;
	}

	.err-msg {
		font-size: 0.85rem;
		color: var(--color-ink);
		word-break: break-word;
	}

	.retry {
		font-family: var(--font-body);
		font-size: 0.75rem;
		padding: 0.4rem 0.85rem;
		border-radius: 999px;
		background: var(--color-error);
		color: white;
		border: none;
		cursor: pointer;
		transition: background 0.15s ease;
		flex-shrink: 0;
	}

	.retry:hover {
		background: color-mix(in srgb, var(--color-error) 80%, var(--color-ink) 20%);
	}

	/* Composer ------------------------------------------------------------ */
	.composer {
		background: var(--color-surface);
		padding: 0.85rem 1.5rem 1.1rem 1.5rem;
		border-top: 1px solid transparent;
	}

	.composer-inner {
		max-width: 920px;
		margin: 0 auto;
		position: relative;
	}

	.composer-rule {
		height: 1px;
		background: linear-gradient(
			to right,
			transparent,
			var(--color-primary) 30%,
			var(--color-accent) 70%,
			transparent
		);
		opacity: 0.35;
		margin-bottom: 0.75rem;
	}

	.composer-box {
		display: grid;
		grid-template-columns: 1fr auto;
		align-items: end;
		gap: 0.65rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 18px;
		padding: 0.6rem 0.6rem 0.6rem 1rem;
	}

	.composer-box:focus-within {
		border-color: var(--color-primary);
		box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary) 12%, transparent);
	}

	textarea {
		width: 100%;
		resize: none;
		border: none;
		outline: none;
		background: transparent;
		font-family: var(--font-body);
		font-size: 0.95rem;
		line-height: 1.55;
		color: var(--color-ink);
		padding: 0.4rem 0;
		max-height: 168px;
		overflow-y: auto;
	}

	textarea:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	textarea::placeholder {
		color: var(--color-ink-muted);
		font-style: italic;
		font-family: var(--font-display);
	}

	.send {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		color: white;
		border: none;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.send:hover:not(:disabled) {
		transform: translateY(-1px) scale(1.04);
		box-shadow: 0 10px 22px -10px color-mix(in srgb, var(--color-primary) 60%, transparent);
	}

	.send:disabled {
		opacity: 0.35;
		cursor: not-allowed;
		background: var(--color-ink-muted);
	}

	.send-glyph {
		font-family: var(--font-display);
		font-size: 1.3rem;
		line-height: 1;
	}

	.composer-hint {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.72rem;
		color: var(--color-ink-muted);
		margin: 0.6rem 0 0 0;
	}

	.hint-sep {
		opacity: 0.5;
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

	/* Animations ---------------------------------------------------------- */
	@keyframes fadeUp {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes pulse {
		0%,
		100% {
			transform: scale(1);
			opacity: 1;
		}
		50% {
			transform: scale(1.4);
			opacity: 0.45;
		}
	}

	@keyframes bounce {
		0%,
		80%,
		100% {
			transform: scale(0.6);
			opacity: 0.4;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	/* Responsive ---------------------------------------------------------- */
	@media (max-width: 700px) {
		.lh-header {
			padding: 0.55rem 1rem;
		}
		.lh-column {
			padding: 1.25rem 1rem 2rem 1rem;
		}
		.composer {
			padding: 0.7rem 1rem 0.95rem 1rem;
		}
		.title {
			max-width: 160px;
		}
		.hero {
			padding-top: 2rem;
		}
	}
</style>
