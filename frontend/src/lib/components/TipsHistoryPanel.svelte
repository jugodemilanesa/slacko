<script lang="ts">
	import { tipsHistory, STEP_LABELS, type TipEntry } from '$lib/stores/chat';
	import katex from 'katex';
	import 'katex/dist/katex.min.css';

	let { open = true }: { open?: boolean } = $props();

		function renderLatex(text: string): string {
			return text
				.replace(/\$\$(.*?)\$\$/g, (_, math) => {
					try {
						return katex.renderToString(math, { displayMode: true, throwOnError: false });
					} catch {
						return `$$${math}$$`;
					}
				})
				.replace(/\$(?=[^$\d])([^\$\n]+?)\$/g, (_, math) => {
					try {
						return katex.renderToString(math, { displayMode: false, throwOnError: false });
					} catch {
						return `$${math}$`;
					}
				});
		}

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

	let activeTip = $state<TipEntry | null>(null);

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape' && activeTip) {
			activeTip = null;
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<aside class="tips-panel" class:closed={!open} aria-label="Historial de tips y conceptos">
	<div class="panel-content">
		<div class="tips-scroll">
			{#each Object.entries(groups) as [stepLabel, tips]}
				<div class="step-group">
					<div class="step-heading">{stepLabel}</div>
					<div class="tip-list">
						{#each tips as tip (tip.id)}
							{@const colors = kindColors[tip.kind] || kindColors.tip}
							<button
								type="button"
								class="tip-entry"
								style="border-left-color: {colors.border}; background: {colors.bg}; --hover-bg: {colors.border}18;"
								onclick={() => activeTip = tip}
							>
								<div class="tip-header" style="color: {colors.text};">
									{kindLabels[tip.kind] || tip.kind}
									{#if tip.title}
										<span class="tip-dot">·</span>
										<span class="tip-title">{tip.title}</span>
									{/if}
								</div>
								<div class="tip-body">
									{@html renderLatex(tip.content)}
								</div>
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</div>
</aside>

{#if activeTip}
	{@const activeColors = kindColors[activeTip.kind] || kindColors.tip}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div
		class="modal-backdrop"
		role="button"
		tabindex="-1"
		aria-label="Cerrar"
		onclick={() => activeTip = null}
	></div>

	<div class="modal-container" role="dialog" aria-modal="true" aria-label="Consejo completo">
		<div class="modal-card" style="border-top: 4px solid {activeColors.border};">
			<button class="modal-close" onclick={() => activeTip = null} aria-label="Cerrar"></button>

			<div class="modal-header">
				<span class="modal-kind-tag" style="color: {activeColors.text}; background: {activeColors.bg}; border: 1px solid {activeColors.border}30;">
					{kindLabels[activeTip.kind] || activeTip.kind}
				</span>
				{#if activeTip.title}
					<span class="modal-dot">·</span>
					<span class="modal-title">{activeTip.title}</span>
				{/if}
			</div>

			<div class="modal-body">
				{@html renderLatex(activeTip.content)}
			</div>

			<div class="modal-footer">
				<button
					type="button"
					class="modal-close-btn"
					style="background: {activeColors.bg}; border: 1px solid {activeColors.border}; color: {activeColors.text};"
					onclick={() => activeTip = null}
				>
					Entendido
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.tips-panel {
		width: 300px;
		background-color: var(--color-surface-card, #fffaf2);
		border-left: 1px solid var(--color-bot-border, #e5e2dc);
		display: flex;
		flex-direction: column;
		overflow: hidden;
		flex-shrink: 0;
		transition: width 0.25s ease-in-out, border-color 0.25s ease-in-out, background-color 0.25s ease-in-out, color 0.25s ease-in-out;
	}

	.tips-panel.closed {
		width: 0;
		border-left-color: transparent;
	}

	.panel-content {
		width: 300px;
		height: 100%;
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
		display: block;
		width: 100%;
		border: none;
		border-left: 2px solid;
		border-radius: 0 6px 6px 0;
		text-align: left;
		cursor: pointer;
		font-family: inherit;
		font-size: inherit;
		line-height: inherit;
		color: inherit;
		padding: 0.5rem 0.6rem 0.55rem 0.55rem;
		animation: fadeIn 0.2s ease-out;
		transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease, background-color 0.2s ease;
	}

	.tip-entry:hover {
		transform: translateY(-2px) scale(1.01);
		box-shadow: 0 6px 14px rgba(26, 26, 46, 0.06);
		background-color: var(--hover-bg) !important;
	}

	.tip-entry:active {
		transform: translateY(0) scale(1);
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

	/* ── Modal ─────────────────────────────────────────────── */
	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(26, 26, 46, 0.45);
		backdrop-filter: blur(4px);
		-webkit-backdrop-filter: blur(4px);
		z-index: 1000;
		animation: modalFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
	}

	.modal-container {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		z-index: 1001;
		width: min(500px, 90vw);
		max-height: 85vh;
		display: flex;
		animation: modalScaleIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
		will-change: transform, opacity;
	}

	.modal-card {
		background: var(--color-surface-card, #ffffff);
		border-radius: 14px;
		box-shadow: 0 24px 60px rgba(26, 26, 46, 0.18);
		width: 100%;
		display: flex;
		flex-direction: column;
		position: relative;
		overflow: hidden;
		padding: 1.75rem;
	}

	.modal-close {
		position: absolute;
		top: 0.75rem;
		right: 0.75rem;
		background: transparent;
		border: none;
		color: var(--color-ink-muted, #8888a4);
		width: 32px;
		height: 32px;
		border-radius: 50%;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		transition: all 0.15s ease;
	}

	.modal-close::after {
		content: '✕';
		font-size: 1.1rem;
		line-height: 1;
	}

	.modal-close:hover {
		color: var(--color-error, #d44848);
		background: rgba(212, 72, 72, 0.08);
		transform: scale(1.15);
	}

	.modal-header {
		display: flex;
		align-items: baseline;
		gap: 0.35rem;
		margin-bottom: 0.3rem;
		padding-right: 2rem;
	}

	.modal-kind-tag {
		font-family: var(--font-mono, 'JetBrains Mono');
		font-size: 0.58rem;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		padding: 0.15rem 0.45rem;
		border-radius: 4px;
		flex-shrink: 0;
	}

	.modal-dot {
		opacity: 0.4;
		color: var(--color-ink-muted);
	}

	.modal-title {
		font-family: var(--font-display, 'Instrument Serif');
		font-size: 1.1rem;
		font-weight: 500;
		color: var(--color-ink, #1a1a2e);
		letter-spacing: -0.01em;
	}

	.modal-body {
		font-size: 0.88rem;
		line-height: 1.65;
		color: var(--color-ink-light, #4a4a6a);
		overflow-y: auto;
		max-height: 55vh;
		padding: 1rem 0 0.5rem;
		white-space: pre-wrap;
	}

	.modal-footer {
		display: flex;
		justify-content: flex-end;
		padding-top: 1rem;
		border-top: 1px dashed var(--color-bot-border, #e5e2dc);
		margin-top: 0.75rem;
	}

	.modal-close-btn {
		font-family: var(--font-body, 'Plus Jakarta Sans');
		font-size: 0.8rem;
		font-weight: 600;
		padding: 0.5rem 1.25rem;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.15s ease;
		letter-spacing: 0.02em;
	}

	.modal-close-btn:hover {
		filter: brightness(0.92);
		transform: translateY(-1px);
	}

	@keyframes modalFadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	@keyframes modalScaleIn {
		from {
			opacity: 0;
			transform: translate(-50%, -50%) scale(0.92) translateX(30px);
		}
		to {
			opacity: 1;
			transform: translate(-50%, -50%) scale(1) translateX(0);
		}
	}
</style>
