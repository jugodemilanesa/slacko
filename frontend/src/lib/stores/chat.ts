import { writable, derived } from 'svelte/store';

export type ChatState =
	| 'SELECT_MODE'
	| 'INPUT_ENUNCIADO'
	| 'DEFINE_OBJECTIVE'
	| 'DEFINE_VARIABLES'
	| 'BUILD_CONSTRAINTS'
	| 'VALIDATE_MODEL'
	| 'CONVERT_FORMS'
	| 'SOLVE_AND_GRAPH'
	| 'INTERPRET'
	| 'THEORY_QUERY';

export interface Variable {
	name: string;
	label: string;
	coefficient: number;
}

export interface Constraint {
	label: string;
	coefficients: number[];
	sign: '<=' | '>=' | '=';
	rhs: number;
}

export interface LPModel {
	enunciado: string;
	sense: 'maximize' | 'minimize';
	variables: Variable[];
	constraints: Constraint[];
}

export interface SolverResult {
	vertices: number[][];
	feasible_vertices: number[][];
	optimal_point: number[] | null;
	optimal_value: number | null;
	vertex_analysis: Array<{ x1: number; x2: number; z: number }>;
}

export interface StandardFormResult {
	constraints: Array<{
		label: string;
		original_sign: string;
		rhs: number;
		slack_var: string | null;
		surplus_var: string | null;
		artificial_var: string | null;
		equation: string;
	}>;
	slack_variables: string[];
	surplus_variables: string[];
	artificial_variables: string[];
}

export interface ChatMessage {
	id: string;
	role: 'assistant' | 'user';
	content: string;
	step?: ChatState;
}

const STEP_ORDER: ChatState[] = [
	'SELECT_MODE',
	'INPUT_ENUNCIADO',
	'DEFINE_OBJECTIVE',
	'DEFINE_VARIABLES',
	'BUILD_CONSTRAINTS',
	'VALIDATE_MODEL',
	'CONVERT_FORMS',
	'SOLVE_AND_GRAPH',
	'INTERPRET'
];

const STEP_LABELS: Record<ChatState, string> = {
	SELECT_MODE: 'Modo',
	INPUT_ENUNCIADO: 'Enunciado',
	DEFINE_OBJECTIVE: 'Objetivo',
	DEFINE_VARIABLES: 'Variables',
	BUILD_CONSTRAINTS: 'Restricciones',
	VALIDATE_MODEL: 'Validación',
	CONVERT_FORMS: 'Forma estándar',
	SOLVE_AND_GRAPH: 'Resolución',
	INTERPRET: 'Interpretación',
	THEORY_QUERY: 'Consulta teórica'
};

export { STEP_ORDER, STEP_LABELS };

function generateId(): string {
	return Math.random().toString(36).substring(2, 10);
}

export const currentState = writable<ChatState>('SELECT_MODE');
export const messages = writable<ChatMessage[]>([]);
export const model = writable<LPModel>({
	enunciado: '',
	sense: 'maximize',
	variables: [
		{ name: 'x1', label: '', coefficient: 0 },
		{ name: 'x2', label: '', coefficient: 0 }
	],
	constraints: []
});
export const solverResult = writable<SolverResult | null>(null);
export const standardFormResult = writable<StandardFormResult | null>(null);

export const isGuidedFlow = derived(currentState, ($state) =>
	STEP_ORDER.includes($state)
);

export const currentStepIndex = derived(currentState, ($state) =>
	STEP_ORDER.indexOf($state)
);

export function addMessage(role: 'assistant' | 'user', content: string, step?: ChatState) {
	messages.update((msgs) => [...msgs, { id: generateId(), role, content, step }]);
}

export function advanceState() {
	currentState.update((state) => {
		const idx = STEP_ORDER.indexOf(state);
		if (idx >= 0 && idx < STEP_ORDER.length - 1) {
			return STEP_ORDER[idx + 1];
		}
		return state;
	});
}

export function goToState(state: ChatState) {
	currentState.set(state);
}

export function resetChat() {
	currentState.set('SELECT_MODE');
	messages.set([]);
	model.set({
		enunciado: '',
		sense: 'maximize',
		variables: [
			{ name: 'x1', label: '', coefficient: 0 },
			{ name: 'x2', label: '', coefficient: 0 }
		],
		constraints: []
	});
	solverResult.set(null);
	standardFormResult.set(null);
}
