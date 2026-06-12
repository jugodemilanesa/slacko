<script lang="ts">
	import { onMount } from 'svelte';
	import { register, loginWithGoogle, preloadGoogle } from '$lib/api/auth';
	import { goto } from '$app/navigation';
	import AuthShell from '$lib/components/auth/AuthShell.svelte';
	import GoogleButton from '$lib/components/auth/GoogleButton.svelte';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let error = $state('');
	let notice = $state('');
	let loading = $state(false);
	let googleLoading = $state(false);

	onMount(() => preloadGoogle());

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

	async function handleGoogle() {
		error = '';
		googleLoading = true;
		try {
			const res = await loginWithGoogle();
			if (res.linkedExisting) {
				notice = 'Ya tenías una cuenta con este correo. La vinculamos con tu cuenta de Google.';
			} else {
				goto('/chat');
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'No se pudo iniciar el login con Google';
		} finally {
			googleLoading = false;
		}
	}
</script>

<AuthShell eyebrow="CREÁ TU CUENTA">
	{#if notice}
		<div class="auth-notice">{notice}</div>
		<button type="button" class="auth-submit" onclick={() => goto('/chat')}>
			<span>Ir a Slacko</span>
			<span class="auth-submit-arrow" aria-hidden="true">→</span>
		</button>
	{:else}
	<form onsubmit={handleSubmit} class="space-y-4">
		{#if error}
			<div class="p-3 text-sm text-error bg-error/10 border border-error/20 rounded-lg whitespace-pre-line">
				{error}
			</div>
		{/if}

		<div>
			<label for="username" class="block text-xs font-semibold uppercase tracking-wide text-ink-muted mb-1.5">
				Usuario
			</label>
			<input
				id="username"
				type="text"
				autocomplete="username"
				bind:value={username}
				required
				minlength={3}
				maxlength={30}
				pattern="[\w.\-]&#123;3,30&#125;"
				class="auth-input"
			/>
			<p class="auth-hint">3–30 caracteres: letras, números, punto, guion o guion bajo.</p>
		</div>

		<div>
			<label for="email" class="block text-xs font-semibold uppercase tracking-wide text-ink-muted mb-1.5">
				Email
			</label>
			<input
				id="email"
				type="email"
				autocomplete="email"
				bind:value={email}
				required
				class="auth-input"
			/>
			<p class="auth-hint">Tu correo es tu identidad — el mismo que uses para entrar con Google.</p>
		</div>

		<div>
			<label for="password" class="block text-xs font-semibold uppercase tracking-wide text-ink-muted mb-1.5">
				Contraseña
			</label>
			<input
				id="password"
				type="password"
				autocomplete="new-password"
				bind:value={password}
				required
				minlength={8}
				class="auth-input"
			/>
			<p class="auth-hint">Mínimo 8 caracteres. Evitá contraseñas comunes o solo numéricas.</p>
		</div>

		<button type="submit" disabled={loading} class="auth-submit">
			<span>{loading ? 'Creando cuenta…' : 'Crear cuenta'}</span>
			{#if !loading}<span class="auth-submit-arrow" aria-hidden="true">→</span>{/if}
		</button>
	</form>

	<div class="auth-divider"><span>o</span></div>

	<GoogleButton
		label={googleLoading ? 'Conectando…' : 'Registrarte con Google'}
		disabled={googleLoading}
		onclick={handleGoogle}
	/>

	<p class="mt-7 text-center text-sm text-ink-muted">
		¿Ya tenés cuenta?
		<a href="/login" class="text-primary hover:text-primary-light hover:underline font-medium">Ingresá</a>
	</p>
	{/if}
</AuthShell>
