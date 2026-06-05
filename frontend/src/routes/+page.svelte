<script lang="ts">
	import { onMount } from 'svelte';
	import { checkAuth } from '$lib/api/auth';
	import { goto } from '$app/navigation';

	onMount(async () => {
		// La sesión vive en una cookie httpOnly: preguntamos al backend.
		goto((await checkAuth()) ? '/chat' : '/login');
	});
</script>

<div class="flex items-center justify-center min-h-screen">
	<p class="text-gray-500">Cargando...</p>
</div>
