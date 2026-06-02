<script lang="ts">
	import { currentStepIndex, STEP_ORDER, STEP_LABELS, type ChatState } from '$lib/stores/chat';

	const totalSteps = STEP_ORDER.length;

	function scrollToStep(step: ChatState) {
		const container = document.getElementById('chat-container');
		if (!container) return;
		const divider = container.querySelector(`[data-step="${step}"]`);
		if (divider) {
			divider.scrollIntoView({ behavior: 'smooth', block: 'start' });

			// Trigger sweeping flash animation
			const textSpan = divider.querySelector('.step-text');
			if (textSpan) {
				textSpan.classList.remove('flash-sweep');
				void (textSpan as HTMLElement).offsetWidth; // Force reflow
				textSpan.classList.add('flash-sweep');

				// Remove class after animation finishes (1.6s)
				textSpan.addEventListener(
					'animationend',
					() => {
						textSpan.classList.remove('flash-sweep');
					},
					{ once: true }
				);
			}
		}
	}
</script>

<div class="flex items-center gap-1.5 w-full">
	{#each STEP_ORDER as step, i}
		{@const isActive = i === $currentStepIndex}
		{@const isDone = i < $currentStepIndex}
		<div class="flex-1 group relative">
			<button
				type="button"
				class="step-dot h-1.5 w-full rounded-full transition-all duration-500 cursor-pointer
					{isDone ? 'bg-accent' : isActive ? 'bg-primary' : 'bg-ink/10 hover:bg-ink/30'}"
				aria-label="Ir a paso: {STEP_LABELS[step]}"
				onclick={() => scrollToStep(step)}
			></button>
			<div
				class="absolute top-full -mt-1 left-1/2 -translate-x-1/2 text-[0.65rem] font-medium whitespace-nowrap
					opacity-0 group-hover:opacity-100 transition-opacity px-2 py-0.5 rounded pointer-events-none
					{isDone ? 'text-accent' : isActive ? 'text-primary' : 'text-ink-muted'}"
			>
				{STEP_LABELS[step]}
			</div>
		</div>
	{/each}
</div>
