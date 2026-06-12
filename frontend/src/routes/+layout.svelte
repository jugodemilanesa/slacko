<script lang="ts">
	import { onMount } from 'svelte';
	import { afterNavigate } from '$app/navigation';
	import { rollShiny } from '$lib/stores/shiny';
	import { ensureCsrf } from '$lib/api/client';
	import '../app.css';
	import '$lib/stores/theme';

	let { children } = $props();

	onMount(() => {
		// Asegura la cookie csrftoken para los POST/PATCH/DELETE de la sesión.
		ensureCsrf();

		const t = setTimeout(() => {
			document.body.classList.remove('preload');
		}, 100);
		return () => clearTimeout(t);
	});

	afterNavigate(() => {
		rollShiny();
	});
</script>

<svelte:head>
	<title>Slacko - Tutor de Programación Lineal</title>
</svelte:head>

<div class="min-h-screen bg-surface text-ink">
	{@render children()}
</div>
