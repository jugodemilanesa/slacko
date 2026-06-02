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

<div class="flex items-center justify-center min-h-screen bg-surface">
	<div class="w-full max-w-md p-8 bg-surface-card rounded-lg shadow-lg border border-bot-border">
		<h1 class="text-3xl font-bold text-center text-ink mb-2 font-display">Slacko</h1>
		<p class="text-center text-ink-muted mb-8 text-sm">Tu tutor de Programación Lineal</p>

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
				<label for="password" class="block text-sm font-medium text-ink-light">Contraseña</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					required
					class="mt-1 w-full px-3 py-2 border border-bot-border bg-surface text-ink rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-surface-card"
				/>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full py-2 px-4 bg-primary text-white font-medium rounded-md hover:bg-primary-light transition-colors cursor-pointer disabled:opacity-50"
			>
				{loading ? 'Ingresando...' : 'Ingresar'}
			</button>
		</form>

		<p class="mt-6 text-center text-sm text-ink-muted">
			¿No tenés cuenta? <a href="/register" class="text-primary hover:text-primary-light hover:underline font-medium">Registrate</a>
		</p>
	</div>
</div>
