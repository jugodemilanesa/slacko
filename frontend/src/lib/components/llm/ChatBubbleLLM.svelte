<script lang="ts">
	import { marked } from 'marked';

	import SlakingAvatar from '$lib/components/SlakingAvatar.svelte';
	import ToolCallChip from './ToolCallChip.svelte';
	import CitationLink from './CitationLink.svelte';
	import ProviderBadge from './ProviderBadge.svelte';
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
		error
	}: {
		role: 'user' | 'assistant';
		content: string;
		provider?: string;
		model?: string;
		toolCalls?: ChatToolCall[];
		citations?: string[];
		error?: string;
	} = $props();

	marked.setOptions({ gfm: true, breaks: false });

	const renderedHtml = $derived(role === 'assistant' ? (marked.parse(content) as string) : '');

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
	<div class="turn user-turn">
		<div class="user-bubble">
			<div class="user-meta">
				<span>Vos</span>
			</div>
			<p class="user-text">{content}</p>
		</div>
	</div>
{:else}
	<div class="turn bot-turn" class:has-error={!!error}>
		<div class="marginalia" aria-hidden="true">
			<SlakingAvatar expression={error ? 'sad' : 'explain'} size="sm" />
			<span class="spine"></span>
		</div>

		<div class="bot-body">
			{#if error}
				<div class="err-banner" role="alert">
					<div class="err-overline">Falla del LLM — respondí con el matcher determinístico</div>
					<div class="err-detail">{error}</div>
				</div>
			{/if}

			<div class="bubble">
				<div class="prose">{@html renderedHtml}</div>
			</div>

			{#if toolCalls.length > 0}
				<div class="chips">
					{#each toolCalls as tool, i (i)}
						<ToolCallChip {tool} />
					{/each}
				</div>
			{/if}

			{#each parseTools as t, i (i)}
				<ParseProblemArtifact args={t.arguments} />
			{/each}

			{#each solveTools as t, i (i)}
				<SolveLpArtifact toolName={t.name as 'solve_lp' | 'graph_lp'} args={t.arguments} />
			{/each}

			{#if citations.length > 0}
				<div class="citations">
					<span class="cite-label" aria-hidden="true">
						<span class="cite-glyph">§</span>
						Referencias
					</span>
					<div class="cite-list">
						{#each citations as c, i (i)}
							<CitationLink citation={c} />
						{/each}
					</div>
				</div>
			{/if}

			<div class="footer">
				<ProviderBadge {provider} {model} />
			</div>
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
		gap: 1rem;
		align-items: flex-start;
	}

	.marginalia {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.4rem;
		padding-top: 0.3rem;
	}

	/* The spine is the gradient indigo→gold mentioned in the brief — it sits
	   below the avatar and visually signals "LLM with curated grounding". */
	.spine {
		width: 1.5px;
		flex: 1;
		min-height: 36px;
		background: linear-gradient(
			180deg,
			var(--color-primary),
			color-mix(in srgb, var(--color-primary) 50%, var(--color-accent)) 50%,
			var(--color-accent) 80%,
			transparent
		);
		opacity: 0.65;
		border-radius: 1px;
	}

	.bot-body {
		min-width: 0;
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	/* Bubble --------------------------------------------------------------- */
	.bubble {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px 14px 14px 4px;
		padding: 0.85rem 1.15rem 0.95rem 1.15rem;
		box-shadow: 0 1px 0 rgba(26, 26, 46, 0.02);
	}

	.bot-turn.has-error .bubble {
		border-left: 3px solid var(--color-error);
		border-radius: 14px 14px 14px 0;
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

	/* Chips, citations, footer -------------------------------------------- */
	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.citations {
		display: flex;
		align-items: center;
		gap: 0.65rem;
		flex-wrap: wrap;
		padding-top: 0.2rem;
	}

	.cite-label {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-family: var(--font-mono);
		font-size: 0.58rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
	}

	.cite-glyph {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-accent);
		font-size: 0.85rem;
	}

	.cite-list {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
	}

	.footer {
		display: flex;
		justify-content: flex-end;
		padding-top: 0.15rem;
	}

	/* Errors --------------------------------------------------------------- */
	.err-banner {
		padding: 0.55rem 0.85rem 0.65rem 0.85rem;
		background: color-mix(in srgb, var(--color-error) 6%, transparent);
		border-left: 3px solid var(--color-error);
		border-radius: 0 6px 6px 0;
	}

	.err-overline {
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
