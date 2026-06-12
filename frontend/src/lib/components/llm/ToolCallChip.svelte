<script lang="ts">
	import type { ChatToolCall } from '$lib/api/chat';

	let {
		tool
	}: {
		tool: ChatToolCall;
	} = $props();

	// Map each tool name to a typographic glyph + human label. Glyphs in
	// font-display italic match the project's editorial language (cf. SlackoTip).
	const META: Record<string, { glyph: string; label: string }> = {
		theory_lookup: { glyph: '§', label: 'teoría' },
		parse_problem: { glyph: '¶', label: 'parseo' },
		solve_lp: { glyph: '∑', label: 'resolución' },
		graph_lp: { glyph: '◇', label: 'gráfico' },
		convert_form: { glyph: '↔', label: 'conversión' },
		start_guided_mode: { glyph: '→', label: 'modo guiado' },
		explain_error: { glyph: '!', label: 'feedback' }
	};

	const meta = $derived(META[tool.name] ?? { glyph: '◆', label: tool.name });

	const summary = $derived.by(() => {
		const s = tool.result_summary ?? '';
		if (s.startsWith('error:')) return { state: 'error' as const, text: s.replace('error:', '') };
		if (s === 'matched') return { state: 'ok' as const, text: 'encontrado' };
		if (s === 'ok') return { state: 'ok' as const, text: 'ok' };
		if (s === 'no_match') return { state: 'miss' as const, text: 'sin match' };
		return { state: 'ok' as const, text: s || '·' };
	});
</script>

<span class="chip" data-state={summary.state}>
	<span class="glyph" aria-hidden="true">{meta.glyph}</span>
	<span class="name">{meta.label}</span>
	<span class="sep" aria-hidden="true">·</span>
	<span class="result">{summary.text}</span>
</span>

<style>
	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.42rem;
		padding: 0.22rem 0.65rem 0.22rem 0.5rem;
		border-radius: 999px;
		font-family: var(--font-body);
		font-size: 0.72rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink-light);
		line-height: 1.4;
		white-space: nowrap;
	}

	.chip:hover {
		border-color: color-mix(in srgb, var(--color-accent) 60%, transparent);
		background: color-mix(in srgb, var(--color-accent) 5%, var(--color-surface-card));
	}

	.glyph {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.95rem;
		line-height: 1;
		color: var(--color-accent);
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 16px;
		height: 16px;
	}

	.name {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-ink);
		font-weight: 500;
	}

	.sep {
		color: var(--color-ink-muted);
		opacity: 0.6;
	}

	.result {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.78rem;
		color: var(--color-ink-light);
	}

	.chip[data-state='error'] {
		border-color: color-mix(in srgb, var(--color-error) 40%, transparent);
		background: color-mix(in srgb, var(--color-error) 6%, var(--color-surface-card));
	}
	.chip[data-state='error'] .glyph {
		color: var(--color-error);
		font-style: normal;
		font-weight: 700;
	}
	.chip[data-state='error'] .name {
		color: var(--color-error);
	}
	.chip[data-state='error'] .result {
		color: var(--color-error);
	}

	.chip[data-state='miss'] {
		border-style: dashed;
	}
	.chip[data-state='miss'] .glyph {
		color: var(--color-ink-muted);
	}
	.chip[data-state='miss'] .result {
		color: var(--color-ink-muted);
	}
</style>
