<script lang="ts">
	import { marked } from 'marked';
	import DOMPurify from 'isomorphic-dompurify';

	import SlakingAvatar from '$lib/components/SlakingAvatar.svelte';
	import ToolCallChip from './ToolCallChip.svelte';
	import CitationLink from './CitationLink.svelte';
	import ParseProblemArtifact from './ParseProblemArtifact.svelte';
	import SolveLpArtifact from './SolveLpArtifact.svelte';

	import type { ChatToolCall } from '$lib/api/chat';

	let {
		role,
		content,
		provider,
		model,
		toolCalls = [],
		citations = [],
		error = null,
		hideTrack = false,
		animate = false,
		isLast = false
	}: {
		role: 'user' | 'assistant';
		content: string;
		provider?: string;
		model?: string;
		toolCalls?: ChatToolCall[];
		citations?: string[];
		error?: string | null;
		hideTrack?: boolean;
		animate?: boolean;
		isLast?: boolean;
	} = $props();

	import { onMount } from 'svelte';

	marked.setOptions({ gfm: true, breaks: false });

	let displayedHtml = $state('');
	let progress = $state(0);
	let trueFinalSpineHeight = $state<number | null>(null);
	let currentSpineHeight = $state(0);

	// Sanitizamos la salida del LLM antes de inyectarla como HTML ({@html}):
	// marked no escapa el HTML inline, así que sin esto sería un sink de XSS.
	const parsed = $derived(
		role === 'assistant' ? DOMPurify.sanitize(marked.parse(content || '') as string) : ''
	);

	onMount(() => {
		const r = role;
		const a = animate;
		
		if (a && r === 'assistant') {
			let tokens: string[] = [];
			let i = 0;
			while (i < parsed.length) {
				if (parsed[i] === '<') {
					let start = i;
					while (i < parsed.length && parsed[i] !== '>') i++;
					tokens.push(parsed.slice(start, i + 1));
					i++;
				} else if (parsed[i] === '&') {
					let start = i;
					while (i < parsed.length && parsed[i] !== ';') i++;
					tokens.push(parsed.slice(start, i + 1));
					i++;
				} else {
					let char = String.fromCodePoint(parsed.codePointAt(i) || parsed.charCodeAt(i));
					tokens.push(char);
					if (char.length > 1) i += char.length;
					else i++;
				}
			}

			let totalVisible = tokens.filter(t => !t.startsWith('<')).length;
			let length = 0;
			let visibleLength = 0;
			let html = '';
			
			// Si el primer token es un tag, agregarlo instantáneamente
			while (length < tokens.length && tokens[length].startsWith('<')) {
				html += tokens[length];
				length++;
			}
			displayedHtml = html;
			progress = totalVisible > 0 ? visibleLength / totalVisible : 1;

			const speed = 180; // chars por segundo
			const startTime = Date.now();
			
			const interval = setInterval(() => {
				const elapsed = (Date.now() - startTime) / 1000;
				const targetVisible = Math.floor(elapsed * speed);

				while (visibleLength < targetVisible && length < tokens.length) {
					html += tokens[length];
					if (!tokens[length].startsWith('<')) visibleLength++;
					length++;
					
					while (length < tokens.length && tokens[length].startsWith('<')) {
						html += tokens[length];
						length++;
					}
				}

				displayedHtml = html;
				progress = totalVisible > 0 ? visibleLength / totalVisible : 1;
				
				if (trueFinalSpineHeight && totalVisible > 0) {
					// Precalcular la velocidad constante en función de la distancia y letras por minuto
					const distancia = trueFinalSpineHeight;
					const cantidadLetras = totalVisible;
					const velocidadLetrasPorMinuto = speed * 60; // speed es chars/seg, así que * 60 = chars/min
					const minutosTotal = cantidadLetras / velocidadLetrasPorMinuto;
					const velocidadLineaPorMinuto = distancia / minutosTotal;
					
					const elapsedMinutes = elapsed / 60;
					currentSpineHeight = Math.min(distancia, elapsedMinutes * velocidadLineaPorMinuto);
				}
				
				if (length >= tokens.length) {
					progress = 1;
					if (trueFinalSpineHeight) currentSpineHeight = trueFinalSpineHeight;
					clearInterval(interval);
				}
			}, 16);

			return () => clearInterval(interval);
		} else {
			displayedHtml = parsed;
			progress = 1;
		}
	});

	// Artifact selection: show ParseProblem artifact for any successful parse,
	// SolveLp artifact for any successful solve/graph. Multiple artifacts in
	// one turn are rare but supported.
	const parseTools = $derived(
		toolCalls.filter((t) => t.name === 'parse_problem' && t.result_summary === 'ok')
	);
	const solveTools = $derived(
		toolCalls.filter(
			(t) =>
				(t.name === 'solve_lp' || t.name === 'graph_lp') && t.result_summary === 'ok'
		)
	);
