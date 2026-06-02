<script lang="ts">
	import { login } from '$lib/api/auth';
	import { goto } from '$app/navigation';
	import { isDarkMode, toggleDarkMode } from '$lib/stores/theme';

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

<div class="relative flex items-center justify-center min-h-screen bg-surface overflow-hidden">
	<!-- Theme Switcher Button -->
	<div class="absolute top-4 right-4 z-20">
		<button
			onclick={toggleDarkMode}
			class="w-10 h-10 rounded-lg bg-surface-card border border-bot-border flex items-center justify-center
				text-ink-muted hover:text-ink hover:border-ink transition-all cursor-pointer shadow-sm hover:scale-[1.03]"
			title={$isDarkMode ? 'Modo claro' : 'Modo oscuro'}
		>
			{#if $isDarkMode}
				<!-- Sun icon -->
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
			{:else}
				<!-- Moon icon -->
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
			{/if}
		</button>
	</div>

	<!-- Background Image at the top with a gradient fading to the page background (crossfaded between themes) -->
	<div class="absolute top-0 left-0 right-0 h-[420px] pointer-events-none select-none z-0 overflow-hidden" style="mask-image: linear-gradient(to bottom, black 0%, black 40%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, black 0%, black 40%, transparent 100%);">
		<!-- Light mode background -->
		<div class="absolute inset-0 light-bg-image bg-crossfade-container">
			<img src="/background.jpg" alt="" class="w-full h-full object-cover object-top opacity-35" />
		</div>
		
		<!-- Dark mode background -->
		<div class="absolute inset-0 dark-bg-image bg-crossfade-container">
			<img src="/background-dark.jpg" alt="" class="w-full h-full object-cover object-top opacity-35" />
		</div>
	</div>

	<div class="relative z-10 w-full max-w-md p-8 bg-surface-card rounded-lg shadow-lg border border-bot-border">
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
