<script lang="ts">
	type Expression = 'idle' | 'thinking' | 'happy' | 'sad' | 'explain';
	type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

	let {
		expression = 'idle',
		size = 'md',
		alt = 'Slaking',
		floating = false,
		ring = false,
		class: className = ''
	}: {
		expression?: Expression;
		size?: Size | number;
		alt?: string;
		floating?: boolean;
		ring?: boolean;
		class?: string;
	} = $props();

	const SIZE_MAP: Record<Size, number> = {
		xs: 24,
		sm: 32,
		md: 44,
		lg: 64,
		xl: 96
	};

	const pixelSize = $derived(typeof size === 'number' ? size : SIZE_MAP[size]);

	// Fallback chain: <expression>.png -> <expression>.svg -> idle.svg
	let src = $state(`/slaking/${expression}.png`);
	let fallbackStep = $state(0);

	$effect(() => {
		src = `/slaking/${expression}.png`;
		fallbackStep = 0;
	});

	function handleError() {
		if (fallbackStep === 0) {
			fallbackStep = 1;
			src = `/slaking/${expression}.svg`;
		} else if (fallbackStep === 1 && expression !== 'idle') {
			fallbackStep = 2;
			src = '/slaking/idle.svg';
		}
	}
</script>

<img
	{src}
	{alt}
	width={pixelSize}
	height={pixelSize}
	onerror={handleError}
	class="shrink-0 select-none {floating ? 'animate-[float_3s_ease-in-out_infinite]' : ''}
		{ring ? 'ring-2 ring-bot-border rounded-full bg-surface-card' : ''}
		{className}"
	style="image-rendering: -webkit-optimize-contrast;"
	draggable="false"
/>

<style>
	@keyframes float {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-4px);
		}
	}
</style>
