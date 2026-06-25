<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { isDarkMode } from '$lib/stores/theme';

	export interface PlotPayload {
		vertices?: Array<[number, number]>;
		feasible_vertices?: Array<[number, number]>;
		optimal_point?: [number, number] | null;
		optimal_value?: number | null;
		constraints?: Array<{
			label?: string;
			coefficients?: [number, number];
			sign?: string;
			rhs?: number;
		}>;
	}

	let {
		payload
	}: {
		payload: PlotPayload;
	} = $props();

	let graphContainer = $state<HTMLDivElement | null>(null);

	function fmt(n: number): string {
		return Number.isInteger(n) ? n.toString() : n.toFixed(2).replace(/\.?0+$/, '');
	}

	function sortPolygonVertices(vertices: Array<[number, number]>): Array<[number, number]> {
		const cx = vertices.reduce((s, p) => s + p[0], 0) / vertices.length;
		const cy = vertices.reduce((s, p) => s + p[1], 0) / vertices.length;
		return [...vertices].sort(
			(a, b) => Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx)
		);
	}

	function toPoint(raw: unknown): [number, number] | null {
		if (Array.isArray(raw) && raw.length >= 2) {
			return [Number(raw[0]), Number(raw[1])];
		}
		if (raw && typeof raw === 'object') {
			const obj = raw as Record<string, unknown>;
			const x1 = Number(obj.x1);
			const x2 = Number(obj.x2);
			if (!Number.isNaN(x1) && !Number.isNaN(x2)) return [x1, x2];
		}
		return null;
	}

	async function renderGraph() {
		if (!graphContainer) return;
		const Plotly = await import('plotly.js-dist-min');
		const traces: any[] = [];

		const allVerts = (payload.vertices ?? []).map(toPoint).filter((p): p is [number, number] => p !== null);
		const feasibleVerts = (payload.feasible_vertices ?? [])
			.map(toPoint)
			.filter((p): p is [number, number] => p !== null);
		const optimalPoint = toPoint(payload.optimal_point);
		const constraints = payload.constraints ?? [];

		const visiblePoints = [...allVerts, ...feasibleVerts].filter(
			(p) => p[0] >= 0 && p[1] >= 0
		);
		const maxX = Math.max(...visiblePoints.map((p) => p[0]), 1) * 1.3;
		const maxY = Math.max(...visiblePoints.map((p) => p[1]), 1) * 1.3;

		const colors = ['#6275d8', '#d4a853', '#2d9c6f', '#d44848', '#8b5cf6', '#0ea5e9'];
		constraints.forEach((c, i) => {
			const coefs = c.coefficients ?? [0, 0];
			const a = coefs[0];
			const b = coefs[1];
			const rhs = c.rhs ?? 0;
			const color = colors[i % colors.length];

			const linePoints: { x: number[]; y: number[] } = { x: [], y: [] };

			if (Math.abs(b) > 1e-9) {
				linePoints.x.push(0, maxX);
				linePoints.y.push(rhs / b, (rhs - a * maxX) / b);
			} else if (Math.abs(a) > 1e-9) {
				const xVal = rhs / a;
				linePoints.x.push(xVal, xVal);
				linePoints.y.push(0, maxY);
			}

			traces.push({
				x: linePoints.x,
				y: linePoints.y,
				mode: 'lines',
				name: c.label || `R${i + 1}`,
				line: { color, width: 2 }
			});
		});

		if (feasibleVerts.length >= 3) {
			const sorted = sortPolygonVertices(feasibleVerts);
			traces.push({
				x: [...sorted.map((p) => p[0]), sorted[0][0]],
				y: [...sorted.map((p) => p[1]), sorted[0][1]],
				fill: 'toself',
				fillcolor: 'rgba(59, 76, 192, 0.12)',
				line: { color: 'rgba(59, 76, 192, 0.3)', width: 1 },
				name: 'Región factible',
				mode: 'lines'
			});
		}

		const dark = $isDarkMode;
		const inkColor = dark ? '#f0f0f5' : '#1a1a2e';
		const inkLightColor = dark ? '#b0b0cc' : '#4a4a6a';
		const gridColor = dark ? '#22223b' : '#e5e2dc';
		const plotBg = dark ? '#121220' : '#faf9f7';
		const legendBg = dark ? 'rgba(18, 18, 32, 0.9)' : 'rgba(255,255,255,0.9)';
		const primaryColor = dark ? '#7a8af5' : '#3b4cc0';

		if (feasibleVerts.length > 0) {
			traces.push({
				x: feasibleVerts.map((p) => p[0]),
				y: feasibleVerts.map((p) => p[1]),
				mode: 'markers+text',
				name: 'Vértices factibles',
				text: feasibleVerts.map((p) => `(${fmt(p[0])}, ${fmt(p[1])})`),
				textposition: 'top center',
				textfont: { size: 10, family: 'JetBrains Mono', color: inkLightColor },
				marker: { color: primaryColor, size: 8 }
			});
		}

		if (optimalPoint) {
			traces.push({
				x: [optimalPoint[0]],
				y: [optimalPoint[1]],
				mode: 'markers',
				name:
					payload.optimal_value != null
						? `Óptimo (Z=${fmt(payload.optimal_value)})`
						: 'Óptimo',
				marker: {
					color: '#d4a853',
					size: 14,
					symbol: 'star',
					line: { width: 2, color: dark ? '#0b0b14' : '#1a1a2e' }
				}
			});
		}

		const layout: any = {
			xaxis: {
				title: { text: 'x₁', font: { color: inkColor } },
				range: [0, maxX],
				autorange: false,
				zeroline: true,
				zerolinewidth: 2,
				zerolinecolor: inkColor,
				gridcolor: gridColor,
				tickfont: { color: inkLightColor },
				dtick: Math.ceil(maxX / 8)
			},
			yaxis: {
				title: { text: 'x₂', font: { color: inkColor } },
				range: [0, maxY],
				autorange: false,
				zeroline: true,
				zerolinewidth: 2,
				zerolinecolor: inkColor,
				gridcolor: gridColor,
				tickfont: { color: inkLightColor },
				dtick: Math.ceil(maxY / 8)
			},
			showlegend: true,
			legend: {
				x: 1,
				xanchor: 'right',
				y: 1,
				bgcolor: legendBg,
				font: { size: 11, color: inkColor }
			},
			margin: { t: 20, r: 20, b: 50, l: 50 },
			paper_bgcolor: 'transparent',
			plot_bgcolor: plotBg,
			font: { family: 'Plus Jakarta Sans', color: inkColor },
			hoverlabel: { font: { family: 'JetBrains Mono' } }
		};

		Plotly.newPlot(graphContainer, traces, layout, {
			responsive: true,
			displayModeBar: true,
			modeBarButtonsToRemove: ['lasso2d', 'select2d']
		});
	}

	$effect(() => {
		// Re-run when payload changes or dark mode toggles.
		const _p = payload;
		const _d = $isDarkMode;
		void _p;
		void _d;
		tick().then(() => {
			renderGraph();
		});
	});

	onMount(() => {
		tick().then(() => {
			renderGraph();
		});
	});
</script>

<aside class="chart-card" aria-label="Gráfico de la solución">
	<header class="card-head">
		<span class="head-glyph" aria-hidden="true">◐</span>
		<span class="head-label">Gráfico</span>
		<span class="head-rule"></span>
	</header>
	<div bind:this={graphContainer} class="graph-canvas"></div>
</aside>

<style>
	.chart-card {
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		overflow: hidden;
		margin-top: 0.7rem;
		animation: fadeIn 0.3s ease-out;
	}

	.card-head {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		padding: 0.5rem 0.85rem;
		background: linear-gradient(
			to right,
			rgba(212, 168, 83, 0.06),
			rgba(212, 168, 83, 0) 70%
		);
		border-bottom: 1px solid var(--color-bot-border);
	}

	.head-glyph {
		color: var(--color-accent);
		font-family: var(--font-display);
		font-size: 0.95rem;
		line-height: 1;
	}

	.head-label {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-ink-muted);
	}

	.head-rule {
		flex: 1;
		height: 1px;
		background: linear-gradient(
			to right,
			rgba(212, 168, 83, 0.4),
			transparent
		);
		margin-left: 0.25rem;
	}

	.graph-canvas {
		height: 320px;
		background: #faf9f7;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(4px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
