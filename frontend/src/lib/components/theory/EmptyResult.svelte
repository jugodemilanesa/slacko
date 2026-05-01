<script lang="ts">
	import type { ConceptSummary } from '$lib/api/theory';

	let {
		message,
		suggestions,
		question,
		onSelect
	}: {
		message: string;
		suggestions: ConceptSummary[];
		question: string;
		onSelect: (id: string) => void;
	} = $props();
</script>

<section class="empty step-enter">
	<div class="ornament" aria-hidden="true">
		<svg viewBox="0 0 120 60" width="120" height="60">
			<path
				d="M5 30 Q 30 5, 60 30 T 115 30"
				fill="none"
				stroke="currentColor"
				stroke-width="1"
				stroke-linecap="round"
				opacity="0.5"
			/>
			<circle cx="60" cy="30" r="3" fill="currentColor" opacity="0.7" />
			<circle cx="60" cy="30" r="8" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3" />
		</svg>
	</div>

	<p class="overline">No reconocí ese tema</p>
	<h2 class="title">«{question}»</h2>
	<p class="message">{message}</p>

	{#if suggestions.length > 0}
		<div class="suggestions">
			<div class="suggestions-label">¿Querés explorar alguno de estos?</div>
			<div class="suggestions-grid">
				{#each suggestions as s}
					<button
						type="button"
						class="suggestion"
						onclick={() => onSelect(s.id)}
					>
						<div class="s-title">{s.title}</div>
						<div class="s-summary">{s.summary}</div>
					</button>
				{/each}
			</div>
		</div>
	{/if}
</section>

<style>
	.empty {
		text-align: center;
		padding: 2rem 1.5rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		max-width: 720px;
		margin: 0 auto;
	}

	.ornament {
		color: var(--color-accent);
		margin-bottom: 1rem;
		display: flex;
		justify-content: center;
	}

	.overline {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		margin-bottom: 0.4rem;
	}

	.title {
		font-family: var(--font-display);
		font-size: 1.75rem;
		color: var(--color-ink);
		line-height: 1.2;
		margin: 0 0 0.75rem 0;
	}

	.message {
		font-size: 0.95rem;
		color: var(--color-ink-light);
		line-height: 1.6;
		max-width: 480px;
		margin: 0 auto 1.5rem auto;
	}

	.suggestions {
		text-align: left;
		max-width: 600px;
		margin: 0 auto;
	}

	.suggestions-label {
		font-family: var(--font-mono);
		font-size: 0.65rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		text-align: center;
		margin-bottom: 1rem;
	}

	.suggestions-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 0.75rem;
	}

	.suggestion {
		text-align: left;
		background: var(--color-surface);
		border: 1px solid var(--color-bot-border);
		border-left: 2px solid var(--color-accent);
		border-radius: 6px;
		padding: 0.75rem 1rem;
		cursor: pointer;
		transition: all 0.18s ease;
	}

	.suggestion:hover {
		border-left-color: var(--color-primary);
		background: var(--color-surface-warm);
		transform: translateY(-1px);
	}

	.s-title {
		font-family: var(--font-display);
		color: var(--color-ink);
		font-size: 1rem;
		margin-bottom: 0.2rem;
	}

	.s-summary {
		font-size: 0.78rem;
		color: var(--color-ink-muted);
		line-height: 1.45;
	}
</style>
