<script lang="ts">
	import SlakingAvatar from './SlakingAvatar.svelte';
	import type { Expression, ChatState } from '$lib/stores/chat';

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
		(content || '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')
	);

	$effect(() => {
		if (animate && role === 'assistant') {
			let tokens: { char: string; isBold: boolean }[] = [];
			let isBold = false;
			let text = content || '';
			for (let i = 0; i < text.length; i++) {
				if (text[i] === '*' && text[i + 1] === '*') {
					isBold = !isBold;
					i++;
					continue;
				}
				if (text[i] === '\n') {
					tokens.push({ char: '<br/>', isBold });
					continue;
				}
				let char = String.fromCodePoint(text.codePointAt(i) || text.charCodeAt(i));
				tokens.push({ char, isBold });
				if (char.length > 1) {
					i += char.length - 1;
				}
			}

			let length = 0;
			displayedHtml = '';
			const interval = setInterval(() => {
				if (length <= tokens.length) {
					let html = '';
					let currentlyBold = false;
					for (let i = 0; i < length; i++) {
						if (tokens[i].isBold && !currentlyBold) {
							html += '<strong>';
							currentlyBold = true;
						}
						if (!tokens[i].isBold && currentlyBold) {
							html += '</strong>';
							currentlyBold = false;
						}
						html += tokens[i].char;
					}
					if (currentlyBold) html += '</strong>';
					displayedHtml = html;
					length++;
				} else {
					clearInterval(interval);
				}
			}, 1000 / 90); // 90 chars per second

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
