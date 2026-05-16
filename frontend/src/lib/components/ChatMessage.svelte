<script lang="ts">
	import SlakingAvatar from './SlakingAvatar.svelte';
	import type { Expression } from '$lib/stores/chat';

	let {
		role,
		content,
		expression = 'idle'
	}: {
		role: 'assistant' | 'user' | 'divider';
		content: string;
		expression?: Expression;
	} = $props();
</script>

{#if role === 'divider'}
	<div class="flex items-center gap-3 py-2 fade-in" aria-label="step divider">
		<div class="flex-1 h-px bg-bot-border"></div>
		<span
			class="text-[0.65rem] tracking-[0.18em] uppercase font-mono text-ink-muted
				bg-surface-warm px-3 py-1 rounded-full border border-bot-border"
		>
			◆ {content}
		</span>
		<div class="flex-1 h-px bg-bot-border"></div>
	</div>
{:else}
	<div class="flex items-end gap-2 {role === 'user' ? 'justify-end' : 'justify-start'} fade-in">
		{#if role === 'assistant'}
			<SlakingAvatar {expression} size="sm" ring />
		{/if}
		<div
			class="max-w-[75%] px-5 py-3 rounded-2xl leading-relaxed text-[0.95rem]
				{role === 'user'
				? 'bg-primary text-user-text rounded-br-md'
				: 'bg-bot-bg border border-bot-border text-ink rounded-bl-md shadow-sm'}"
		>
			{@html content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')}
		</div>
	</div>
{/if}
