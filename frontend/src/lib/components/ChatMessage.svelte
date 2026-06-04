<script lang="ts">
	import SlakingAvatar from './SlakingAvatar.svelte';
	import type { Expression, ChatState } from '$lib/stores/chat';
	import { onMount } from 'svelte';
	import katex from 'katex';
	import 'katex/dist/katex.min.css';

	let {
		role,
		content,
		expression = 'idle',
		step,
		animate = false
	}: {
		role: 'assistant' | 'user' | 'divider';
		content: string;
		expression?: Expression;
		step?: ChatState;
		animate?: boolean;
	} = $props();

	let displayedHtml = $state('');
	let finalWidth = $state<number | null>(null);

	const fullHtml = $derived(
		(content || '')
			.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
			.replace(/\$\$(.*?)\$\$/g, (_, math) => {
				try {
					return katex.renderToString(math, { displayMode: true, throwOnError: false });
				} catch {
					return `$$${math}$$`;
				}
			})
			.replace(/\$(.*?)\$/g, (_, math) => {
				try {
					return katex.renderToString(math, { displayMode: false, throwOnError: false });
				} catch {
					return `$${math}$`;
				}
			})
			.replace(/\n/g, '<br/>')
	);

	onMount(() => {
		if (animate && role === 'assistant') {
			let tokens: string[] = [];
			let parsed = fullHtml;
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

			let totalVisible = tokens.filter((t) => !t.startsWith('<')).length;
			let length = 0;
			let visibleLength = 0;
			let html = '';

			while (length < tokens.length && tokens[length].startsWith('<')) {
				html += tokens[length];
				length++;
			}
			displayedHtml = html;

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

				if (length >= tokens.length) {
					clearInterval(interval);
				}
			}, 16);

			return () => clearInterval(interval);
		} else {
			displayedHtml = fullHtml;
		}
	});
</script>

{#if role === 'divider'}
	<div class="flex items-center gap-3 py-2 fade-in" aria-label="step divider" data-step={step}>
		<div class="flex-1 h-px bg-bot-border"></div>
		<span
			class="text-[0.65rem] tracking-[0.18em] uppercase font-mono text-ink-muted
				bg-surface-warm px-3 py-1 rounded-full border border-bot-border"
		>
			<span class="step-text">◆ {content}</span>
		</span>
		<div class="flex-1 h-px bg-bot-border"></div>
	</div>
{:else}
	<div class="w-full flex items-end gap-2 {role === 'user' ? 'justify-end' : 'justify-start'} fade-in relative">
		{#if role === 'assistant'}
			<SlakingAvatar {expression} size="sm" ring />

			{#if animate}
				<div
					class="max-w-[85%] px-5 py-3 text-[0.95rem] leading-relaxed absolute invisible pointer-events-none inline-block"
					bind:clientWidth={finalWidth}
					aria-hidden="true"
				>
					{@html fullHtml}
				</div>
			{/if}
		{/if}

		<div
			class="max-w-[85%] px-5 py-3 rounded-2xl leading-relaxed text-[0.95rem] inline-block
				{role === 'user'
				? 'bg-primary text-user-text'
				: 'bg-bot-bg border border-bot-border text-ink shadow-sm'}"
			style={finalWidth ? `width: ${finalWidth}px;` : ''}
		>
			{@html displayedHtml}
		</div>
	</div>
{/if}
