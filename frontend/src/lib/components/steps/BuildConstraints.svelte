<script lang="ts">
	import {
		model,
		addMessage,
		advanceState,
		sendAssistantMessage,
		addTip,
		type Constraint
	} from '$lib/stores/chat';
	import { get } from 'svelte/store';
	import Latex from '$lib/components/Latex.svelte';
	import {
		constraintLatex,
		mixingToConstraint,
		mixingPreviewLatex,
		type MixingSpec
	} from '$lib/math/formula';

	type Mode = 'standard' | 'mixing';
	type SignKind = '<=' | '>=' | '=';

	let mode = $state<Mode>('standard');

	// Standard form fields
	let label = $state('');
	let coeff1 = $state<number | string>('');
	let coeff2 = $state<number | string>('');
	let sign = $state<SignKind>('<=');
	let rhs = $state<number | string>('');

	// Mixing form fields
	let mixLabel = $state('');
	let mixTargetIdx = $state<0 | 1>(0);
	let mixModeKind = $state<'min' | 'max'>('min');
	let mixPercent = $state<number | string>('');

	// In-place editing state
	let editingIndex = $state<number | null>(null);

	let localConstraints: Constraint[] = $state([...get(model).constraints]);

	function isValidNumber(val: string | number) {
		const str = String(val);
		if (str.trim() === '') return false;
		return !isNaN(Number(str));
	}

	function isInvalidInput(val: string | number) {
		const str = String(val);
		if (str.trim() === '') return false;
		return isNaN(Number(str));
	}

	function resetForm() {
		label = '';
		coeff1 = '';
		coeff2 = '';
		sign = '<=';
		rhs = '';
		mixLabel = '';
		mixTargetIdx = 0;
		mixModeKind = 'min';
		mixPercent = '';
		editingIndex = null;
	}

	function buildStandard(): Constraint | null {
		if (!label.trim() || !isValidNumber(coeff1) || !isValidNumber(coeff2) || !isValidNumber(rhs)) return null;
		return {
			label: label.trim(),
			coefficients: [Number(coeff1), Number(coeff2)],
			sign,
			rhs: Number(rhs)
		};
	}

	function buildMixing(): Constraint | null {
		if (!isValidNumber(mixPercent) || Number(mixPercent) <= 0 || Number(mixPercent) >= 100) return null;
		const m = get(model);
		const spec: MixingSpec = {
			mode: mixModeKind,
			targetVarIndex: mixTargetIdx,
			percent: Number(mixPercent)
		};
		const c = mixingToConstraint(spec, m.variables, mixLabel.trim());
		return c;
	}

	function addOrUpdate() {
		const c = mode === 'standard' ? buildStandard() : buildMixing();
		if (!c) return;

		if (editingIndex !== null) {
			localConstraints = localConstraints.map((existing, i) =>
				i === editingIndex ? c : existing
			);
		} else {
			localConstraints = [...localConstraints, c];
		}
		model.update((m) => ({ ...m, constraints: [...localConstraints] }));
		resetForm();
	}

	function startEdit(index: number) {
		const c = localConstraints[index];
		// Heuristic: if rhs is 0 and one coefficient is between 0 and 1 (1-p style), open
		// as standard editor (we don't reverse-engineer the mixing spec since the user
		// already saw the coefficient form).
		mode = 'standard';
		label = c.label;
		coeff1 = c.coefficients[0];
		coeff2 = c.coefficients[1];
		sign = c.sign;
		rhs = c.rhs;
		editingIndex = index;
	}

	function cancelEdit() {
		resetForm();
	}

	function removeConstraint(index: number) {
		localConstraints = localConstraints.filter((_, i) => i !== index);
		model.update((m) => ({ ...m, constraints: [...localConstraints] }));
		if (editingIndex === index) resetForm();
	}

	async function finish() {
		if (localConstraints.length === 0) return;

		const m = get(model);
		const lines = localConstraints
			.map((c, i) => `${i + 1}. ${c.label}: ${constraintLatex(c, m.variables)}`)
			.join('\n');

		addMessage('user', lines);
		advanceState();
		await sendAssistantMessage(
			'Revisá el modelo completo antes de resolver. Si está todo bien, confirmá para continuar.',
			{ delay: 800, expression: 'explain' }
		);
	}

	const canAddStandard = $derived(
		label.trim() !== '' && isValidNumber(coeff1) && isValidNumber(coeff2) && isValidNumber(rhs)
	);

	const canAddMixing = $derived(
		isValidNumber(mixPercent) && Number(mixPercent) > 0 && Number(mixPercent) < 100
	);

	const canAdd = $derived(mode === 'standard' ? canAddStandard : canAddMixing);

	const mixingPreview = $derived.by(() => {
		if (!isValidNumber(mixPercent)) return null;
		const m = get(model);
		const spec: MixingSpec = {
			mode: mixModeKind,
			targetVarIndex: mixTargetIdx,
			percent: Number(mixPercent) || 0
		};
		return {
			natural: mixingPreviewLatex(spec, m.variables),
			coefficient: constraintLatex(
				mixingToConstraint(spec, m.variables, ''),
				m.variables
			)
		};
	});

	$effect(() => {
		addTip('concept', 'Una restricción es una limitación del problema, ligada a recursos disponibles, capacidades máximas o condiciones mínimas.', '¿Qué es una restricción?');
		addTip('tip', 'Cuando el enunciado dice algo como "los balones deben ser al menos el 25% del total", usá la pestaña Mezcla / proporción: Slacko la convierte automáticamente.', 'Las restricciones de mezcla');
	});
