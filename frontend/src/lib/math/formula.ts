import type { Constraint, LPModel, Variable } from '$lib/stores/chat';

function fmtNum(n: number): string {
	if (Number.isInteger(n)) return n.toString();
	return n.toFixed(2).replace(/\.?0+$/, '');
}

function varSym(name: string): string {
	const m = /^([a-zA-Z]+)(\d+)?$/.exec(name);
	if (!m) return name;
	const [, base, idx] = m;
	return idx ? `${base}_{${idx}}` : base;
}

function coefTerm(coef: number, varName: string, isFirst: boolean): string {
	const sym = varSym(varName);
	const abs = Math.abs(coef);
	const sign = coef < 0 ? '-' : isFirst ? '' : '+';
	if (abs === 0) return '';
	if (abs === 1) return `${sign}${sign === '-' ? '\\,' : ''}${sym}`;
	return `${sign}${sign && sign !== '-' ? '\\,' : ''}${fmtNum(abs)}${sym}`;
}

export function objectiveLatex(model: LPModel): string {
	const sense = model.sense === 'maximize' ? '\\text{Max}' : '\\text{Min}';
	const parts: string[] = [];
	model.variables.forEach((v, i) => {
		const term = coefTerm(v.coefficient, v.name, parts.length === 0);
		if (term) parts.push(term);
	});
	const rhs = parts.length > 0 ? parts.join(' ') : '0';
	return `${sense}\\;\\; Z = ${rhs}`;
}

export function constraintLatex(c: Constraint, vars: Variable[]): string {
	const parts: string[] = [];
	c.coefficients.forEach((coef, i) => {
		const term = coefTerm(coef, vars[i]?.name ?? `x_${i + 1}`, parts.length === 0);
		if (term) parts.push(term);
	});
	const lhs = parts.length > 0 ? parts.join(' ') : '0';
	const signLatex = c.sign === '<=' ? '\\leq' : c.sign === '>=' ? '\\geq' : '=';
	return `${lhs} ${signLatex} ${fmtNum(c.rhs)}`;
}

export function nonNegativityLatex(vars: Variable[]): string {
	return `${vars.map((v) => varSym(v.name)).join(',\\,')} \\geq 0`;
}

/** For mixing/proportion constraints: "x_k is at least p% of total". */
export interface MixingSpec {
	mode: 'min' | 'max';
	targetVarIndex: number;
	percent: number;
}

/**
 * Convert a mixing/proportion spec into coefficient form.
 *
 * x_k >= p * (x_1 + x_2 + ...)  =>  (1-p)x_k - p*sum_{i!=k} x_i >= 0
 * x_k <= p * (x_1 + x_2 + ...)  =>  (1-p)x_k - p*sum_{i!=k} x_i <= 0
 */
export function mixingToConstraint(
	spec: MixingSpec,
	vars: Variable[],
	label: string
): Constraint {
	const p = spec.percent / 100;
	const coeffs = vars.map((_, i) =>
		i === spec.targetVarIndex ? 1 - p : -p
	);
	return {
		label: label || `Proporción ${vars[spec.targetVarIndex].name}`,
		coefficients: coeffs,
		sign: spec.mode === 'min' ? '>=' : '<=',
		rhs: 0
	};
}

export function mixingPreviewLatex(spec: MixingSpec, vars: Variable[]): string {
	const xk = varSym(vars[spec.targetVarIndex].name);
	const total = vars.map((v) => varSym(v.name)).join(' + ');
	const op = spec.mode === 'min' ? '\\geq' : '\\leq';
	return `${xk} ${op} ${spec.percent / 100}\\,(${total})`;
}
