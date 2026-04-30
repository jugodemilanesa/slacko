<script lang="ts">
	import { register } from '$lib/api/auth';
	import { goto } from '$app/navigation';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		loading = true;

		try {
			await register(username, email, password);
			goto('/chat');
		} catch (err) {
			error = err instanceof Error ? err.message : 'Error al registrarse';
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex items-center justify-center min-h-screen">
	<div class="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
		<h1 class="text-2xl font-bold text-center text-gray-800 mb-6">Registrarse</h1>

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
				<label for="email" class="block text-sm font-medium text-gray-700">Email</label>
				<input
					id="email"
					type="email"
					bind:value={email}
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
					minlength={6}
					class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
			>
				{loading ? 'Registrando...' : 'Crear cuenta'}
			</button>
		</form>

		<p class="mt-4 text-center text-sm text-gray-500">
			Ya tenes cuenta? <a href="/login" class="text-blue-600 hover:underline">Ingresa</a>
		</p>
	</div>
</div>
