<script lang="ts">
	import { marked } from 'marked';

	let { content }: { content: string } = $props();

	marked.setOptions({
		gfm: true,
		breaks: false
	});

	const html = $derived(marked.parse(content) as string);
</script>

<div class="markdown-body">
	{@html html}
</div>

<style>
	.markdown-body :global(p) {
		font-family: var(--font-body);
		color: var(--color-ink-light);
		line-height: 1.75;
		font-size: 1.0625rem;
		margin: 0 0 1.1em 0;
	}

	.markdown-body :global(p:last-child) {
		margin-bottom: 0;
	}

	.markdown-body :global(strong) {
		color: var(--color-ink);
		font-weight: 600;
	}

	.markdown-body :global(em) {
		color: var(--color-ink-light);
		font-style: italic;
	}

	.markdown-body :global(ul),
	.markdown-body :global(ol) {
		margin: 0 0 1.1em 0;
		padding-left: 1.25em;
		color: var(--color-ink-light);
		line-height: 1.75;
	}

	.markdown-body :global(ul) {
		list-style: none;
	}

	.markdown-body :global(ul li) {
		position: relative;
		padding-left: 1em;
		margin-bottom: 0.4em;
	}

	.markdown-body :global(ul li::before) {
		content: '';
		position: absolute;
		left: 0;
		top: 0.7em;
		width: 0.4em;
		height: 1px;
		background: var(--color-accent);
	}

	.markdown-body :global(ol) {
		list-style: none;
		counter-reset: ordered;
		padding-left: 0;
	}

	.markdown-body :global(ol li) {
		counter-increment: ordered;
		position: relative;
		padding-left: 2.2em;
		margin-bottom: 0.5em;
	}

	.markdown-body :global(ol li::before) {
		content: counter(ordered, decimal-leading-zero);
		position: absolute;
		left: 0;
		top: 0.05em;
		font-family: var(--font-mono);
		font-size: 0.78em;
		color: var(--color-accent);
		letter-spacing: 0.05em;
		font-weight: 500;
	}

	.markdown-body :global(blockquote) {
		margin: 1.25em 0;
		padding: 1em 1.25em;
		border-left: 3px solid var(--color-accent);
		background: var(--color-surface-warm);
		border-radius: 0 8px 8px 0;
		font-style: italic;
		color: var(--color-ink-light);
	}

	.markdown-body :global(blockquote p) {
		margin-bottom: 0;
	}

	.markdown-body :global(code) {
		font-family: var(--font-mono);
		font-size: 0.875em;
		background: var(--color-surface-warm);
		color: var(--color-ink);
		padding: 0.15em 0.45em;
		border-radius: 4px;
		border: 1px solid rgba(212, 168, 83, 0.2);
	}

	.markdown-body :global(pre) {
		font-family: var(--font-mono);
		font-size: 0.875em;
		background: var(--color-surface-warm);
		color: var(--color-ink);
		padding: 1em 1.25em;
		border-radius: 8px;
		border: 1px solid var(--color-bot-border);
		overflow-x: auto;
		margin: 1em 0;
	}

	.markdown-body :global(pre code) {
		background: transparent;
		border: none;
		padding: 0;
	}

	.markdown-body :global(h1),
	.markdown-body :global(h2),
	.markdown-body :global(h3) {
		font-family: var(--font-display);
		color: var(--color-ink);
		margin-top: 1.5em;
		margin-bottom: 0.5em;
		line-height: 1.2;
	}

	.markdown-body :global(h2) {
		font-size: 1.5rem;
	}

	.markdown-body :global(h3) {
		font-size: 1.25rem;
	}

	.markdown-body :global(a) {
		color: var(--color-primary);
		text-decoration: underline;
		text-decoration-thickness: 1px;
		text-underline-offset: 2px;
	}
</style>
