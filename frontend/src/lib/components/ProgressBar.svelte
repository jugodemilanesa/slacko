<script lang="ts">
	import { currentStepIndex, STEP_ORDER, STEP_LABELS, type ChatState } from '$lib/stores/chat';

	const totalSteps = STEP_ORDER.length;
</script>

<div class="flex items-center gap-1.5 w-full">
	{#each STEP_ORDER as step, i}
		{@const isActive = i === $currentStepIndex}
		{@const isDone = i < $currentStepIndex}
		<div class="flex-1 group relative">
			<div
				class="h-1.5 rounded-full transition-all duration-500
					{isDone ? 'bg-accent' : isActive ? 'bg-primary' : 'bg-ink/10'}"
			></div>
			<div
				class="absolute -top-7 left-1/2 -translate-x-1/2 text-[0.65rem] font-medium whitespace-nowrap
					opacity-0 group-hover:opacity-100 transition-opacity px-2 py-0.5 rounded
					{isDone ? 'text-accent' : isActive ? 'text-primary' : 'text-ink-muted'}"
			>
				{STEP_LABELS[step]}
			</div>
		</div>
	{/each}
</div>
