import type { Constraint, LPModel } from '$lib/stores/chat';

export interface SlackInfo {
	constraintLabel: string;
	originalSign: '<=' | '>=' | '=';
	rhs: number;
	lhs: number;
	slack: number; // signed; for ≤, slack = rhs - lhs (positive = ociosity);
	// for ≥, surplus = lhs - rhs (positive = exceso por encima del mínimo).
	kind: 'slack' | 'surplus' | 'equality';
	binding: boolean;
}

const EPS = 1e-6;

export function computeSlacks(
	model: LPModel,
	optimal: number[]
): SlackInfo[] {
	return model.constraints.map((c: Constraint) => {
		const lhs = c.coefficients.reduce(
			(acc, coef, i) => acc + coef * (optimal[i] ?? 0),
			0
		);
		const rhs = c.rhs;

		if (c.sign === '<=') {
			const slack = rhs - lhs;
			return {
				constraintLabel: c.label,
				originalSign: c.sign,
				rhs,
				lhs,
				slack,
				kind: 'slack' as const,
				binding: Math.abs(slack) < EPS
			};
		}
		if (c.sign === '>=') {
			const surplus = lhs - rhs;
			return {
				constraintLabel: c.label,
				originalSign: c.sign,
				rhs,
				lhs,
				slack: surplus,
				kind: 'surplus' as const,
				binding: Math.abs(surplus) < EPS
			};
		}
		return {
			constraintLabel: c.label,
			originalSign: c.sign,
			rhs,
			lhs,
			slack: rhs - lhs,
			kind: 'equality' as const,
			binding: true
		};
	});
}

export function fmt(n: number, digits = 2): string {
	if (Math.abs(n) < EPS) return '0';
	if (Number.isInteger(n)) return n.toString();
	return n.toFixed(digits).replace(/\.?0+$/, '');
}
