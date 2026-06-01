<script lang="ts">
	type Expression = 'idle' | 'thinking' | 'happy' | 'sad' | 'explain';
	type Size = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

	let {
		expression = 'idle',
		size = 'md',
		alt = 'Slaking',
		floating = false,
		ring = true, // Enabled by default to show the circular frame
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
		xs: 28,
		sm: 60,
		md: 56,
		lg: 76,
		xl: 110
	};

	const pixelSize = $derived(typeof size === 'number' ? size : SIZE_MAP[size]);
	
	// Use the animated Slaking GIF
	const src = '/slaking/slaking.gif';
</script>

<div
	class="shrink-0 select-none overflow-hidden rounded-full flex items-center justify-center
		{ring ? 'ring-2 ring-bot-border mb-[-10px]' : ''}
		{floating ? 'animate-[float_3s_ease-in-out_infinite]' : ''}
		{className}"
	style="width: {pixelSize}px; height: {pixelSize}px; background: {ring ? 'linear-gradient(135deg, #a5b4fc, #fde047)' : 'transparent'};"
>
	<img
		{src}
		{alt}
		class="w-full h-full"
		style="image-rendering: pixelated; object-fit: contain; transform: scale(1.8) translate(-26%, 8%);"
		draggable="false"
	/>
</div>

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