</script>

<div class="step-enter space-y-3">
	<!-- Restricciones ya ingresadas -->
	{#if localConstraints.length > 0}
		<div class="constraint-list">
			{#each localConstraints as c, i}
				{@const m = get(model)}
				{@const isEditing = editingIndex === i}
				<div class="constraint-row" class:is-editing={isEditing}>
					<div class="row-tag">R{i + 1}</div>
					<div class="row-body">
						<div class="row-label">{c.label}</div>
						<div class="row-eq">
							<Latex expr={constraintLatex(c, m.variables)} />
						</div>
					</div>
					<div class="row-actions">
						<button
							type="button"
							class="action-btn edit"
							onclick={() => startEdit(i)}
							aria-label="Editar restricción"
							title="Editar"
						>
							<span aria-hidden="true">✎</span>
						</button>
						<button
							type="button"
							class="action-btn remove"
							onclick={() => removeConstraint(i)}
							aria-label="Quitar restricción"
							title="Quitar"
						>
							<span aria-hidden="true">×</span>
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Mode tabs -->
	<div class="mode-tabs" role="tablist" aria-label="Tipo de restricción">
		<button
			role="tab"
			aria-selected={mode === 'standard'}
			class="mode-tab"
			class:active={mode === 'standard'}
			onclick={() => (mode = 'standard')}
		>
			<span class="tab-glyph">≤≥=</span>
			<span class="tab-label">Recurso / mínimo / igualdad</span>
		</button>
		<button
			role="tab"
			aria-selected={mode === 'mixing'}
			class="mode-tab"
			class:active={mode === 'mixing'}
			onclick={() => (mode = 'mixing')}
		>
			<span class="tab-glyph">%</span>
			<span class="tab-label">Mezcla / proporción</span>
		</button>
	</div>

	<!-- Formulario -->
	<div class="form-card">
		{#if editingIndex !== null}
			<div class="edit-banner">
				<span class="super-title">Editando R{editingIndex + 1}</span>
				<button type="button" class="cancel-btn" onclick={cancelEdit}>
					Cancelar
				</button>
			</div>
		{/if}

		{#if mode === 'standard'}
			<div class="form-row">
				<label class="lbl" for="c-label">Nombre de la restricción</label>
				<input
					id="c-label"
					type="text"
					bind:value={label}
					placeholder="ej: Máquina A, Mano de obra…"
					class="text-input"
				/>
			</div>

			<div class="grid-form">
				<div>
					<label class="lbl" for="c-coef1">Coef x₁</label>
					<input
						id="c-coef1"
						type="text"
						bind:value={coeff1}
						placeholder="0"
						inputmode="decimal"
						class="num-input {isInvalidInput(coeff1) ? 'invalid' : ''}"
					/>
				</div>
				<div>
					<label class="lbl" for="c-coef2">Coef x₂</label>
					<input
						id="c-coef2"
						type="text"
						bind:value={coeff2}
						placeholder="0"
						inputmode="decimal"
						class="num-input {isInvalidInput(coeff2) ? 'invalid' : ''}"
					/>
				</div>
				<div>
					<label class="lbl" for="c-sign">Signo</label>
					<select id="c-sign" bind:value={sign} class="num-input">
						<option value="<=">≤</option>
						<option value=">=">≥</option>
						<option value="=">=</option>
					</select>
				</div>
				<div>
					<label class="lbl" for="c-rhs">Valor (RHS)</label>
					<input
						id="c-rhs"
						type="text"
						bind:value={rhs}
						placeholder="0"
						inputmode="decimal"
						class="num-input {isInvalidInput(rhs) ? 'invalid' : ''}"
					/>
				</div>
				<button
					onclick={addOrUpdate}
					disabled={!canAdd}
					class="add-btn"
				>
					{editingIndex !== null ? 'Guardar' : '+ Agregar'}
				</button>
			</div>
		{:else}
			<!-- Mixing form -->
			<div class="form-row">
				<label class="lbl" for="mix-label">Nombre (opcional)</label>
				<input
					id="mix-label"
					type="text"
					bind:value={mixLabel}
					placeholder="ej: Mínimo de balones en producción total"
					class="text-input"
				/>
			</div>

			<div class="mix-sentence">
				<span class="sentence-text">La variable</span>
				<select bind:value={mixTargetIdx} class="num-input compact">
					{#each get(model).variables as v, i}
						<option value={i}>{v.name} ({v.label || `variable ${i + 1}`})</option>
					{/each}
				</select>
				<span class="sentence-text">debe representar</span>
				<select bind:value={mixModeKind} class="num-input compact">
					<option value="min">al menos</option>
					<option value="max">a lo sumo</option>
				</select>
				<input
					type="text"
					bind:value={mixPercent}
					placeholder="25"
					inputmode="decimal"
					class="num-input compact percent {isInvalidInput(mixPercent) ? 'invalid' : ''}"
				/>
				<span class="sentence-text">% del total.</span>
			</div>

			{#if mixingPreview}
				<div class="mixing-preview">
					<div class="preview-block">
						<div class="preview-label">Cómo lo lee Slacko</div>
						<Latex expr={mixingPreview.natural} display />
					</div>
					<div class="preview-arrow" aria-hidden="true">↓</div>
					<div class="preview-block">
						<div class="preview-label">Forma estándar equivalente</div>
						<Latex expr={mixingPreview.coefficient} display />
					</div>
				</div>
			{/if}

			<button
				onclick={addOrUpdate}
				disabled={!canAdd}
				class="add-btn full"
			>
				{editingIndex !== null ? 'Guardar' : '+ Agregar restricción de proporción'}
			</button>
		{/if}
	</div>

	{#if localConstraints.length > 0}
		<button onclick={finish} class="finish-btn">
			Listo, revisar modelo
			<span class="count">
				({localConstraints.length} restriccion{localConstraints.length > 1 ? 'es' : ''})
			</span>
		</button>
	{/if}
</div>

<style>
	.constraint-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.constraint-row {
		display: grid;
		grid-template-columns: 36px 1fr auto;
		align-items: center;
		gap: 0.6rem;
		padding: 0.65rem 0.8rem;
		background: var(--color-surface-warm);
		border: 1px solid var(--color-bot-border);
		border-left: 3px solid var(--color-primary);
		border-radius: 0 8px 8px 0;
		transition: all 0.25s ease-in-out;
	}

	.constraint-row.is-editing {
		border-left-color: var(--color-accent);
		background: color-mix(in srgb, var(--color-accent) 8%, transparent);
		box-shadow: 0 0 0 1px var(--color-accent);
	}

	.row-tag {
		font-family: var(--font-mono);
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--color-primary);
		letter-spacing: 0.1em;
		text-align: center;
	}

	.row-body {
		display: flex;
		flex-direction: column;
		gap: 0.1rem;
		min-width: 0;
	}

	.row-label {
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink-muted);
		font-size: 0.78rem;
	}

	.row-eq {
		font-size: 0.95rem;
	}

	.row-actions {
		display: flex;
		gap: 0.25rem;
		opacity: 0.55;
		transition: opacity 0.25s ease-in-out;
	}

	.constraint-row:hover .row-actions {
		opacity: 1;
	}

	.action-btn {
		width: 26px;
		height: 26px;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		border: 1px solid var(--color-bot-border);
		background: transparent;
		font-family: var(--font-display);
		font-size: 0.95rem;
		line-height: 1;
		color: var(--color-ink-muted);
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.action-btn:hover {
		background: var(--color-surface-card);
		border-color: var(--color-ink);
		color: var(--color-ink);
	}

	.action-btn.edit:hover {
		color: var(--color-primary);
		border-color: var(--color-primary);
	}

	.action-btn.remove:hover {
		color: var(--color-error, #d44848);
		border-color: var(--color-error, #d44848);
	}

	.mode-tabs {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0;
		background: var(--color-surface-warm);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		padding: 3px;
	}

	.mode-tab {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 0.55rem 0.9rem;
		background: transparent;
		border: none;
		border-radius: 8px;
		font-family: var(--font-body);
		font-size: 0.8rem;
		color: var(--color-ink-muted);
		cursor: pointer;
		transition: all 0.25s ease-in-out;
	}

	.mode-tab.active {
		background: var(--color-surface-card);
		color: var(--color-ink);
		box-shadow: 0 1px 0 var(--color-bot-border),
			0 4px 12px -8px color-mix(in srgb, var(--color-ink) 18%, transparent);
	}

	.tab-glyph {
		font-family: var(--font-mono);
		font-size: 0.85rem;
		color: var(--color-accent);
		font-weight: 600;
	}

	.form-card {
		padding: 1rem;
		background: var(--color-surface-card);
		border: 1px solid var(--color-bot-border);
		border-radius: 12px;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.edit-banner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.4rem 0.65rem;
		background: color-mix(in srgb, var(--color-accent) 10%, transparent);
		border: 1px solid color-mix(in srgb, var(--color-accent) 40%, transparent);
		border-radius: 6px;
		margin: -0.25rem -0.25rem 0.25rem -0.25rem;
	}

	.super-title {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-accent);
	}

	.cancel-btn {
		font-family: var(--font-body);
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		background: transparent;
		border: none;
		cursor: pointer;
		text-decoration: underline;
		text-decoration-style: dotted;
		text-underline-offset: 3px;
	}

	.cancel-btn:hover {
		color: var(--color-ink);
	}

	.form-row {
		display: flex;
		flex-direction: column;
	}

	.lbl {
		display: block;
		font-size: 0.7rem;
		color: var(--color-ink-muted);
		margin-bottom: 0.25rem;
	}

	.text-input,
	.num-input {
		width: 100%;
		padding: 0.55rem 0.75rem;
		border-radius: 8px;
		border: 1px solid var(--color-bot-border);
		font-size: 0.85rem;
		background: var(--color-surface-card);
		color: var(--color-ink);
		font-family: inherit;
		height: 38px;
		box-sizing: border-box;
	}

	.text-input::placeholder,
	.num-input::placeholder {
		color: var(--color-ink-muted);
		opacity: 0.5;
	}

	.num-input option {
		background: var(--color-surface-card);
		color: var(--color-ink);
	}

	.num-input {
		font-family: var(--font-mono);
	}

	.text-input:focus,
	.num-input:focus {
		outline: none;
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 15%, transparent);
		border-color: var(--color-primary);
	}

	.num-input.invalid {
		border-color: rgba(239, 68, 68, 0.6);
		background-color: rgba(239, 68, 68, 0.1);
		color: #ef4444;
	}
	.num-input.invalid:focus {
		box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
		border-color: #ef4444;
	}

	.grid-form {
		display: grid;
		grid-template-columns: 1fr 1fr 0.7fr 1fr auto;
		gap: 0.5rem;
		align-items: end;
	}

	.add-btn {
		padding: 0.55rem 1rem;
		background: var(--color-ink);
		color: var(--color-surface-card);
		border: none;
		border-radius: 8px;
		font-family: var(--font-body);
		font-size: 0.8rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
		white-space: nowrap;
		height: 38px;
		box-sizing: border-box;
		align-self: end;
		display: inline-flex;
		align-items: center;
		justify-content: center;
	}

	.add-btn:hover:not(:disabled) {
		background: var(--color-primary);
	}

	.add-btn:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.add-btn.full {
		width: 100%;
		padding: 0.7rem 1rem;
	}

	.mix-sentence {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		flex-wrap: wrap;
		padding: 0.85rem 1rem;
		background: var(--color-surface-warm);
		border-radius: 8px;
		border: 1px dashed var(--color-bot-border);
		font-family: var(--font-display);
		font-style: italic;
		color: var(--color-ink);
		font-size: 0.95rem;
		line-height: 1.6;
	}

	.sentence-text {
		color: var(--color-ink-light);
	}

	.num-input.compact {
		width: auto;
		font-family: var(--font-body);
		font-style: normal;
		padding: 0.35rem 0.6rem;
		font-size: 0.85rem;
	}

	.num-input.compact.percent {
		width: 70px;
		font-family: var(--font-mono);
		text-align: center;
	}

	.mixing-preview {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.25rem;
		padding: 0.85rem 1rem;
		background: var(--color-surface-warm);
		border: 1px solid var(--color-bot-border);
		border-radius: 10px;
		border-left: 3px solid var(--color-accent);
	}

	.preview-block {
		width: 100%;
		text-align: center;
	}

	.preview-label {
		font-family: var(--font-display);
		font-size: 0.85rem;
		font-weight: 500;
		color: var(--color-ink-muted);
		margin-bottom: 0.1rem;
	}

	.preview-arrow {
		font-family: var(--font-display);
		font-size: 1.2rem;
		color: var(--color-accent);
		line-height: 1;
		opacity: 0.6;
	}

	.finish-btn {
		width: 100%;
		padding: 0.75rem 1rem;
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: 10px;
		font-family: var(--font-body);
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.25s ease-in-out;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.4rem;
	}

	.finish-btn:hover {
		background: var(--color-primary-dark, #2d3a9a);
		transform: translateY(-1px);
		box-shadow: 0 6px 16px -8px rgba(59, 76, 192, 0.5);
	}

	.count {
		opacity: 0.8;
		font-size: 0.8rem;
	}

	@media (max-width: 640px) {
		.grid-form {
			grid-template-columns: 1fr 1fr;
		}
		.add-btn {
			grid-column: span 2;
		}
	}
</style>
