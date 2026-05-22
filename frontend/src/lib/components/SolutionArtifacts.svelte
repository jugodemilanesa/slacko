<script lang="ts">
	import { onMount, tick } from 'svelte';
	import type { LPModel, SolverResult } from '$lib/stores/chat';

	let {
		model,
		result,
		show = 'both',
		variant = 'full'
	}: {
		model: LPModel;
		result: SolverResult;
		show?: 'both' | 'graph' | 'vertices';
		variant?: 'full' | 'compact';
	} = $props();

	let graphContainer = $state<HTMLDivElement>();

	function fmt(n: number): string {
		return Number.isInteger(n) ? n.toString() : n.toFixed(2).replace(/\.?0+$/, '');
	}

	function sortPolygonVertices(vertices: number[][]): number[][] {
		const cx = vertices.reduce((s, p) => s + p[0], 0) / vertices.length;
		const cy = vertices.reduce((s, p) => s + p[1], 0) / vertices.length;
		return [...vertices].sort(
			(a, b) => Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx)
		);
	}

	async function renderGraph() {
		if (!graphContainer) return;
		const Plotly = await import('plotly.js-dist-min');
		const traces: any[] = [];

		const allPoints = [...result.vertices, ...result.feasible_vertices];
		const maxX = Math.max(...allPoints.map((p) => p[0]), 1) * 1.3;
		const maxY = Math.max(...allPoints.map((p) => p[1]), 1) * 1.3;

		const colors = ['#6275d8', '#d4a853', '#2d9c6f', '#d44848', '#8b5cf6', '#0ea5e9'];
		model.constraints.forEach((c, i) => {
			const a = c.coefficients[0];
			const b = c.coefficients[1];
			const rhs = c.rhs;
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

		if (result.feasible_vertices.length >= 3) {
			const sorted = sortPolygonVertices(result.feasible_vertices);
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

		traces.push({
			x: result.feasible_vertices.map((p) => p[0]),
			y: result.feasible_vertices.map((p) => p[1]),
			mode: 'markers+text',
			name: 'Vértices factibles',
			text: result.feasible_vertices.map((p) => `(${fmt(p[0])}, ${fmt(p[1])})`),
			textposition: 'top center',
			textfont: { size: 10, family: 'JetBrains Mono', color: '#4a4a6a' },
			marker: { color: '#3b4cc0', size: 8 }
		});

		if (result.optimal_point) {
			traces.push({
				x: [result.optimal_point[0]],
				y: [result.optimal_point[1]],
				mode: 'markers',
				name: `Óptimo (Z=${fmt(result.optimal_value!)})`,
				marker: {
					color: '#d4a853',
					size: 14,
					symbol: 'star',
					line: { width: 2, color: '#1a1a2e' }
				}
			});

			const c1 = model.variables[0].coefficient;
			const c2 = model.variables[1].coefficient;
			const z = result.optimal_value!;
			if (Math.abs(c2) > 1e-9) {
				traces.push({
					x: [0, maxX],
					y: [z / c2, (z - c1 * maxX) / c2],
					mode: 'lines',
					name: `Z = ${fmt(z)}`,
					line: { color: '#d4a853', width: 2, dash: 'dash' }
				});
			}
		}

		const layout: any = {
			xaxis: {
				title: { text: model.variables[0].name + ' (' + model.variables[0].label + ')' },
				range: [0, maxX],
				zeroline: true,
				zerolinewidth: 2,
				zerolinecolor: '#1a1a2e',
				gridcolor: '#e5e2dc',
				dtick: Math.ceil(maxX / 8)
			},
			yaxis: {
				title: { text: model.variables[1].name + ' (' + model.variables[1].label + ')' },
				range: [0, maxY],
				zeroline: true,
				zerolinewidth: 2,
				zerolinecolor: '#1a1a2e',
				gridcolor: '#e5e2dc',
				dtick: Math.ceil(maxY / 8)
			},
			showlegend: true,
			legend: { x: 1, xanchor: 'right', y: 1, bgcolor: 'rgba(255,255,255,0.9)', font: { size: 11 } },
			margin: { t: 20, r: 20, b: 60, l: 60 },
			paper_bgcolor: 'transparent',
			plot_bgcolor: '#faf9f7',
			font: { family: 'Plus Jakarta Sans', color: '#1a1a2e' },
			hoverlabel: { font: { family: 'JetBrains Mono' } }
		};

		Plotly.newPlot(graphContainer, traces, layout, {
			responsive: true,
			displayModeBar: variant !== 'compact',
			modeBarButtonsToRemove: ['lasso2d', 'select2d']
		});
	}

	onMount(async () => {
		if (show === 'graph' || show === 'both') {
			await tick();
			renderGraph();
		}
	});
</script>

<div class="artifacts" class:compact={variant === 'compact'}>
	{#if show === 'graph' || show === 'both'}
		<div class="panel graph-panel">
			<header class="panel-head">
				<span class="head-glyph" aria-hidden="true">◐</span>
				<span class="head-label">Gráfico</span>
				<span class="head-rule"></span>
			</header>
			<div
				bind:this={graphContainer}
				class="graph-canvas"
				class:compact-graph={variant === 'compact'}
			></div>
		</div>
	{/if}

	{#if show === 'vertices' || show === 'both'}
		<div class="panel">
			<header class="panel-head">
				<span class="head-glyph" aria-hidden="true">▦</span>
				<span class="head-label">Análisis de vértices</span>
				<span class="head-rule"></span>
			</header>
			<div class="table-wrap">
				<table>
					<thead>
						<tr>
							<th class="t-th">Vértice</th>
							<th class="t-th t-num">{model.variables[0].name}</th>
							<th class="t-th t-num">{model.variables[1].name}</th>
							<th class="t-th t-num">Z</th>
						</tr>
					</thead>
					<tbody>
						{#each result.vertex_analysis as va, i}
							{@const isOptimal =
								result.optimal_point &&
								Math.abs(va.x1 - result.optimal_point[0]) < 1e-6 &&
								Math.abs(va.x2 - result.optimal_point[1]) < 1e-6}
							<tr class:optimal={isOptimal} class:alt={i % 2 === 1 && !isOptimal}>
								<td>
									<span class="vertex-name">
										{#if isOptimal}<span class="star">★</span>{/if}
										({fmt(va.x1)}, {fmt(va.x2)})
									</span>
								</td>
								<td class="t-num">{fmt(va.x1)}</td>
								<td class="t-num">{fmt(va.x2)}</td>
								<td class="t-num t-z" class:opt={isOptimal}>{fmt(va.z)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>

<style>
	.artifacts {
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
	}

	.panel {
		background: var(--color-surface-card, #fffaf2);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		overflow: hidden;
	}

	.compact .panel {
		border-radius: 8px;
	}

	.panel-head {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		padding: 0.55rem 0.9rem;
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
		font-family: var(--font-mono);
		font-size: 0.62rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
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
		height: 420px;
		background: #faf9f7;
	}

	.compact-graph {
		height: 280px;
	}

	.table-wrap {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-family: var(--font-body);
		font-size: 0.85rem;
	}

	.t-th {
		text-align: left;
		padding: 0.55rem 0.9rem;
		font-family: var(--font-mono);
		font-size: 0.6rem;
		letter-spacing: 0.18em;
		text-transform: uppercase;
		color: var(--color-ink-muted);
		background: var(--color-surface-warm, #fff7e8);
		border-bottom: 1px solid var(--color-bot-border);
	}

	.t-num {
		text-align: right;
		font-family: var(--font-mono);
	}

	tbody td {
		padding: 0.5rem 0.9rem;
		border-bottom: 1px solid var(--color-bot-border);
	}

	tbody tr:last-child td {
		border-bottom: none;
	}

	tbody tr.alt {
		background: rgba(212, 168, 83, 0.025);
	}

	tbody tr.optimal {
		background: rgba(212, 168, 83, 0.14);
		font-weight: 600;
	}

	.vertex-name {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
	}

	.star {
		color: var(--color-accent);
		font-size: 0.95rem;
		line-height: 1;
	}

	.t-z {
		color: var(--color-ink);
	}

	.t-z.opt {
		color: var(--color-accent);
		font-weight: 700;
	}
</style>
