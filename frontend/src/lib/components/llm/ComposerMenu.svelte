<script lang="ts">
	import { personality, setPersonality } from '$lib/stores/llmChat';

	let open = $state(false);
	let rootEl = $state<HTMLDivElement | null>(null);
	let tooltipOpen = $state(false);

	function toggle() {
		open = !open;
	}

	function close() {
		open = false;
	}

	function togglePersonality() {
		setPersonality(!$personality);
	}

	function handleDocClick(e: MouseEvent) {
		if (!rootEl) return;
		if (!rootEl.contains(e.target as Node)) close();
	}

	$effect(() => {
		document.addEventListener('click', handleDocClick);
		return () => document.removeEventListener('click', handleDocClick);
	});
</script>

<div class="menu-root" bind:this={rootEl}>
	<button
		type="button"
		class="plus-btn"
		class:active={open}
		onclick={toggle}
		aria-label="Opciones del chat"
		aria-expanded={open}
		title="Más opciones"
	>
		<span class="plus-glyph" aria-hidden="true">+</span>
	</button>

	{#if open}
		<div class="dropdown" role="menu">
			<div
				class="row"
				class:hovering={tooltipOpen}
				onmouseenter={() => (tooltipOpen = true)}
				onmouseleave={() => (tooltipOpen = false)}
				role="presentation"
			>
				<span class="row-label">Rol</span>
				<button
					type="button"
					class="toggle"
					class:on={$personality}
					role="switch"
					aria-checked={$personality}
					aria-label="Activar personalidad de Slacko"
					onclick={togglePersonality}
				>
					<span class="knob" aria-hidden="true"></span>
				</button>

				{#if tooltipOpen}
					<div class="tip" role="tooltip">
						{#if $personality}
							Slacko responde con su personalidad (perezoso pero servicial).
						{:else}
							Respuesta directa del LLM, sin personalidad ni adornos.
						{/if}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.menu-root {
		position: relative;
		display: inline-flex;
		align-items: center;
		flex-shrink: 0;
	}

	.plus-btn {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink);
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-family: var(--font-mono);
		font-size: 1.15rem;
		line-height: 1;
		padding: 0;
		transition:
			border-color 0.15s ease,
			color 0.15s ease,
			transform 0.15s ease;
	}

	.plus-btn:hover,
	.plus-btn.active {
		border-color: var(--color-primary);
		color: var(--color-primary);
		transform: translateY(-1px);
	}

	.plus-glyph {
		font-family: var(--font-display);
		font-weight: 500;
	}

	.dropdown {
		position: absolute;
		bottom: calc(100% + 0.5rem);
		left: 0;
		z-index: 20;
		min-width: 200px;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		padding: 0.45rem 0.65rem;
		box-shadow:
			0 1px 0 rgba(26, 26, 26, 0.04),
			0 14px 32px -18px rgba(0, 0, 0, 0.45);
		animation: pop 0.15s ease-out;
	}

	.row {
		position: relative;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		padding: 0.4rem 0.45rem;
		border-radius: 8px;
	}

	.row.hovering {
		background: color-mix(in srgb, var(--color-primary) 6%, transparent);
	}

	.row-label {
		font-family: var(--font-display);
		font-size: 0.9rem;
		color: var(--color-ink);
		font-weight: 500;
	}

	.toggle {
		position: relative;
		width: 36px;
		height: 20px;
		border-radius: 999px;
		border: 1px solid var(--color-bot-border);
		background: var(--color-surface-warm);
		cursor: pointer;
		padding: 0;
		transition:
			background 0.2s ease,
			border-color 0.2s ease;
	}

	.toggle.on {
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		border-color: transparent;
	}

	.knob {
		position: absolute;
		top: 2px;
		left: 2px;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: white;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
		transition: transform 0.2s ease;
	}

	.toggle.on .knob {
		transform: translateX(16px);
	}

	.tip {
		position: absolute;
		bottom: calc(100% + 0.4rem);
		left: 50%;
		transform: translateX(-50%);
		min-width: 220px;
		max-width: 260px;
		padding: 0.45rem 0.7rem;
		background: var(--color-ink);
		color: var(--color-surface);
		font-family: var(--font-body);
		font-size: 0.75rem;
		line-height: 1.4;
		border-radius: 8px;
		text-align: center;
		pointer-events: none;
		box-shadow: 0 6px 18px -8px rgba(0, 0, 0, 0.5);
		animation: fadeIn 0.15s ease-out;
		white-space: normal;
	}

	.tip::after {
		content: '';
		position: absolute;
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		border: 5px solid transparent;
		border-top-color: var(--color-ink);
	}

	@keyframes pop {
		from {
			opacity: 0;
			transform: translateY(4px) scale(0.97);
		}
		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}
</style>
