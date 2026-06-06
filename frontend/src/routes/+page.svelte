<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isDarkMode, toggleDarkMode } from '$lib/stores/theme';
	import { reveal } from '$lib/actions/reveal';
	import { checkAuth } from '$lib/api/auth';

	// Con sesión activa redirigimos al chat; si no, se queda en la landing.
	let authed = $state(false);

	const modes = [
		{
			glyph: '∞',
			kicker: 'Chat con IA',
			title: 'Conversá en lenguaje natural',
			body: 'Preguntale a Slacko teoría, pegale un enunciado o pedile que razone un modelo. Busca en la wiki curada y, cuando hace falta, resuelve.'
		},
		{
			glyph: '1→',
			kicker: 'Paso a paso',
			title: 'Armá el modelo desde cero',
			body: 'Te guía variable por variable, restricción por restricción, hasta la forma estándar — sin saltearse ningún razonamiento.'
		},
		{
			glyph: '§',
			kicker: 'Teoría',
			title: 'Conceptos clave, bien explicados',
			body: 'Definiciones, formas canónicas, casos especiales. Una wiki estilo apunte, con ejemplos y sin paja.'
		},
		{
			glyph: '✦',
			kicker: 'Tutorial',
			title: 'Un ejemplo resuelto con vos',
			body: 'Recorré un problema completo, del enunciado al gráfico y la interpretación, a tu ritmo.'
		}
	];

	let canvas: HTMLCanvasElement;
	let plotEl: HTMLElement;

	onMount(() => {
		// Si ya hay sesión, mandamos directo al chat; si no, queda la landing.
		checkAuth().then((ok) => {
			if (ok) goto('/chat');
			else authed = false;
		});

		const ctx2d = canvas.getContext('2d');
		if (!ctx2d) return;
		const ctx = ctx2d; // tipo no-nulo, estable dentro de los closures
		const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

		type Dot = { hx: number; hy: number; x: number; y: number; vx: number; vy: number };
		let dpr = Math.min(window.devicePixelRatio || 1, 2);
		let W = 0, H = 0;
		let dots: Dot[] = [];

		const SPACING = 40;   // separación de la grilla en reposo
		const R = 150;        // radio de influencia del mouse
		const ATTRACT = 0.95; // fuerza de agrupamiento hacia el mouse
		const SPRING = 0.022; // fuerza de retorno al reposo
		const DAMP = 0.87;    // amortiguación

		const mouse = { x: -9999, y: -9999, active: false };
		let baseColor = '#8888a4';
		let activeColor = '#d4a853';

		// Zona del gráfico: ahí no se dibujan puntos ni reacciona el mouse.
		let dead = { x: 0, y: 0, w: 0, h: 0 };
		const inDead = (x: number, y: number) =>
			dead.w > 0 && x >= dead.x && x <= dead.x + dead.w && y >= dead.y && y <= dead.y + dead.h;
		function computeDead() {
			if (!plotEl) { dead = { x: 0, y: 0, w: 0, h: 0 }; return; }
			const cr = canvas.getBoundingClientRect();
			const pr = plotEl.getBoundingClientRect();
			const pad = 16;
			dead = {
				x: pr.left - cr.left - pad,
				y: pr.top - cr.top - pad,
				w: pr.width + pad * 2,
				h: pr.height + pad * 2
			};
		}

		function readColors() {
			const cs = getComputedStyle(document.documentElement);
			baseColor = cs.getPropertyValue('--color-ink-muted').trim() || baseColor;
			activeColor = cs.getPropertyValue('--color-accent').trim() || activeColor;
		}

		function build() {
			const rect = canvas.getBoundingClientRect();
			W = rect.width; H = rect.height;
			canvas.width = Math.round(W * dpr);
			canvas.height = Math.round(H * dpr);
			ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
			dots = [];
			const cols = Math.ceil(W / SPACING) + 2;
			const rows = Math.ceil(H / SPACING) + 2;
			for (let r = 0; r < rows; r++) {
				for (let c = 0; c < cols; c++) {
					const hx = c * SPACING + (r % 2 ? SPACING / 2 : 0) - SPACING / 2;
					const hy = r * SPACING - SPACING / 2;
					dots.push({ hx, hy, x: hx, y: hy, vx: 0, vy: 0 });
				}
			}
			computeDead();
		}

		function paintStatic() {
			ctx.clearRect(0, 0, W, H);
			for (const d of dots) {
				if (inDead(d.hx, d.hy)) continue;
				ctx.beginPath();
				ctx.arc(d.x, d.y, 1.4, 0, Math.PI * 2);
				ctx.fillStyle = baseColor;
				ctx.globalAlpha = 0.38;
				ctx.fill();
			}
			ctx.globalAlpha = 1;
		}

		let raf = 0;
		function frame() {
			ctx.clearRect(0, 0, W, H);
			for (const d of dots) {
				if (inDead(d.hx, d.hy)) continue;
				let ax = (d.hx - d.x) * SPRING;
				let ay = (d.hy - d.y) * SPRING;
				let act = 0;
				if (mouse.active) {
					const dx = mouse.x - d.x;
					const dy = mouse.y - d.y;
					const dist = Math.hypot(dx, dy);
					if (dist < R && dist > 0.01) {
						const f = ((R - dist) / R) * ATTRACT;
						ax += (dx / dist) * f;
						ay += (dy / dist) * f;
						act = (R - dist) / R;
					}
				}
				d.vx = (d.vx + ax) * DAMP;
				d.vy = (d.vy + ay) * DAMP;
				d.x += d.vx;
				d.y += d.vy;

				ctx.beginPath();
				ctx.arc(d.x, d.y, 1.4 + act * 2.3, 0, Math.PI * 2);
				ctx.fillStyle = act > 0.18 ? activeColor : baseColor;
				ctx.globalAlpha = 0.34 + act * 0.62;
				ctx.fill();
			}
			ctx.globalAlpha = 1;
			raf = requestAnimationFrame(frame);
		}

		const onMove = (e: PointerEvent) => {
			// Coordenadas relativas al canvas (que ahora cubre solo el bloque superior).
			const rect = canvas.getBoundingClientRect();
			const x = e.clientX - rect.left;
			const y = e.clientY - rect.top;
			if (x >= -30 && x <= W + 30 && y >= -30 && y <= H + 30 && !inDead(x, y)) {
				mouse.x = x;
				mouse.y = y;
				mouse.active = true;
			} else {
				mouse.active = false;
			}
		};
		const onLeave = () => { mouse.active = false; };

		readColors();
		build();
		if (reduce) {
			paintStatic();
		} else {
			raf = requestAnimationFrame(frame);
			window.addEventListener('pointermove', onMove, { passive: true });
			window.addEventListener('pointerout', onLeave);
			window.addEventListener('blur', onLeave);
		}
		const ro = new ResizeObserver(() => {
			dpr = Math.min(window.devicePixelRatio || 1, 2);
			build();
			if (reduce) paintStatic();
		});
		ro.observe(canvas);
		const unsub = isDarkMode.subscribe(() => { readColors(); if (reduce) paintStatic(); });

		return () => {
			cancelAnimationFrame(raf);
			window.removeEventListener('pointermove', onMove);
			window.removeEventListener('pointerout', onLeave);
			window.removeEventListener('blur', onLeave);
			ro.disconnect();
			unsub();
		};
	});
