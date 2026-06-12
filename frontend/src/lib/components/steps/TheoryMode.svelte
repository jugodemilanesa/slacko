<script lang="ts">
	import { onMount, tick } from 'svelte';
	import {
		queryTheory,
		getConcept,
		listCategories,
		type TheoryCategory
	} from '$lib/api/theory';
	import {
		lastQuery,
		isLoading,
		queryError,
		turns,
		pushHistory,
		pushQueryTurn,
		pushConceptTurn,
		clearTheory
	} from '$lib/stores/theory';

	import TheorySearch from '$lib/components/theory/TheorySearch.svelte';
	import ConceptCard from '$lib/components/theory/ConceptCard.svelte';
	import EmptyResult from '$lib/components/theory/EmptyResult.svelte';
	import CategoryBrowser from '$lib/components/theory/CategoryBrowser.svelte';
	import SlakingAvatar from '$lib/components/SlakingAvatar.svelte';

	let question = $state('');
	let categories = $state<TheoryCategory[]>([]);
	let stackEl = $state<HTMLDivElement | null>(null);
	let drawerOpen = $state(false);

	onMount(async () => {
		try {
			const res = await listCategories();
			categories = res.categories;
		} catch {
			// silent
		}
	});

	function categoryTitle(catId: string): string {
		return categories.find((c) => c.id === catId)?.title ?? catId.replace(/-/g, ' ');
	}

	async function scrollToBottom() {
		await tick();
		if (stackEl) {
			stackEl.scrollTo({ top: stackEl.scrollHeight, behavior: 'smooth' });
		}
	}

	async function runQuery(q: string) {
		const trimmed = q.trim();
		if (!trimmed) return;
		isLoading.set(true);
		queryError.set(null);
		lastQuery.set(trimmed);
		question = '';
		await scrollToBottom();
		try {
			const [res] = await Promise.all([
				queryTheory(trimmed),
				new Promise((r) => setTimeout(r, 450))
			]);
			pushQueryTurn(trimmed, res);
			pushHistory(trimmed, res);
			await scrollToBottom();
		} catch (e) {
			queryError.set(e instanceof Error ? e.message : 'Error al buscar');
		} finally {
			isLoading.set(false);
		}
	}

	async function openConcept(id: string, _fromId: string | null = null) {
		isLoading.set(true);
		queryError.set(null);
		drawerOpen = false;
		await scrollToBottom();
		try {
			const [res] = await Promise.all([
				getConcept(id),
				new Promise((r) => setTimeout(r, 300))
			]);
			pushConceptTurn(res.concept, res.related, _fromId);
			await scrollToBottom();
		} catch (e) {
			queryError.set(e instanceof Error ? e.message : 'Error al cargar concepto');
		} finally {
			isLoading.set(false);
		}
	}

	const hasTurns = $derived($turns.length > 0);

	function formatTime(ts: number): string {
		const d = new Date(ts);
		return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	function toggleDrawer() {
		drawerOpen = !drawerOpen;
	}

	function handleEscape(e: KeyboardEvent) {
		if (e.key === 'Escape' && drawerOpen) drawerOpen = false;
	}
</script>

<svelte:window onkeydown={handleEscape} />

<div class="theory-page" class:has-turns={hasTurns}>
	<!-- Background ornament: paper-like radial wash + faint grid -->
	<div class="paper-bg" aria-hidden="true"></div>

	<!-- Compact sticky header (only while chatting) -->
	{#if hasTurns}
		<header class="th-header compact">
			<div class="th-header-inner">
				<div class="th-header-left">
					<span class="chip">
						<span class="chip-dot" aria-hidden="true"></span>
						Modo teoría
					</span>
					<span class="turn-count">
						{$turns.length} {$turns.length === 1 ? 'consulta' : 'consultas'}
					</span>
				</div>

				<div class="th-header-right">
					<button
						type="button"
						class="th-btn ghost"
						onclick={toggleDrawer}
						aria-expanded={drawerOpen}
						aria-controls="theory-drawer"
					>
						<span class="btn-glyph" aria-hidden="true">§</span>
						Explorar temas
					</button>
					<button
						type="button"
						class="th-btn subtle"
						onclick={() => clearTheory()}
						title="Vaciar el cuaderno de consultas"
					>
						Limpiar
					</button>
				</div>
			</div>
		</header>
	{/if}

	<!-- Main scroll area -->
	<div class="th-scroll" bind:this={stackEl}>
		<div class="th-column">
			{#if !hasTurns}
				<!-- Idle hero: two-column landing -->
				<section class="hero-grid" aria-label="Bienvenida">
					<div class="hero-left">
						<div class="hero-super-title">
							<span class="ov-dot"></span>
							Cuaderno de teoría
							<span class="ov-dot"></span>
						</div>

						<h1 class="hero-title">
							<span class="drop">¿</span>De qué tema querés
							<em>conversar</em><span class="drop closing">?</span>
						</h1>

						<svg class="hero-arc" viewBox="0 0 320 60" aria-hidden="true">
							<path
								d="M5 40 Q 80 5, 160 30 T 315 40"
								fill="none"
								stroke="currentColor"
								stroke-width="1"
								stroke-linecap="round"
								opacity="0.45"
							/>
							<circle cx="160" cy="30" r="2.5" fill="currentColor" />
						</svg>

						<p class="hero-kicker">
							Preguntame sobre <em>variables slack</em>, <em>región factible</em>,
							<em>casos especiales</em> de la Programación Lineal, o lo que sea — voy a
							buscar en la bibliografía de la cátedra y devolverte el concepto con sus
							relacionados.
						</p>

						<div class="hero-cta-row">
							<button
								type="button"
								class="hero-cta"
								onclick={toggleDrawer}
							>
								<span class="cta-glyph">§</span>
								Explorar por categoría
								<span class="cta-arrow">→</span>
							</button>
							<div class="hero-avatar">
								<SlakingAvatar expression="happy" size="md" ring floating />
							</div>
						</div>
					</div>

					<div class="hero-right">
						<TheorySearch
							bind:value={question}
							loading={$isLoading}
							onSubmit={runQuery}
						/>
					</div>
				</section>
			{:else}
				<!-- Turn stack -->
				{#each $turns as turn (turn.id)}
					{#if turn.kind === 'query'}
						<div class="turn user-turn">
							<div class="user-bubble">
								<div class="user-meta">
									<span class="meta-label">Vos</span>
									<span class="meta-time">{formatTime(turn.timestamp)}</span>
								</div>
								<p class="user-text">{turn.question}</p>
							</div>
						</div>

						<div class="turn bot-turn">
							<div class="bot-marginalia" aria-hidden="true">
								<SlakingAvatar
									expression={turn.response.matched ? 'explain' : 'sad'}
									size="sm"
								/>
								<span class="margin-line"></span>
							</div>
							<div class="bot-body">
								{#if turn.response.matched}
									<ConceptCard
										concept={turn.response.concept}
										related={turn.response.related}
										categoryTitle={categoryTitle(turn.response.concept.category)}
										onSelectRelated={(id) =>
											openConcept(
												id,
												turn.response.matched ? turn.response.concept.id : null
											)
										}
									/>
								{:else}
									<EmptyResult
										message={turn.response.message}
										suggestions={turn.response.suggestions}
										question={turn.question}
										onSelect={(id) => openConcept(id, null)}
									/>
								{/if}
							</div>
						</div>
					{:else}
						<div class="turn user-turn">
							<div class="user-bubble subtle">
								<div class="user-meta">
									<span class="meta-label">Vos</span>
									<span class="meta-time">{formatTime(turn.timestamp)}</span>
								</div>
								<p class="user-text">
									Quiero ver:&nbsp;<strong>{turn.concept.title}</strong>
								</p>
							</div>
						</div>
						<div class="turn bot-turn">
							<div class="bot-marginalia" aria-hidden="true">
								<SlakingAvatar expression="explain" size="sm" />
								<span class="margin-line"></span>
							</div>
							<div class="bot-body">
								<ConceptCard
									concept={turn.concept}
									related={turn.related}
									categoryTitle={categoryTitle(turn.concept.category)}
									onSelectRelated={(id) => openConcept(id, turn.concept.id)}
								/>
							</div>
						</div>
					{/if}
				{/each}

				{#if $isLoading}
					<div class="turn bot-turn">
						<div class="bot-marginalia" aria-hidden="true">
							<SlakingAvatar expression="thinking" size="sm" />
							<span class="margin-line"></span>
						</div>
						<div class="bot-body">
							<div class="typing">
								<span></span><span></span><span></span>
							</div>
						</div>
					</div>
				{/if}
			{/if}

			{#if $queryError}
				<div class="error-banner" role="alert">
					<span class="error-glyph" aria-hidden="true">!</span>
					<div>
						<div class="error-label">Algo falló con la búsqueda</div>
						<div class="error-msg">{$queryError}</div>
					</div>
				</div>
			{/if}
		</div>
	</div>

	<!-- Composer (only while chatting) -->
	{#if hasTurns}
		<div class="composer">
			<div class="composer-inner">
				<TheorySearch
					bind:value={question}
					loading={$isLoading}
					onSubmit={runQuery}
					compact
				/>
			</div>
		</div>
	{/if}

	<!-- Drawer: floating categories panel -->
	{#if drawerOpen}
		<div
			class="drawer-backdrop"
			role="button"
			tabindex="-1"
			aria-label="Cerrar panel"
			onclick={() => (drawerOpen = false)}
			onkeydown={(e) => e.key === 'Enter' && (drawerOpen = false)}
		></div>
	{/if}
	<aside
		id="theory-drawer"
		class="drawer"
		class:open={drawerOpen}
		aria-hidden={!drawerOpen}
		aria-label="Temario por categoría"
	>
		<header class="drawer-head">
			<div>
				<div class="drawer-super-title">Explorar</div>
				<h2 class="drawer-title">Temario</h2>
			</div>
			<button
				type="button"
				class="drawer-close"
				onclick={() => (drawerOpen = false)}
				aria-label="Cerrar panel"
			>
				×
			</button>
		</header>
		<div class="drawer-body">
			<CategoryBrowser onSelect={(id) => openConcept(id, null)} />
		</div>
	</aside>
</div>

<style>
	/* Layout shell --------------------------------------------------------- */
	.theory-page {
		position: relative;
		display: flex;
		flex-direction: column;
		height: 100%;
		isolation: isolate;
	}

	.paper-bg {
		position: absolute;
		inset: 0;
		z-index: -1;
		background:
			radial-gradient(
				ellipse 80% 40% at 50% 0%,
				rgba(212, 168, 83, 0.08) 0%,
				transparent 70%
			),
			radial-gradient(
				ellipse 60% 70% at 100% 100%,
				rgba(59, 76, 192, 0.04) 0%,
				transparent 60%
			);
		pointer-events: none;
	}

	.paper-bg::after {
		content: '';
		position: absolute;
		inset: 0;
		background-image:
			linear-gradient(
				to right,
				rgba(212, 168, 83, 0.05) 1px,
				transparent 1px
			);
		background-size: 64px 100%;
		opacity: 0.25;
		mask-image: linear-gradient(to bottom, transparent, black 40%, transparent);
	}

	/* Header --------------------------------------------------------------- */
	.th-header {
		position: sticky;
		top: 0;
		z-index: 5;
		padding: 1rem 1.5rem 0.85rem 1.5rem;
		transition: padding 0.3s ease, background 0.25s ease-in-out, border-color 0.25s ease-in-out;
	}

	.th-header.compact {
		padding: 0.55rem 1.5rem;
		background: linear-gradient(
			to bottom,
			color-mix(in srgb, var(--color-surface) 96%, transparent),
			color-mix(in srgb, var(--color-surface) 85%, transparent)
		);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		border-bottom: 1px solid var(--color-bot-border);
	}

	.th-header-inner {
		max-width: 960px;
		margin: 0 auto;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.th-header-left {
		display: flex;
		align-items: center;
		gap: 0.7rem;
	}

	.chip {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-accent);
		background: rgba(212, 168, 83, 0.08);
		border: 1px solid rgba(212, 168, 83, 0.35);
		padding: 0.25rem 0.65rem;
		border-radius: 999px;
	}

	.chip-dot {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		background: var(--color-accent);
		animation: pulse 2.4s infinite ease-in-out;
	}

	.turn-count {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.78rem;
		color: var(--color-ink-muted);
	}

	.th-header-right {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.th-btn {
		font-family: var(--font-body);
		font-size: 0.78rem;
		padding: 0.45rem 0.95rem;
		border-radius: 999px;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		border: 1px solid var(--color-bot-border);
		background: var(--color-surface-card);
		color: var(--color-ink);
	}

	.th-btn:hover {
		border-color: var(--color-primary);
		color: var(--color-primary);
	}

	.th-btn.ghost {
		background: var(--color-surface-card);
	}

	.th-btn.subtle {
		background: transparent;
		color: var(--color-ink-muted);
		border-style: dashed;
	}

	.th-btn.subtle:hover {
		color: var(--color-error);
		border-color: var(--color-error);
		border-style: solid;
	}

	.btn-glyph {
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.95rem;
		color: var(--color-accent);
		line-height: 1;
	}

	/* Scroll + column ------------------------------------------------------ */
	.th-scroll {
		flex: 1;
		overflow-y: auto;
		scroll-behavior: smooth;
	}

	.th-scroll::-webkit-scrollbar {
		width: 8px;
	}
	.th-scroll::-webkit-scrollbar-thumb {
		background: var(--color-bot-border);
		border-radius: 4px;
	}
	.th-scroll::-webkit-scrollbar-thumb:hover {
		background: var(--color-ink-muted);
	}

	.th-column {
		max-width: 960px;
		margin: 0 auto;
		padding: 1.25rem 1.5rem 2.5rem 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.has-turns .th-column {
		padding-top: 1.5rem;
	}

	/* Hero (idle state) ---------------------------------------------------- */
	.hero-grid {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 2.5rem;
		padding: 2.5rem 0 2rem 0;
		align-items: center;
		animation: fadeUp 0.5s ease-out;
	}

	.hero-left {
		min-width: 0;
		position: relative;
	}

	.hero-left::before {
		content: '';
		position: absolute;
		left: -1.25rem;
		top: 0.25rem;
		bottom: 0.25rem;
		width: 1px;
		background: linear-gradient(
			180deg,
			transparent,
			var(--color-accent) 30%,
			var(--color-accent) 70%,
			transparent
		);
		opacity: 0.4;
	}

	.hero-right {
		min-width: 0;
	}

	@media (max-width: 880px) {
		.hero-grid {
			grid-template-columns: 1fr;
			gap: 1.5rem;
			padding: 1.5rem 0 1rem 0;
		}
		.hero-left::before {
			display: none;
		}
	}

	.hero-super-title {
		display: inline-flex;
		align-items: center;
		gap: 0.6rem;
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-accent);
		margin-bottom: 1.1rem;
	}

	.ov-dot {
		width: 4px;
		height: 4px;
		border-radius: 50%;
		background: currentColor;
		opacity: 0.7;
	}

	.hero-title {
		font-family: var(--font-display);
		font-size: clamp(2rem, 3.2vw, 2.8rem);
		line-height: 1.05;
		color: var(--color-ink);
		margin: 0 0 0.85rem 0;
		letter-spacing: -0.015em;
		font-weight: 400;
	}

	.hero-title em {
		font-style: italic;
		color: var(--color-primary);
	}

	.hero-title .drop {
		color: var(--color-accent);
		font-style: italic;
		font-size: 1.15em;
		display: inline-block;
		transform: translateY(0.06em);
	}

	.hero-title .drop.closing {
		transform: translateY(0.06em);
		display: inline-block;
	}

	.hero-arc {
		display: block;
		width: 220px;
		height: 38px;
		color: var(--color-accent);
		margin: 0.3rem 0 1.25rem 0;
	}

	.hero-kicker {
		font-family: var(--font-display);
		font-size: 1.1rem;
		line-height: 1.65;
		color: var(--color-ink-light);
		font-style: italic;
		max-width: 580px;
		margin: 0 0 1.85rem 0;
	}

	.hero-kicker em {
		color: var(--color-primary);
		font-style: italic;
	}

	.hero-cta-row {
		display: flex;
		align-items: center;
		gap: 1.5rem;
		flex-wrap: wrap;
	}

	.hero-cta {
		display: inline-flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.75rem 1.35rem;
		background: var(--color-surface-card);
		color: var(--color-ink);
		border: 1px solid var(--color-bot-border);
		border-radius: 999px;
		font-family: var(--font-body);
		font-size: 0.88rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.hero-cta:hover {
		background: var(--color-primary);
		color: var(--color-user-text);
		border-color: var(--color-primary);
		transform: translateY(-2px);
		box-shadow: 0 10px 28px -12px rgba(59, 76, 192, 0.55);
	}

	.cta-glyph {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-accent);
		font-size: 1rem;
		line-height: 1;
	}

	.cta-arrow {
		font-family: var(--font-display);
		transition: transform 0.25s ease-in-out;
	}

	.hero-cta:hover .cta-arrow {
		transform: translateX(3px);
	}

	.hero-avatar {
		opacity: 0.85;
	}

	/* Turns ---------------------------------------------------------------- */
	.turn {
		animation: fadeUp 0.3s ease-out;
	}

	.user-turn {
		display: flex;
		justify-content: flex-end;
	}

	.user-bubble {
		max-width: 78%;
		background: linear-gradient(
			180deg,
			var(--color-primary),
			color-mix(in srgb, var(--color-primary) 88%, var(--color-ink) 12%)
		);
		color: white;
		padding: 0.75rem 1.05rem 0.8rem 1.05rem;
		border-radius: 16px 16px 4px 16px;
		box-shadow:
			0 1px 0 rgba(26, 26, 46, 0.04),
			0 12px 24px -16px rgba(59, 76, 192, 0.45);
	}

	.user-bubble.subtle {
		background: var(--color-surface-card);
		color: var(--color-ink);
		border: 1px solid var(--color-bot-border);
	}

	.user-meta {
		display: flex;
		justify-content: space-between;
		gap: 0.8rem;
		font-family: var(--font-mono);
		font-size: 0.55rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		opacity: 0.85;
		margin-bottom: 0.3rem;
	}

	.user-text {
		margin: 0;
		font-family: var(--font-body);
		font-size: 0.95rem;
		line-height: 1.5;
		word-break: break-word;
	}

	.user-bubble.subtle .user-text strong {
		font-weight: 600;
		color: var(--color-primary);
	}

	.bot-turn {
		display: grid;
		grid-template-columns: 56px 1fr;
		gap: 1rem;
		align-items: flex-start;
	}

	.bot-marginalia {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.4rem;
		padding-top: 0.3rem;
	}

	.margin-line {
		width: 1px;
		flex: 1;
		min-height: 30px;
		background: linear-gradient(
			180deg,
			var(--color-accent),
			transparent 80%
		);
		opacity: 0.5;
	}

	.bot-body {
		min-width: 0;
	}

	.typing {
		display: inline-flex;
		gap: 6px;
		padding: 0.85rem 1.1rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 14px 14px 14px 4px;
		width: fit-content;
	}

	.typing span {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: var(--color-ink-muted);
		animation: bounce 1.2s infinite ease-in-out both;
	}

	.typing span:nth-child(2) {
		animation-delay: 0.15s;
	}
	.typing span:nth-child(3) {
		animation-delay: 0.3s;
	}

	/* Error ---------------------------------------------------------------- */
	.error-banner {
		display: grid;
		grid-template-columns: 36px 1fr;
		gap: 0.85rem;
		padding: 0.85rem 1rem 0.95rem 0.85rem;
		background: rgba(212, 72, 72, 0.06);
		border-left: 3px solid var(--color-error);
		border-radius: 0 8px 8px 0;
		align-items: center;
	}

	.error-glyph {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		border: 1px solid var(--color-error);
		color: var(--color-error);
		font-family: var(--font-display);
		font-weight: 700;
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}

	.error-label {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-error);
		margin-bottom: 0.1rem;
	}

	.error-msg {
		font-size: 0.85rem;
		color: var(--color-ink);
	}

	/* Composer (bottom block) --------------------------------------------- */
	.composer {
		background: var(--color-surface, transparent);
		border-top: 1px solid var(--color-bot-border);
		padding: 1rem 1.5rem 1.1rem 1.5rem;
	}

	.composer-inner {
		max-width: 960px;
		margin: 0 auto;
		position: relative;
	}

	.composer-rule {
		height: 1px;
		background: linear-gradient(
			to right,
			transparent,
			var(--color-accent),
			transparent
		);
		opacity: 0.4;
		margin-bottom: 0.75rem;
	}

	.composer-hint {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		font-family: var(--font-display);
		font-style: italic;
		font-size: 0.75rem;
		color: var(--color-ink-muted);
		margin: 0.55rem 0 0 0;
	}

	.key {
		font-family: var(--font-mono);
		font-style: normal;
		font-size: 0.65rem;
		padding: 0.1rem 0.4rem;
		border: 1px solid var(--color-bot-border);
		border-radius: 4px;
		background: var(--color-surface-card);
		color: var(--color-ink);
	}

	.hint-link {
		background: transparent;
		border: none;
		padding: 0;
		font: inherit;
		color: var(--color-primary);
		cursor: pointer;
		text-decoration: underline;
		text-decoration-style: dotted;
		text-underline-offset: 3px;
	}

	.hint-link:hover {
		color: var(--color-accent);
	}

	/* Drawer --------------------------------------------------------------- */
	.drawer-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(26, 26, 46, 0.4);
		backdrop-filter: blur(2px);
		-webkit-backdrop-filter: blur(2px);
		z-index: 50;
		animation: fadeIn 0.2s ease-out;
		border: none;
		cursor: pointer;
	}

	.drawer {
		position: fixed;
		top: 0;
		right: 0;
		bottom: 0;
		width: min(400px, 92vw);
		background: var(--color-surface-card);
		border-left: 1px solid var(--color-bot-border);
		box-shadow: -24px 0 60px -32px rgba(26, 26, 46, 0.35);
		z-index: 51;
		transform: translateX(100%);
		transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1), background-color 0.25s ease-in-out, border-color 0.25s ease-in-out, box-shadow 0.25s ease-in-out;
		display: flex;
		flex-direction: column;
	}

	.drawer.open {
		transform: translateX(0);
	}

	.drawer-head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		padding: 1.5rem 1.5rem 1rem 1.5rem;
		border-bottom: 1px dashed var(--color-bot-border);
	}

	.drawer-super-title {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-accent);
		margin-bottom: 0.25rem;
	}

	.drawer-title {
		font-family: var(--font-display);
		font-size: 1.75rem;
		color: var(--color-ink);
		margin: 0;
		line-height: 1;
	}

	.drawer-close {
		font-family: var(--font-display);
		font-size: 1.8rem;
		line-height: 1;
		background: transparent;
		border: 1px solid var(--color-bot-border);
		color: var(--color-ink-muted);
		width: 36px;
		height: 36px;
		border-radius: 50%;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0;
	}

	.drawer-close:hover {
		color: var(--color-error);
		border-color: var(--color-error);
	}

	.drawer-body {
		flex: 1;
		overflow-y: auto;
		padding: 1.25rem 1.5rem 2rem 1.5rem;
	}

	/* Animations ----------------------------------------------------------- */
	@keyframes fadeUp {
		from {
			opacity: 0;
			transform: translateY(8px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
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

	@keyframes bounce {
		0%, 80%, 100% {
			transform: scale(0.6);
			opacity: 0.4;
		}
		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	@keyframes pulse {
		0%, 100% {
			transform: scale(1);
			opacity: 1;
		}
		50% {
			transform: scale(1.4);
			opacity: 0.45;
		}
	}

	/* Responsive ----------------------------------------------------------- */
	@media (max-width: 700px) {
		.hero {
			grid-template-columns: 32px 1fr;
			gap: 0.85rem;
			padding-top: 2rem;
		}
		.bot-turn {
			grid-template-columns: 36px 1fr;
			gap: 0.55rem;
		}
		.user-bubble {
			max-width: 88%;
		}
		.th-column {
			padding: 1.25rem 1rem 2rem 1rem;
		}
		.composer {
			padding: 0.8rem 1rem 0.95rem 1rem;
		}
		.th-header {
			padding: 0.75rem 1rem;
		}
		.th-header-inner {
			gap: 0.5rem;
		}
		.th-btn {
			padding: 0.4rem 0.75rem;
			font-size: 0.72rem;
		}
	}
</style>