</script>

{#if role === 'user'}
	<div class="turn user-turn" class:is-last={hideTrack}>
		{#if !hideTrack}
			<div class="user-track" aria-hidden="true"></div>
		{/if}
		<div class="user-bubble">
			<div class="user-meta">
				<span>Vos</span>
			</div>
			<p class="user-text">{content}</p>
		</div>
	</div>
{:else}
	<div class="turn bot-turn" class:has-error={!!error} class:is-last={hideTrack}>
		{#if animate && role === 'assistant' && progress < 1}
			<!-- Hidden precalc clone to get the exact final distance for the line -->
			<div style="position: absolute; visibility: hidden; pointer-events: none; width: 100%; top: 0; left: 0; display: grid; grid-template-columns: 48px 1fr; gap: 0.55rem 1rem; align-items: stretch;" aria-hidden="true">
				<div class="marginalia">
					<SlakingAvatar expression={error ? 'sad' : 'explain'} size="sm" />
					<span bind:clientHeight={trueFinalSpineHeight} style="flex: 1; min-height: 36px; margin-bottom: 10px;"></span>
				</div>
				<div class="bot-content">
					{#if error}
						<div class="err-banner">
							<div class="err-super-title">Falla del LLM — respondí con el matcher determinístico</div>
							<div class="err-detail">{error}</div>
						</div>
					{/if}
					<div style="position: relative; width: 100%;">
						<div class="bubble">
							<div class="prose">{@html parsed}</div>
						</div>
					</div>
				</div>
			</div>
		{/if}

		<div class="marginalia" class:is-finished={progress === 1} class:is-latest={isLast} aria-hidden="true">
			<SlakingAvatar expression={error ? 'sad' : 'explain'} size="sm" />
			<span class="spine" style={animate && progress < 1 ? `height: ${currentSpineHeight}px; min-height: 0; flex: none;` : ''}></span>
		</div>

		<div class="bot-content">
			{#if error}
				<div class="err-banner" role="alert">
					<div class="err-super-title">Falla del LLM — respondí con el matcher determinístico</div>
					<div class="err-detail">{error}</div>
				</div>
			{/if}

			<div style="position: relative; width: 100%;">
				<div class="bubble">
					<div class="prose">{@html displayedHtml}</div>
				</div>
			</div>
		</div>

		{#if !hideTrack}
			<div class="bot-track" aria-hidden="true"></div>
		{/if}

		<div class="bot-accessories">
			{#if progress === 1}
				<div class="accessories-content">
					{#if toolCalls.length > 0 || citations.length > 0}
						<div class="chips">
							{#each toolCalls as tool, i (i)}
								<ToolCallChip {tool} />
								{#if tool.name === 'theory_lookup'}
									{#each citations as c, j (j)}
										<CitationLink citation={c} />
									{/each}
								{/if}
							{/each}
							{#if !toolCalls.some(t => t.name === 'theory_lookup') && citations.length > 0}
								{#each citations as c, i (i)}
									<CitationLink citation={c} />
								{/each}
							{/if}
						</div>
					{/if}

					{#each parseTools as t, i (i)}
						<ParseProblemArtifact args={t.arguments} />
					{/each}

					{#each solveTools as t, i (i)}
						<SolveLpArtifact toolName={t.name as 'solve_lp' | 'graph_lp'} args={t.arguments} />
					{/each}
				</div>
			{/if}
			
		</div>
	</div>
{/if}

<style>
	.turn {
		animation: fadeUp 0.3s ease-out;
	}

	/* User turn ------------------------------------------------------------ */
	.user-turn {
		display: flex;
		justify-content: flex-end;
		position: relative;
	}

	.user-track {
		position: absolute;
		top: 0;
		bottom: calc(-1.5rem - 0.3rem - 16px); /* Reaches the center of the bot avatar below */
		left: 23px; /* 24px center - 1px half-width = 23px */
		width: 2px;
		background: var(--color-primary);
		-webkit-mask-image: linear-gradient(to bottom, transparent 50%, black 50%);
		-webkit-mask-size: 2px 16px;
		mask-image: linear-gradient(to bottom, transparent 50%, black 50%);
		mask-size: 2px 16px;
		opacity: 0.5;
		z-index: 0;
	}

	:global(.dark) .user-track {
		background: var(--color-accent);
	}

	.user-bubble {
		max-width: 78%;
		background: linear-gradient(
			180deg,
			var(--color-primary),
			color-mix(in srgb, var(--color-primary) 88%, var(--color-ink) 12%)
		);
		color: white;
		padding: 0.75rem 1.05rem 0.85rem 1.05rem;
		border-radius: 16px 16px 4px 16px;
		box-shadow:
			0 1px 0 rgba(26, 26, 46, 0.04),
			0 12px 24px -16px rgba(59, 76, 192, 0.45);
	}

	.user-meta {
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		opacity: 0.8;
		margin-bottom: 0.3rem;
	}

	.user-text {
		margin: 0;
		font-family: var(--font-body);
		font-size: 0.95rem;
		line-height: 1.55;
		white-space: pre-wrap;
		word-break: break-word;
	}

	/* Bot turn ------------------------------------------------------------- */
	.bot-turn {
		display: grid;
		grid-template-columns: 48px 1fr;
		gap: 0.55rem 1rem;
		align-items: stretch;
		position: relative;
	}

	.marginalia {
		grid-column: 1;
		grid-row: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.4rem;
		padding-top: 0.3rem;
		position: relative;
		z-index: 1;
	}

	/* The spine is the gradient indigo→gold mentioned in the brief — it sits
	   below the avatar and visually signals "LLM with curated grounding". */
	.spine {
		width: 2px;
		flex: 1;
		min-height: 36px;
		margin-bottom: 10px; /* 6px shift + 4px to reach dot center */
		background: linear-gradient(
			180deg,
			var(--color-primary),
			var(--color-accent)
		);
		opacity: 0.65;
		border-radius: 1px;
		position: relative;
		z-index: -1;
	}

	:global(.dark) .spine {
		background: linear-gradient(
			180deg,
			var(--color-accent),
			var(--color-primary)
		);
	}

	.spine::after {
		content: '';
		position: absolute;
		left: 50%;
		bottom: -4px;
		width: 8px;
		height: 8px;
		background: var(--color-accent);
		border-radius: 50%;
		transform: translateX(-50%) scale(0);
		box-shadow: 0 0 8px var(--color-accent);
		opacity: 0;
		z-index: 2;
	}

	.marginalia.is-finished .spine::after {
		animation: dotAppear 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
	}

	.marginalia.is-finished.is-latest .spine::before {
		content: '';
		position: absolute;
		left: 50%;
		bottom: -4px;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		transform: translateX(-50%);
		z-index: 1;
		animation:
			burstShockwave 2s cubic-bezier(0.1, 0.9, 0.2, 1) forwards,
			pulseShockwave 2s infinite 2s;
	}

	:global(.dark) .spine::after {
		background: var(--color-primary);
		box-shadow: 0 0 6px var(--color-primary);
	}

	:global(.dark) .marginalia.is-finished .spine::after {
		animation: dotAppear 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
	}

	:global(.dark) .marginalia.is-finished.is-latest .spine::before {
		animation:
			burstShockwaveDark 2s cubic-bezier(0.1, 0.9, 0.2, 1) forwards,
			pulseShockwaveDark 2s infinite 2s;
	}

	@keyframes dotAppear {
		from {
			opacity: 0;
			transform: translateX(-50%) scale(0);
		}
		to {
			opacity: 0.9;
			transform: translateX(-50%) scale(1);
		}
	}

	@keyframes burstShockwave {
		0% {
			box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-accent) 90%, transparent);
		}
		100% {
			box-shadow: 0 0 0 48px transparent;
		}
	}

	@keyframes burstShockwaveDark {
		0% {
			box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-primary) 90%, transparent);
		}
		100% {
			box-shadow: 0 0 0 48px transparent;
		}
	}

	@keyframes pulseShockwave {
		0% {
			box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-accent) 50%, transparent);
		}
		70% {
			box-shadow: 0 0 0 10px transparent;
		}
		100% {
			box-shadow: 0 0 0 0 transparent;
		}
	}

	@keyframes pulseShockwaveDark {
		0% {
			box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-primary) 50%, transparent);
		}
		70% {
			box-shadow: 0 0 0 10px transparent;
		}
		100% {
			box-shadow: 0 0 0 0 transparent;
		}
	}

	.bot-content {
		grid-column: 2;
		grid-row: 1;
		min-width: 0;
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	.bot-accessories {
		grid-column: 2;
		grid-row: 2;
		min-width: 0;
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	.accessories-content {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
		animation: fadeUp 0.4s ease-out;
	}

	.bot-track {
		grid-column: 1;
		grid-row: 2;
		position: relative;
	}

	.bot-track::after {
		content: '';
		position: absolute;
		top: calc(-0.55rem - 10px); /* Starts exactly at the center of the shifted dot */
		bottom: -1.5rem;
		left: 50%;
		transform: translateX(-50%);
		width: 2px;
		background: linear-gradient(180deg, var(--color-accent), var(--color-primary));
		-webkit-mask-image: linear-gradient(to bottom, transparent 50%, black 50%);
		-webkit-mask-size: 2px 16px;
		mask-image: linear-gradient(to bottom, transparent 50%, black 50%);
		mask-size: 2px 16px;
		opacity: 0.5;
		z-index: 0;
	}

	:global(.dark) .bot-track::after {
		background: linear-gradient(180deg, var(--color-primary), var(--color-accent));
	}

	/* Force hide tracks if it's the last message */
	.is-last .user-track,
	.is-last .bot-track,
	:global(.lh-column > .turn:last-child .user-track),
	:global(.lh-column > .turn:last-child .bot-track) {
		display: none !important;
	}

	/* The very first track should extend upwards infinitely for overscroll */
	:global(.lh-column > .turn:first-child .user-track),
	:global(.lh-column > .turn:first-child .bot-track::after) {
		top: -100vh;
	}

	/* Bubble --------------------------------------------------------------- */
	.bubble {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px;
		padding: 0.85rem 1.15rem 0.95rem 1.15rem;
		box-shadow: 0 1px 0 rgba(26, 26, 46, 0.02);
	}

	.bot-turn.has-error .bubble {
		border-left: 3px solid var(--color-error);
		border-radius: 14px;
	}

	/* Prose styling — mirrors MarkdownBody but a tone tighter for chat ---- */
	.prose :global(p) {
		font-family: var(--font-body);
		color: var(--color-ink);
		line-height: 1.65;
		font-size: 0.96rem;
		margin: 0 0 0.7em 0;
	}

	.prose :global(p:last-child) {
		margin-bottom: 0;
	}

	.prose :global(strong) {
		color: var(--color-ink);
		font-weight: 600;
	}

	.prose :global(em) {
		font-style: italic;
		color: var(--color-ink-light);
	}

	.prose :global(ul),
	.prose :global(ol) {
		margin: 0.25rem 0 0.7rem 0;
		padding-left: 1.2rem;
		color: var(--color-ink);
		line-height: 1.65;
	}

	.prose :global(ul) {
		list-style: none;
	}

	.prose :global(ul li) {
		position: relative;
		padding-left: 0.85rem;
	}

	.prose :global(ul li::before) {
		content: '◇';
		font-family: var(--font-display);
		color: var(--color-accent);
		position: absolute;
		left: -0.05rem;
		top: 0.05rem;
		font-size: 0.78rem;
	}

	.prose :global(ol) {
		list-style: none;
		counter-reset: olc;
	}

	.prose :global(ol li) {
		position: relative;
		padding-left: 1.35rem;
		counter-increment: olc;
	}

	.prose :global(ol li::before) {
		content: counter(olc, decimal-leading-zero);
		font-family: var(--font-mono);
		color: var(--color-accent);
		position: absolute;
		left: 0;
		top: 0.05rem;
		font-size: 0.72rem;
		font-weight: 600;
	}

	.prose :global(code) {
		font-family: var(--font-mono);
		font-size: 0.85em;
		background: var(--color-surface-warm);
		padding: 0.1em 0.4em;
		border-radius: 3px;
		color: var(--color-ink);
	}

	.prose :global(pre) {
		background: var(--color-surface-warm);
		padding: 0.75rem 1rem;
		border-radius: 8px;
		overflow-x: auto;
		margin: 0.5rem 0 0.7rem 0;
		font-size: 0.85rem;
	}

	.prose :global(pre code) {
		background: transparent;
		padding: 0;
	}

	.prose :global(blockquote) {
		border-left: 2px solid var(--color-accent);
		padding-left: 0.85rem;
		margin: 0.5rem 0 0.7rem 0;
		font-style: italic;
		color: var(--color-ink-light);
	}

	.prose :global(h1),
	.prose :global(h2),
	.prose :global(h3) {
		font-family: var(--font-display);
		color: var(--color-ink);
		margin: 0.6em 0 0.4em 0;
		font-weight: 500;
		line-height: 1.2;
	}

	.prose :global(h1) {
		font-size: 1.25rem;
	}

	.prose :global(h2) {
		font-size: 1.1rem;
	}

	.prose :global(h3) {
		font-size: 0.98rem;
	}

	.prose :global(a) {
		color: var(--color-primary);
		text-decoration: underline;
		text-decoration-style: dotted;
		text-underline-offset: 2px;
	}

	/* Chips and footer -------------------------------------------- */
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}
	/* Errors --------------------------------------------------------------- */
	.err-banner {
		padding: 0.55rem 0.85rem 0.65rem 0.85rem;
		background: color-mix(in srgb, var(--color-error) 6%, transparent);
		border-left: 3px solid var(--color-error);
		border-radius: 0 6px 6px 0;
	}

	.err-super-title {
		font-family: var(--font-mono);
		font-size: 0.58rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-error);
		margin-bottom: 0.2rem;
	}

	.err-detail {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.82rem;
		color: var(--color-ink-light);
		word-break: break-word;
	}

	/* Animations ----------------------------------------------------------- */
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

	/* Responsive ----------------------------------------------------------- */
	@media (max-width: 700px) {
		.bot-turn {
			grid-template-columns: 36px 1fr;
			gap: 0.6rem;
		}
		.user-bubble {
			max-width: 88%;
		}
	}
</style>
