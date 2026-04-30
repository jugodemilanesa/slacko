<script lang="ts">
	import { onMount } from 'svelte';
	import { isAuthenticated } from '$lib/api/client';
	import { goto } from '$app/navigation';

	onMount(() => {
		if (isAuthenticated()) {
			goto('/chat');
		} else {
			goto('/login');
		}
	});
</script>

<div class="flex items-center justify-center min-h-screen">
	<p class="text-gray-500">Cargando...</p>
</div>
