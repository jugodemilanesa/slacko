<script lang="ts">
	import { isDarkMode, toggleDarkMode } from '$lib/stores/theme';
	import type { Snippet } from 'svelte';

	// Subtítulo contextual chico bajo el branding (ej. "Iniciá sesión").
	let { eyebrow = 'TUTOR DE PROGRAMACIÓN LINEAL', children }: {
		eyebrow?: string;
		children: Snippet;
	} = $props();
</script>

<div class="relative flex items-center justify-center min-h-screen bg-surface overflow-hidden">
	<!-- Theme switcher -->
	<div class="absolute top-4 right-4 z-20">
		<button
			onclick={toggleDarkMode}
			class="w-10 h-10 rounded-lg bg-surface-card border border-bot-border flex items-center justify-center
				text-ink-muted hover:text-ink hover:border-ink transition-all cursor-pointer shadow-sm hover:scale-[1.03]"
			title={$isDarkMode ? 'Modo claro' : 'Modo oscuro'}
			aria-label={$isDarkMode ? 'Activar modo claro' : 'Activar modo oscuro'}
		>
			{#if $isDarkMode}
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
			{:else}
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
			{/if}
		</button>
	</div>

	<!-- Atmósfera: imagen de fondo con máscara, crossfade entre temas (misma que la entrada al chat) -->
	<div class="absolute top-0 left-0 right-0 h-[460px] pointer-events-none select-none z-0 overflow-hidden" style="mask-image: linear-gradient(to bottom, black 0%, black 38%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, black 0%, black 38%, transparent 100%);">
		<div class="absolute inset-0 light-bg-image bg-crossfade-container">
			<img src="/background.jpg" alt="" class="w-full h-full object-cover object-top opacity-35" />
		</div>
		<div class="absolute inset-0 dark-bg-image bg-crossfade-container">
			<img src="/background-dark.jpg" alt="" class="w-full h-full object-cover object-top opacity-35" />
		</div>
	</div>

	<div class="relative z-10 w-full max-w-md px-6">
		<!-- Branding: héroe serif + eyebrow mono, espejando la pantalla principal -->
		<div class="text-center mb-7 select-none">
			<h1 class="auth-reveal font-display text-6xl text-ink tracking-tight font-normal leading-none" style="animation-delay: 60ms">
				Slacko
			</h1>
			<p
				class="auth-reveal text-[0.62rem] tracking-[0.25em] uppercase font-mono mt-3 {$isDarkMode ? 'text-accent' : 'text-primary'}"
				style="animation-delay: 160ms"
			>
				{eyebrow}
			</p>
		</div>

		<!-- Tarjeta -->
		<div class="auth-reveal relative bg-surface-card rounded-2xl shadow-xl shadow-ink/5 border border-bot-border p-7 sm:p-8" style="animation-delay: 240ms">
			{@render children()}
		</div>
	</div>
</div>

<style>
	@keyframes authReveal {
		from {
			opacity: 0;
			transform: translateY(14px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.auth-reveal {
		opacity: 0;
		animation: authReveal 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
	}
</style>
