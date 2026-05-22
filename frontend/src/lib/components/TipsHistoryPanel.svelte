<script lang="ts">
	import { tipsHistory, STEP_LABELS, type TipEntry } from '$lib/stores/chat';

	const kindColors: Record<string, { bg: string; border: string; text: string }> = {
		tip: { bg: 'rgba(212,168,83,0.06)', border: '#d4a853', text: '#d4a853' },
		concept: { bg: 'rgba(59,76,192,0.06)', border: '#3b4cc0', text: '#3b4cc0' },
		warning: { bg: 'rgba(212,72,72,0.06)', border: '#d44848', text: '#d44848' },
		question: { bg: 'rgba(26,26,46,0.03)', border: '#6b6982', text: '#6b6982' },
		note: { bg: 'rgba(212,168,83,0.06)', border: '#d4a853', text: '#d4a853' }
	};

	const kindLabels: Record<string, string> = {
		tip: '✦ Slacko tip',
		concept: '§ Concepto',
		warning: '! Cuidado',
		question: '? Pensalo',
		note: '¶ Nota'
	};

	const groups = $derived.by(() => {
		const result: Record<string, TipEntry[]> = {};
		for (const t of $tipsHistory) {
			const label = STEP_LABELS[t.step] || t.step;
			if (!result[label]) result[label] = [];
			result[label].push(t);
		}
		return result;
	});
</script>

<aside class="tips-panel" aria-label="Historial de tips y conceptos">
	<div class="tips-scroll">
		{#each Object.entries(groups) as [stepLabel, tips]}
			<div class="step-group">
				<div class="step-heading">{stepLabel}</div>
				<div class="tip-list">
					{#each tips as tip (tip.id)}
							{@const colors = kindColors[tip.kind] || kindColors.tip}
							<div class="tip-entry" style="border-left-color: {colors.border}; background: {colors.bg};">
								<div class="tip-header" style="color: {colors.text};">
									{kindLabels[tip.kind] || tip.kind}
									{#if tip.title}
										<span class="tip-dot">·</span>
										<span class="tip-title">{tip.title}</span>
									{/if}
								</div>
								<div class="tip-body">
									{tip.content}
								</div>
							</div>
						{/each}
					</div>
				</div>
			{/each}
	</div>
</aside>

<style>
	.tips-panel {
		width: 300px;
		background: var(--color-surface-card, #fffaf2);
		border-left: 1px solid var(--color-bot-border, #e5e2dc);
		display: flex;
		flex-direction: column;
		overflow: hidden;
		flex-shrink: 0;
	}

	.tips-scroll {
		flex: 1;
		overflow-y: auto;
		padding: 0.6rem 0.75rem 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.6rem;
	}

	.step-group {
		margin-bottom: 0.25rem;
	}

	.step-heading {
		font-family: var(--font-mono, 'JetBrains Mono');
		font-size: 0.58rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted, #6b6982);
		margin-bottom: 0.35rem;
		padding: 0 0.1rem;
	}

	.tip-list {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.tip-entry {
		padding: 0.5rem 0.6rem 0.55rem 0.55rem;
		border-left: 2px solid;
		border-radius: 0 6px 6px 0;
		animation: fadeIn 0.2s ease-out;
	}

	.tip-header {
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		display: flex;
		align-items: baseline;
		gap: 0.25rem;
		margin-bottom: 0.2rem;
	}

	.tip-dot {
		opacity: 0.4;
	}

	.tip-title {
		letter-spacing: 0.08em;
		opacity: 0.9;
	}

	.tip-body {
		font-size: 0.72rem;
		line-height: 1.45;
		color: var(--color-ink-light, #4a4a6a);
		overflow: hidden;
		display: -webkit-box;
		-webkit-line-clamp: 3;
		-webkit-box-orient: vertical;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateX(-3px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}
</style>
