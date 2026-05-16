import { api } from './client';
import type { SolverResult, StandardFormResult } from '$lib/stores/chat';

interface SolveRequest {
	objective_coefficients: number[];
	sense: string;
	constraints: Array<{
		coefficients: number[];
		sign: string;
		rhs: number;
		label?: string;
	}>;
}

interface StandardFormRequest {
	variables: string[];
	objective_coefficients: number[];
	sense: string;
	constraints: Array<{
		coefficients: number[];
		sign: string;
		rhs: number;
		label?: string;
	}>;
}

export async function solveProblem(data: SolveRequest): Promise<SolverResult> {
	return api<SolverResult>('/solver/solve/', {
		method: 'POST',
		body: data
	});
}

export async function getStandardForm(data: StandardFormRequest): Promise<StandardFormResult> {
	return api<StandardFormResult>('/solver/standard-form/', {
		method: 'POST',
		body: data
	});
}
