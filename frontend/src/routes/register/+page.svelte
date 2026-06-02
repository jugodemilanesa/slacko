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

<div class="flex items-center justify-center min-h-screen bg-surface">
	<div class="w-full max-w-md p-8 bg-surface-card rounded-lg shadow-lg border border-bot-border">
		<h1 class="text-3xl font-bold text-center text-ink mb-6 font-display">Registrarse</h1>

		<form onsubmit={handleSubmit} class="space-y-4">
			{#if error}
				<div class="p-3 text-sm text-error bg-error/10 border border-error/20 rounded whitespace-pre-line">{error}</div>
			{/if}

			<div>
				<label for="username" class="block text-sm font-medium text-ink-light">Usuario</label>
				<input
					id="username"
					type="text"
					bind:value={username}
					required
					class="mt-1 w-full px-3 py-2 border border-bot-border bg-surface text-ink rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-surface-card"
				/>
			</div>

			<div>
				<label for="email" class="block text-sm font-medium text-ink-light">Email</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					required
					class="mt-1 w-full px-3 py-2 border border-bot-border bg-surface text-ink rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-surface-card"
				/>
			</div>

			<div>
				<label for="password" class="block text-sm font-medium text-ink-light">Contraseña</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					required
					minlength={6}
					class="mt-1 w-full px-3 py-2 border border-bot-border bg-surface text-ink rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-surface-card"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full py-2 px-4 bg-primary text-white font-medium rounded-md hover:bg-primary-light transition-colors cursor-pointer disabled:opacity-50"
			>
				{loading ? 'Registrando...' : 'Crear cuenta'}
			</button>
		</form>

		<p class="mt-6 text-center text-sm text-ink-muted">
			¿Ya tenés cuenta? <a href="/login" class="text-primary hover:text-primary-light hover:underline font-medium">Ingresá</a>
		</p>
	</div>
</div>