</script>

<svelte:head><title>Slacko · Tutor de Programación Lineal</title></svelte:head>

<div class="page">
	<!-- Bloque superior: solo acá vive el campo de puntos interactivo -->
	<div class="top">
		<canvas bind:this={canvas} class="dotfield" aria-hidden="true"></canvas>

	<!-- ── Nav ── -->
	<header class="nav">
		<a href="/" class="brand">Slacko</a>
		<nav class="nav-right">
			<button class="theme" onclick={toggleDarkMode} aria-label="Cambiar tema">
				{#if $isDarkMode}☀{:else}☾{/if}
			</button>
			{#if authed}
				<a href="/chat" class="btn-pill">Ir a Slacko <span>→</span></a>
			{:else}
				<a href="/login" class="link">Iniciar sesión</a>
				<a href="/register" class="btn-pill">Empezá <span>→</span></a>
			{/if}
		</nav>
	</header>

	<!-- ── Hero ── -->
	<section class="hero">
		<div class="hero-copy">
			<p class="eyebrow reveal" style="--d: 40ms">INVESTIGACIÓN OPERATIVA · UTN</p>
			<h1 class="display">
				<span class="reveal line" style="--d: 120ms">Programación Lineal,</span>
				<span class="reveal line" style="--d: 240ms">explicada como si</span>
				<span class="reveal line" style="--d: 360ms">tuvieras un <em>tutor</em></span>
				<span class="reveal line" style="--d: 480ms">al lado.</span>
			</h1>
			<p class="lede reveal" style="--d: 640ms">
				Slacko formula, resuelve gráficamente e interpreta problemas de PL de dos variables.
				Charlás, te guía paso a paso, repasás teoría — y ve el método como lo ves vos.
			</p>
			<div class="cta-row reveal" style="--d: 780ms">
				{#if authed}
					<a href="/chat" class="btn-grad">Ir a Slacko <span>→</span></a>
				{:else}
					<a href="/register" class="btn-grad">Probar gratis <span>→</span></a>
					<a href="/login" class="btn-ghost">Ya tengo cuenta</a>
				{/if}
			</div>
			<p class="micro reveal" style="--d: 900ms">
				{#if authed}Tenés una sesión activa — seguí donde lo dejaste.{:else}Sin tarjeta · Entrá con tu correo o con Google{/if}
			</p>
		</div>

		<!-- Pieza central: región factible + objetivo que barre paralela -->
		<figure class="plot" bind:this={plotEl} aria-label="Método gráfico: la recta objetivo barre paralela hasta el vértice óptimo">
			<svg viewBox="0 0 400 320" role="img">
				<defs>
					<clipPath id="plotclip"><rect x="52" y="32" width="322" height="240" /></clipPath>
				</defs>

				<!-- grilla suave -->
				<g class="grid">
					{#each [90, 130, 170, 210, 250] as gy}
						<line x1="52" y1={gy} x2="372" y2={gy} />
					{/each}
					{#each [100, 150, 200, 250, 300] as gx}
						<line x1={gx} y1="40" x2={gx} y2="272" />
					{/each}
				</g>

				<!-- región factible -->
				<polygon class="region" points="52,272 52,150 150,78 262,128 300,272" />

				<!-- familia de rectas de nivel (paralelas, pendiente negativa) + objetivo
				     animado: en translate(0,0) la recta pasa por el óptimo (262,128) -->
				<g clip-path="url(#plotclip)">
					<line class="lvl" x1="-23" y1="-12" x2="349" y2="237" />
					<line class="lvl" x1="-46" y1="23" x2="326" y2="272" />
					<line class="lvl" x1="-69" y1="58" x2="303" y2="307" />
					<line class="obj" x1="0" y1="-47" x2="372" y2="202" />
				</g>

				<!-- ejes -->
				<line class="axis" x1="52" y1="272" x2="372" y2="272" />
				<line class="axis" x1="52" y1="272" x2="52" y2="34" />
				<text class="axislabel" x="366" y="290">x₁</text>
				<text class="axislabel" x="36" y="44">x₂</text>

				<!-- aristas (restricciones) que se dibujan -->
				<polyline class="edge e1" points="52,150 150,78" />
				<polyline class="edge e2" points="150,78 262,128" />
				<polyline class="edge e3" points="262,128 300,272" />

				<!-- vértices -->
				<circle class="vtx v1" cx="52" cy="150" r="4.5" />
				<circle class="vtx v2" cx="150" cy="78" r="4.5" />
				<circle class="vtx v3" cx="300" cy="272" r="4.5" />
				<!-- óptimo: vértice de la derecha, máximo de Z -->
				<circle class="opt-halo" cx="262" cy="128" r="13" />
				<circle class="opt" cx="262" cy="128" r="5.5" />
				<text class="opt-label" x="270" y="120">óptimo</text>
			</svg>
			<figcaption>
				<span class="zexpr">máx Z = 2x₁ + 3x₂</span>
				<span class="zval">óptimo en (5, 4)</span>
			</figcaption>
		</figure>
	</section>
	</div>
	<!-- /.top -->

	<!-- ── Tira de credibilidad ── -->
	<div class="strip reveal" use:reveal>
		<span>Solver propio en NumPy/SciPy</span><i>·</i>
		<span>Gráficos interactivos</span><i>·</i>
		<span>Wiki curada de 32 conceptos</span><i>·</i>
		<span>Multi-modelo con fallback</span>
	</div>

	<!-- ── Modos ── -->
	<section class="modes">
		<header class="section-head reveal" use:reveal>
			<p class="eyebrow">CUATRO MANERAS DE TRABAJAR</p>
			<h2 class="display sm">Elegí cómo querés que te acompañe.</h2>
		</header>
		<div class="mode-grid">
			{#each modes as m, i}
				<article class="mode reveal" use:reveal style="--d: {i * 90}ms">
					<div class="mode-glyph">{m.glyph}</div>
					<p class="mode-kicker">{m.kicker}</p>
					<h3 class="mode-title">{m.title}</h3>
					<p class="mode-body">{m.body}</p>
				</article>
			{/each}
		</div>
	</section>

	<!-- ── Cierre ── -->
	<section class="closer reveal" use:reveal>
		<h2 class="display">¿Arrancamos?</h2>
		<p class="lede">Creá tu cuenta y resolvé tu primer problema en minutos.</p>
		<a href={authed ? '/chat' : '/register'} class="btn-grad lg">Entrar a Slacko <span>→</span></a>
	</section>

	<footer class="foot">
		<span>Slacko · Equipo SLAKING</span>
		<span>Investigación Operativa — UTN · 2026</span>
	</footer>
</div>

<style>
	.top { position: relative; }
	.dotfield {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		z-index: 0;
		pointer-events: none;
		display: block;
		/* el campo se disipa de a poco hacia abajo (sin corte abrupto) */
		-webkit-mask-image: linear-gradient(to bottom, #000 55%, transparent 100%);
		mask-image: linear-gradient(to bottom, #000 55%, transparent 100%);
	}
	.page {
		position: relative;
		min-height: 100vh;
		overflow-x: clip;
		color: var(--color-ink);
		font-family: var(--font-body);
		background: var(--color-surface);
	}

	/* ── Nav ── */
	.nav {
		position: relative;
		z-index: 2;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.4rem clamp(1.2rem, 5vw, 4rem);
		max-width: 1180px;
		margin: 0 auto;
	}
	.brand {
		font-family: var(--font-display);
		font-size: 1.9rem;
		color: var(--color-ink);
		text-decoration: none;
		letter-spacing: -0.01em;
	}
	.nav-right { display: flex; align-items: center; gap: 1.1rem; }
	.theme {
		width: 38px; height: 38px; border-radius: 0.6rem;
		border: 1px solid var(--color-bot-border); background: var(--color-surface-card);
		color: var(--color-ink-muted); cursor: pointer; font-size: 1rem;
		transition: color 0.2s, border-color 0.2s, transform 0.2s;
	}
	.theme:hover { color: var(--color-ink); border-color: var(--color-ink); transform: scale(1.05); }
	.link { color: var(--color-ink-light); text-decoration: none; font-size: 0.92rem; font-weight: 500; }
	.link:hover { color: var(--color-primary); }
	.btn-pill {
		display: inline-flex; gap: 0.4rem; align-items: center;
		padding: 0.5rem 1.05rem; border-radius: 999px;
		background: var(--color-ink); color: var(--color-surface);
		text-decoration: none; font-weight: 600; font-size: 0.9rem;
		transition: transform 0.18s, box-shadow 0.18s;
	}
	.btn-pill:hover { transform: translateY(-1px); box-shadow: 0 10px 22px -12px var(--color-ink); }
	.btn-pill span { transition: transform 0.18s; }
	.btn-pill:hover span { transform: translateX(3px); }

	/* ── Hero ── */
	.hero {
		position: relative;
		z-index: 1;
		max-width: 1180px;
		margin: 0 auto;
		padding: clamp(2rem, 6vw, 4.5rem) clamp(1.2rem, 5vw, 4rem) 2rem;
		display: grid;
		grid-template-columns: 1.05fr 0.95fr;
		gap: clamp(1.5rem, 4vw, 3.5rem);
		align-items: center;
	}
	.eyebrow {
		font-family: var(--font-mono); font-size: 0.66rem; letter-spacing: 0.26em;
		text-transform: uppercase; color: var(--color-primary); margin-bottom: 1.1rem;
	}
	:global(.dark) .eyebrow { color: var(--color-accent); }
	.display {
		font-family: var(--font-display); font-weight: 400;
		font-size: clamp(2.6rem, 6vw, 4.3rem); line-height: 1.02;
		letter-spacing: -0.015em; margin: 0;
	}
	.display.sm { font-size: clamp(2rem, 4vw, 3rem); }
	.display em {
		font-style: italic;
		background: linear-gradient(100deg, var(--color-primary), var(--color-accent));
		-webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
	}
	.display .line { display: block; }
	.lede { margin-top: 1.5rem; max-width: 30rem; font-size: 1.08rem; line-height: 1.55; color: var(--color-ink-light); }
	.cta-row { margin-top: 1.8rem; display: flex; gap: 0.9rem; flex-wrap: wrap; }
	.btn-grad {
		display: inline-flex; gap: 0.5rem; align-items: center;
		padding: 0.8rem 1.4rem; border-radius: 0.8rem; color: #fff; text-decoration: none; font-weight: 600;
		background: linear-gradient(110deg, var(--color-primary), var(--color-accent));
		box-shadow: 0 12px 26px -14px color-mix(in srgb, var(--color-primary) 70%, transparent);
		transition: transform 0.18s, filter 0.18s, box-shadow 0.18s;
	}
	.btn-grad.lg { padding: 1rem 1.8rem; font-size: 1.05rem; margin-top: 1.6rem; }
	.btn-grad span { transition: transform 0.18s; }
	.btn-grad:hover { transform: translateY(-2px); filter: brightness(1.05); }
	.btn-grad:hover span { transform: translateX(4px); }
	.btn-ghost {
		display: inline-flex; align-items: center; padding: 0.8rem 1.3rem; border-radius: 0.8rem;
		border: 1px solid var(--color-bot-border); color: var(--color-ink); text-decoration: none; font-weight: 500;
		background: var(--color-surface-card); transition: border-color 0.18s, transform 0.18s;
	}
	.btn-ghost:hover { border-color: var(--color-ink); transform: translateY(-2px); }
	.micro { margin-top: 1rem; font-size: 0.8rem; color: var(--color-ink-muted); }

	/* ── Plot ── */
	.plot { margin: 0; }
	.plot svg {
		width: 100%; height: auto; overflow: visible;
		filter: drop-shadow(0 24px 40px color-mix(in srgb, var(--color-primary) 16%, transparent));
	}
	.grid line { stroke: var(--color-ink); opacity: 0.06; stroke-width: 1; }
	.axis { stroke: var(--color-ink-light); stroke-width: 1.6; opacity: 0; animation: fade 0.6s ease forwards 0.2s; }
	.axislabel { fill: var(--color-ink-muted); font-family: var(--font-mono); font-size: 12px; opacity: 0; animation: fade 0.6s ease forwards 0.5s; }
	.region {
		fill: color-mix(in srgb, var(--color-primary) 16%, transparent);
		stroke: color-mix(in srgb, var(--color-primary) 50%, transparent);
		stroke-width: 1.4; opacity: 0; transform-origin: 52px 272px;
		animation: region-in 0.9s cubic-bezier(0.22, 1, 0.36, 1) forwards 0.7s;
	}
	.edge {
		fill: none; stroke: var(--color-primary); stroke-width: 2.6; stroke-linecap: round;
		stroke-dasharray: 240; stroke-dashoffset: 240; animation: draw 0.8s ease forwards;
	}
	.e1 { animation-delay: 0.9s; }
	.e2 { animation-delay: 1.25s; }
	.e3 { animation-delay: 1.6s; }

	/* familia de niveles (pendiente negativa) — tenues y fijas */
	.lvl {
		stroke: var(--color-accent); stroke-width: 1.3; stroke-dasharray: 5 6;
		opacity: 0; animation: fade-faint 0.6s ease forwards 1.9s;
	}
	/* recta objetivo: misma pendiente, barre paralela hacia el óptimo */
	.obj {
		stroke: var(--color-accent); stroke-width: 2.6; stroke-linecap: round;
		opacity: 0; animation: obj-appear 0.5s ease forwards 1.9s, obj-sweep 4.2s cubic-bezier(0.45, 0, 0.55, 1) infinite 2.1s;
	}
	.vtx { fill: var(--color-surface-card); stroke: var(--color-primary); stroke-width: 2.4; opacity: 0; animation: pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
	.v1 { animation-delay: 1.1s; }
	.v2 { animation-delay: 1.5s; }
	.v3 { animation-delay: 1.8s; }
	.opt { fill: var(--color-accent); opacity: 0; animation: pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards 2.1s; }
	.opt-halo { fill: var(--color-accent); opacity: 0; transform-origin: 262px 128px; animation: halo 4.2s ease-out infinite 4.3s; }
	.opt-label { fill: var(--color-accent); font-family: var(--font-mono); font-size: 11px; font-weight: 500; opacity: 0; animation: fade 0.5s ease forwards 2.5s; }
	figcaption { display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.8rem; padding: 0 0.5rem; }
	.zexpr { font-family: var(--font-mono); font-size: 0.92rem; color: var(--color-ink); }
	.zval { font-family: var(--font-mono); font-size: 0.78rem; color: var(--color-accent); }

	@keyframes draw { to { stroke-dashoffset: 0; } }
	@keyframes fade { to { opacity: 1; } }
	@keyframes fade-faint { to { opacity: 0.32; } }
	@keyframes obj-appear { to { opacity: 0.95; } }
	@keyframes region-in { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
	@keyframes pop { from { opacity: 0; transform: scale(0); } to { opacity: 1; transform: scale(1); } }
	@keyframes halo { 0% { opacity: 0.5; transform: scale(0.6); } 60%, 100% { opacity: 0; transform: scale(1.9); } }
	/* La recta arranca cerca del origen (Z bajo) y barre, en perpendicular a su
	   pendiente, hasta pasar por el óptimo (translate 0,0) — siempre paralela. */
	@keyframes obj-sweep {
		0% { transform: translate(-58px, 88px); }
		45%, 60% { transform: translate(0, 0); }
		100% { transform: translate(-58px, 88px); }
	}

	/* ── Strip ── */
	.strip {
		position: relative; z-index: 1; max-width: 1180px; margin: 1.5rem auto 0;
		padding: 1rem clamp(1.2rem, 5vw, 4rem); display: flex; flex-wrap: wrap;
		gap: 0.4rem 0.9rem; align-items: center; font-family: var(--font-mono);
		font-size: 0.74rem; letter-spacing: 0.04em; color: var(--color-ink-muted);
		border-top: 1px solid var(--color-bot-border); border-bottom: 1px solid var(--color-bot-border);
	}
	.strip i { color: var(--color-accent); font-style: normal; }

	/* ── Modos ── */
	.modes { position: relative; z-index: 1; max-width: 1180px; margin: 0 auto; padding: clamp(3.5rem, 8vw, 6rem) clamp(1.2rem, 5vw, 4rem); }
	.section-head { margin-bottom: 2.5rem; }
	.section-head .eyebrow { margin-bottom: 0.7rem; }
	.mode-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.1rem; }
	.mode {
		position: relative; padding: 1.6rem 1.7rem 1.8rem; border-radius: 1rem;
		background: var(--color-surface-card); border: 1px solid var(--color-bot-border);
		transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s; overflow: hidden;
	}
	.mode::before {
		content: ''; position: absolute; inset: 0 0 auto 0; height: 3px;
		background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
		transform: scaleX(0); transform-origin: left; transition: transform 0.35s ease;
	}
	.mode:hover { transform: translateY(-4px); box-shadow: 0 22px 44px -28px color-mix(in srgb, var(--color-primary) 50%, transparent); border-color: transparent; }
	.mode:hover::before { transform: scaleX(1); }
	.mode-glyph {
		font-family: var(--font-display); font-style: italic; font-size: 1.7rem;
		width: 46px; height: 46px; display: grid; place-items: center; border-radius: 0.7rem;
		background: linear-gradient(135deg, color-mix(in srgb, var(--color-primary) 12%, transparent), color-mix(in srgb, var(--color-accent) 12%, transparent));
		color: var(--color-primary); margin-bottom: 1rem;
	}
	.mode-kicker { font-family: var(--font-mono); font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--color-accent); margin-bottom: 0.5rem; }
	.mode-title { font-size: 1.18rem; font-weight: 600; margin: 0 0 0.5rem; color: var(--color-ink); }
	.mode-body { font-size: 0.92rem; line-height: 1.55; color: var(--color-ink-light); margin: 0; }

	/* ── Closer ── */
	.closer { position: relative; z-index: 1; text-align: center; max-width: 720px; margin: 0 auto; padding: clamp(2rem, 6vw, 4rem) 1.5rem clamp(3rem, 8vw, 5rem); }
	.closer .lede { margin: 1rem auto 0; }

	.foot {
		position: relative; z-index: 1; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;
		max-width: 1180px; margin: 0 auto; padding: 1.6rem clamp(1.2rem, 5vw, 4rem);
		border-top: 1px solid var(--color-bot-border); font-family: var(--font-mono); font-size: 0.72rem; color: var(--color-ink-muted);
	}

	/* ── Reveal ── */
	.reveal { opacity: 0; transform: translateY(18px); transition: opacity 0.7s cubic-bezier(0.22, 1, 0.36, 1), transform 0.7s cubic-bezier(0.22, 1, 0.36, 1); transition-delay: var(--d, 0ms); }
	.reveal.is-visible, :global(.is-visible).reveal { opacity: 1; transform: none; }
	.hero .reveal { animation: rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards; animation-delay: var(--d, 0ms); }
	@keyframes rise { to { opacity: 1; transform: none; } }

	@media (max-width: 860px) {
		.hero { grid-template-columns: 1fr; }
		.plot { max-width: 460px; margin-top: 1rem; }
		.mode-grid { grid-template-columns: 1fr; }
	}
	@media (prefers-reduced-motion: reduce) {
		.reveal, .hero .reveal { opacity: 1; transform: none; animation: none; transition: none; }
		.edge, .obj, .lvl, .vtx, .opt, .opt-halo, .region, .axis, .axislabel { animation: none; opacity: 1; stroke-dashoffset: 0; }
		.obj { opacity: 0.95; }
		.lvl { opacity: 0.32; }
	}
</style>
