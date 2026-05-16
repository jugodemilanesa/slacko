<script lang="ts">
	import type { QueryHistoryEntry } from '$lib/stores/theory';

	let {
		history,
		onSelect
	}: {
		history: QueryHistoryEntry[];
		onSelect: (entry: QueryHistoryEntry) => void;
	} = $props();
</script>

{#if history.length > 0}
	<div class="history">
		<div class="history-label font-mono">Recientes</div>
		<div class="history-list">
			{#each history as entry, i (entry.id)}
				{#if i > 0}
					<span class="sep" aria-hidden="true">—</span>
				{/if}
				<button
					type="button"
					class="entry"
					class:matched={entry.matchedConceptId !== null}
					title={entry.matchedTitle ?? 'Sin coincidencia'}
					onclick={() => onSelect(entry)}
				>
					{entry.question}
				</button>
			{/each}
		</div>
	</div>
{/if}

<style>
	.history {
		display: flex;
		align-items: baseline;
		gap: 0.85rem;
		padding: 0.6rem 0;
		max-width: 100%;
		overflow-x: auto;
		flex-wrap: wrap;
	}

	.history-label {
		flex-shrink: 0;
		font-size: 0.6rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
	}

	.history-list {
		display: flex;
		align-items: baseline;
		gap: 0.6rem;
		flex-wrap: wrap;
	}

	.sep {
		color: var(--color-ink-muted);
		opacity: 0.4;
		font-family: var(--font-display);
	}

	.entry {
		font-family: var(--font-display);
		font-size: 0.95rem;
		font-style: italic;
		color: var(--color-ink-muted);
		background: transparent;
		border: none;
		cursor: pointer;
		padding: 0.1rem 0;
		max-width: 280px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		transition: color 0.15s ease;
		text-align: left;
	}

	.entry:hover {
		color: var(--color-primary);
	}

	.entry.matched {
		color: var(--color-ink-light);
	}

	.entry.matched:hover {
		color: var(--color-primary);
	}
</style>
