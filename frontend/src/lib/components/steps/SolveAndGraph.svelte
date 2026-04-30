<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { model, addMessage, advanceState, solverResult } from '$lib/stores/chat';
	import { solveProblem } from '$lib/api/solver';
	import { get } from 'svelte/store';

	let loading = $state(true);
	let error = $state('');
	let graphContainer = $state<HTMLDivElement>();

	onMount(async () => {
		try {
			const m = get(model);
			const result = await solveProblem({
				objective_coefficients: m.variables.map((v) => v.coefficient),
				sense: m.sense,
				constraints: m.constraints.map((c) => ({
					coefficients: c.coefficients,
					sign: c.sign,
					rhs: c.rhs,
					label: c.label
				}))
			});
			solverResult.set(result);
			loading = false;

			await tick();
			if (graphContainer) {
				renderGraph(result, m);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error al resolver';
			loading = false;
		}
	});

	async function renderGraph(
		result: NonNullable<typeof $solverResult>,
		m: ReturnType<typeof get<typeof model>>
	) {
		const Plotly = await import('plotly.js-dist-min');

		const traces: Plotly.Data[] = [];

		// Determine axis range
		const allPoints = [...result.vertices, ...result.feasible_vertices];
		const maxX = Math.max(...allPoints.map((p) => p[0]), 1) * 1.3;
		const maxY = Math.max(...allPoints.map((p) => p[1]), 1) * 1.3;

		// Constraint lines
		m.constraints.forEach((c, i) => {
			const a = c.coefficients[0];
			const b = c.coefficients[1];
			const rhs = c.rhs;
			const colors = ['#6275d8', '#d4a853', '#2d9c6f', '#d44848', '#8b5cf6'];
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

		// Feasible region (shaded)
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

		// Feasible vertices
		traces.push({
			x: result.feasible_vertices.map((p) => p[0]),
			y: result.feasible_vertices.map((p) => p[1]),
			mode: 'markers+text',
			name: 'Vértices factibles',
			text: result.feasible_vertices.map((p) => `(${round(p[0])}, ${round(p[1])})`),
			textposition: 'top center',
			textfont: { size: 10, family: 'JetBrains Mono', color: '#4a4a6a' },
			marker: { color: '#3b4cc0', size: 8 }
		});

		// Optimal point
		if (result.optimal_point) {
			traces.push({
				x: [result.optimal_point[0]],
				y: [result.optimal_point[1]],
				mode: 'markers',
				name: `Óptimo (Z=${round(result.optimal_value!)})`,
				marker: { color: '#d4a853', size: 14, symbol: 'star', line: { width: 2, color: '#1a1a2e' } }
			});
		}

		// Objective function line (dashed, through optimal)
		if (result.optimal_point && result.optimal_value !== null) {
			const c1 = m.variables[0].coefficient;
			const c2 = m.variables[1].coefficient;
			const z = result.optimal_value;

			if (Math.abs(c2) > 1e-9) {
				traces.push({
					x: [0, maxX],
					y: [z / c2, (z - c1 * maxX) / c2],
					mode: 'lines',
					name: `Z = ${z}`,
					line: { color: '#d4a853', width: 2, dash: 'dash' }
				});
			}
		}

		const layout: Partial<Plotly.Layout> = {
			xaxis: {
				title: { text: m.variables[0].name + ' (' + m.variables[0].label + ')' },
				range: [0, maxX],
				zeroline: true,
				zerolinewidth: 2,
				zerolinecolor: '#1a1a2e',
				gridcolor: '#e5e2dc',
				dtick: Math.ceil(maxX / 8)
			},
			yaxis: {
				title: { text: m.variables[1].name + ' (' + m.variables[1].label + ')' },
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
			displayModeBar: true,
			modeBarButtonsToRemove: ['lasso2d', 'select2d']
		});
	}

	function sortPolygonVertices(vertices: number[][]): number[][] {
		const cx = vertices.reduce((s, p) => s + p[0], 0) / vertices.length;
		const cy = vertices.reduce((s, p) => s + p[1], 0) / vertices.length;
		return [...vertices].sort(
			(a, b) => Math.atan2(a[1] - cy, a[0] - cx) - Math.atan2(b[1] - cy, b[0] - cx)
		);
	}

	function round(n: number): string {
		return Number.isInteger(n) ? n.toString() : n.toFixed(2);
	}

	function next() {
		addMessage('user', 'Ver interpretación');
		const r = get(solverResult);
		const m = get(model);
		if (r?.optimal_point) {
			const sense = m.sense === 'maximize' ? 'máxima' : 'mínima';
			addMessage(
				'assistant',
				`El punto óptimo se encuentra en **${m.variables[0].name} = ${round(r.optimal_point[0])}** (${m.variables[0].label}), **${m.variables[1].name} = ${round(r.optimal_point[1])}** (${m.variables[1].label}), generando un **Z = ${round(r.optimal_value!)}** ${sense}.`
			);
		} else {
			addMessage('assistant', 'No se encontró una solución factible para este problema.');
		}
		advanceState();
	}
</script>

<div class="step-enter space-y-4">
	{#if loading}
		<div class="p-8 text-center text-ink-muted">
			<div class="animate-pulse">Resolviendo el problema...</div>
		</div>
	{:else if error}
		<div class="p-4 bg-error/10 text-error rounded-xl text-sm">{error}</div>
	{:else if $solverResult}
		<!-- Vertex analysis table -->
		<div class="rounded-xl overflow-hidden border border-bot-border">
			<table class="w-full text-sm">
				<thead>
					<tr class="bg-sidebar text-white/90">
						<th class="px-4 py-2.5 text-left font-medium">Vértice</th>
						<th class="px-4 py-2.5 text-right font-medium font-mono">
							{get(model).variables[0].name}
						</th>
						<th class="px-4 py-2.5 text-right font-medium font-mono">
							{get(model).variables[1].name}
						</th>
						<th class="px-4 py-2.5 text-right font-medium font-mono">Z</th>
					</tr>
				</thead>
				<tbody>
					{#each $solverResult.vertex_analysis as va, i}
						{@const isOptimal =
							$solverResult.optimal_point &&
							Math.abs(va.x1 - $solverResult.optimal_point[0]) < 1e-6 &&
							Math.abs(va.x2 - $solverResult.optimal_point[1]) < 1e-6}
						<tr
							class="{isOptimal
								? 'bg-accent/10 font-semibold'
								: i % 2 === 0
									? 'bg-white'
									: 'bg-surface-warm'}"
						>
							<td class="px-4 py-2">
								{isOptimal ? '★' : ''} ({round(va.x1)}, {round(va.x2)})
							</td>
							<td class="px-4 py-2 text-right font-mono">{round(va.x1)}</td>
							<td class="px-4 py-2 text-right font-mono">{round(va.x2)}</td>
							<td class="px-4 py-2 text-right font-mono {isOptimal ? 'text-accent' : ''}">
								{round(va.z)}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Graph -->
		<div
			bind:this={graphContainer}
			class="w-full h-[420px] rounded-xl border border-bot-border bg-white overflow-hidden"
		></div>

		<button
			onclick={next}
			class="w-full py-2.5 bg-primary text-white rounded-lg text-sm font-medium
				hover:bg-primary-dark transition-colors cursor-pointer"
		>
			Ver interpretación final
		</button>
	{/if}
</div>
