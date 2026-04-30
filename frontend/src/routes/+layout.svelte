<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<title>Slacko - Tutor de Investigación Operativa</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	{@render children()}
</div>
