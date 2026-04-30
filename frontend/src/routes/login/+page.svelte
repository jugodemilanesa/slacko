<script lang="ts">
	import { login } from '$lib/api/auth';
	import { goto } from '$app/navigation';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		loading = true;

		try {
			await login(username, password);
			goto('/chat');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al iniciar sesión';
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex items-center justify-center min-h-screen">
	<div class="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
		<h1 class="text-2xl font-bold text-center text-gray-800 mb-6">Slacko</h1>
		<p class="text-center text-gray-500 mb-8">Tu tutor de Investigación Operativa</p>

		<form onsubmit={handleSubmit} class="space-y-4">
			{#if error}
				<div class="p-3 text-sm text-red-700 bg-red-100 rounded">{error}</div>
			{/if}

			<div>
				<label for="username" class="block text-sm font-medium text-gray-700">Usuario</label>
				<input
					id="username"
					type="text"
					bind:value={username}
					required
					class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>

			<div>
				<label for="password" class="block text-sm font-medium text-gray-700">Contraseña</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					required
					class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
			>
				{loading ? 'Ingresando...' : 'Ingresar'}
			</button>
		</form>

		<p class="mt-4 text-center text-sm text-gray-500">
			No tenes cuenta? <a href="/register" class="text-blue-600 hover:underline">Registrate</a>
		</p>
	</div>
</div>
