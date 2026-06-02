<script lang="ts">
	import '../app.css';
	import '$lib/stores/theme';

	let { children } = $props();
</script>

<svelte:head>
	<title>Slacko - Tutor de Programación Lineal</title>
</svelte:head>

<div class="min-h-screen bg-surface text-ink">
	{@render children()}
</div>
