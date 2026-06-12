<script lang="ts">
	type TipKind = 'tip' | 'concept' | 'warning' | 'question' | 'note';

	let {
		kind = 'tip',
		title = '',
		collapsible = false,
		open = true,
		dense = false,
		children
	}: {
		kind?: TipKind;
		title?: string;
		collapsible?: boolean;
		open?: boolean;
		dense?: boolean;
		children: any;
	} = $props();

	const glyph: Record<TipKind, string> = {
		tip: '✦',
		concept: '§',
		warning: '!',
		question: '?',
		note: '¶'
	};

	const superTitle: Record<TipKind, string> = {
		tip: 'Slacko tip',
		concept: 'Concepto',
		warning: 'Cuidado',
		question: 'Pensalo',
		note: 'Nota al margen'
	};

	let isOpen = $state(open);
</script>

<aside
	class="slacko-tip"
	class:dense
	data-kind={kind}
	aria-label={superTitle[kind]}
>
	<div class="marker" aria-hidden="true">
		<span class="glyph">{glyph[kind]}</span>
	</div>
	<div class="body">
		<header class="tip-head">
			<span class="super-title">{superTitle[kind]}</span>
			{#if title}
				<span class="dot">·</span>
				<span class="title">{title}</span>
			{/if}
			{#if collapsible}
				<button
					type="button"
					class="toggle"
					aria-expanded={isOpen}
					onclick={() => (isOpen = !isOpen)}
				>
					{isOpen ? '−' : '+'}
				</button>
			{/if}
		</header>
		{#if !collapsible || isOpen}
			<div class="content">
				{@render children()}
			</div>
		{/if}
	</div>
</aside>

<style>
	.slacko-tip {
		display: grid;
		grid-template-columns: 28px 1fr;
		gap: 0.85rem;
		padding: 0.85rem 1rem 0.95rem 0.75rem;
		background-color: color-mix(in srgb, var(--color-accent, #d4a853) 4%, transparent);
		border-left: 2px solid var(--color-accent, #d4a853);
		border-radius: 0 8px 8px 0;
		font-family: var(--font-body, 'Plus Jakarta Sans');
		position: relative;
		animation: fadeIn 0.25s ease-out;
		transition: background-color 0.25s ease-in-out, border-color 0.25s ease-in-out, color 0.25s ease-in-out;
	}

	.slacko-tip.dense {
		padding: 0.5rem 0.8rem 0.55rem 0.55rem;
		gap: 0.6rem;
	}

	.slacko-tip::before {
		content: '';
		position: absolute;
		left: -2px;
		top: -1px;
		height: 18px;
		width: 18px;
		border-top: 2px solid var(--color-accent, #d4a853);
		border-left: 2px solid var(--color-accent, #d4a853);
		border-top-left-radius: 4px;
		opacity: 0.35;
		transition: border-color 0.25s ease-in-out;
	}

	.slacko-tip[data-kind='warning'] {
		border-left-color: var(--color-error, #d44848);
		background-color: color-mix(in srgb, var(--color-error, #d44848) 5%, transparent);
	}
	.slacko-tip[data-kind='warning']::before {
		border-color: var(--color-error, #d44848);
	}

	.slacko-tip[data-kind='concept'] {
		border-left-color: var(--color-primary, #3b4cc0);
		background-color: color-mix(in srgb, var(--color-primary, #3b4cc0) 5%, transparent);
	}
	.slacko-tip[data-kind='concept']::before {
		border-color: var(--color-primary, #3b4cc0);
	}

	.slacko-tip[data-kind='question'] {
		border-left-style: dashed;
	}

	.marker {
		display: flex;
		justify-content: center;
		padding-top: 0.1rem;
	}

	.glyph {
		font-family: var(--font-display, 'EB Garamond');
		font-style: italic;
		font-size: 1.35rem;
		line-height: 1;
		color: var(--color-accent, #d4a853);
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 26px;
		height: 26px;
		border-radius: 50%;
		border: 1px solid currentColor;
		background-color: var(--color-surface-card, #fffaf2);
		transition: background-color 0.25s ease-in-out, border-color 0.25s ease-in-out, color 0.25s ease-in-out;
	}

	.slacko-tip.dense .glyph {
		font-size: 1.05rem;
		width: 20px;
		height: 20px;
	}

	.slacko-tip[data-kind='warning'] .glyph {
		color: var(--color-error, #d44848);
		font-weight: 700;
		font-style: normal;
	}

	.slacko-tip[data-kind='concept'] .glyph {
		color: var(--color-primary, #3b4cc0);
		font-style: normal;
	}

	.slacko-tip[data-kind='question'] .glyph {
		color: var(--color-ink, #1a1a2e);
		font-weight: 600;
		font-style: normal;
	}

	.tip-head {
		display: flex;
		align-items: baseline;
		gap: 0.35rem;
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-ink-muted, #6b6982);
		margin-bottom: 0.25rem;
	}

	.super-title {
		color: var(--color-accent, #d4a853);
	}

	.slacko-tip[data-kind='warning'] .super-title {
		color: var(--color-error, #d44848);
	}
	.slacko-tip[data-kind='concept'] .super-title {
		color: var(--color-primary, #3b4cc0);
	}

	.dot {
		opacity: 0.5;
	}

	.title {
		color: var(--color-ink, #1a1a2e);
		letter-spacing: 0.12em;
	}

	.toggle {
		margin-left: auto;
		background: transparent;
		border: 1px solid var(--color-bot-border, #e5e2dc);
		border-radius: 4px;
		width: 18px;
		height: 18px;
		font-family: var(--font-mono);
		font-size: 0.8rem;
		line-height: 1;
		color: var(--color-ink-muted);
		cursor: pointer;
		padding: 0;
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}
	.toggle:hover {
		color: var(--color-ink);
		border-color: var(--color-ink);
	}

	.content {
		font-family: var(--font-body, 'Plus Jakarta Sans');
		font-size: 0.86rem;
		line-height: 1.55;
		color: var(--color-ink-light, #4a4a6a);
	}

	.content :global(p) {
		margin: 0 0 0.5rem 0;
	}
	.content :global(p:last-child) {
		margin-bottom: 0;
	}

	.content :global(strong) {
		color: var(--color-ink, #1a1a2e);
		font-weight: 600;
	}

	.content :global(code),
	.content :global(.k) {
		font-family: var(--font-mono);
		font-size: 0.82em;
		background-color: color-mix(in srgb, var(--color-ink) 8%, transparent);
		padding: 0.05em 0.35em;
		border-radius: 3px;
		color: var(--color-ink);
		transition: background-color 0.25s ease-in-out, color 0.25s ease-in-out;
	}

	.content :global(ul) {
		margin: 0.25rem 0 0.5rem 0;
		padding-left: 1.1rem;
	}

	.content :global(li) {
		margin-bottom: 0.2rem;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateX(-4px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}
</style>
