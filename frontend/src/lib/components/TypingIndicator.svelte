<script lang="ts">
	import SlakingAvatar from './SlakingAvatar.svelte';
</script>

<div class="flex items-end gap-2 justify-start fade-in" aria-label="Slacko está escribiendo">
	<SlakingAvatar expression="thinking" size="sm" ring />
	<div
		class="bg-bot-bg border border-bot-border rounded-2xl rounded-bl-md shadow-sm
			px-4 py-3 flex items-center gap-1"
	>
		<span class="dot"></span>
		<span class="dot" style="animation-delay: 150ms"></span>
		<span class="dot" style="animation-delay: 300ms"></span>
	</div>
</div>

<style>
	.dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: var(--color-ink-muted, #6b7280);
		opacity: 0.5;
		animation: bounce 1s infinite ease-in-out;
	}
	@keyframes bounce {
		0%, 80%, 100% {
			transform: translateY(0);
			opacity: 0.4;
		}
		40% {
			transform: translateY(-4px);
			opacity: 1;
		}
	}
</style>
