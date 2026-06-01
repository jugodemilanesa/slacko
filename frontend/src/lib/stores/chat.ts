import { writable, derived, get, type Readable } from 'svelte/store';

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
	| 'THEORY_QUERY'
	| 'TUTORIAL'
	| 'LLM_CHAT';

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
	status?: 'optimal' | 'infeasible' | 'single_point';
	warning?: string;
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

export type Expression = 'idle' | 'thinking' | 'happy' | 'sad' | 'explain';

export interface ChatMessage {
	id: string;
	role: 'assistant' | 'user' | 'divider';
	content: string;
	step?: ChatState;
	expression?: Expression;
}

export interface TipEntry {
	id: string;
	kind: 'tip' | 'concept' | 'warning' | 'question' | 'note';
	title?: string;
	content: string;
	step: ChatState;
}

const STEP_ORDER: ChatState[] = [
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
	THEORY_QUERY: 'Consulta teórica',
	TUTORIAL: 'Tutorial',
	LLM_CHAT: 'Chat con Slacko'
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
export const tipsHistory = writable<TipEntry[]>([]);

export function addTip(kind: TipEntry['kind'], content: string, title?: string) {
	tipsHistory.update((tips) => {
		const key = `${kind}|${title || ''}|${content.slice(0, 40)}`;
		if (tips.some((t) => `${t.kind}|${t.title || ''}|${t.content.slice(0, 40)}` === key)) {
			return tips;
		}
		return [
			...tips,
			{
				id: generateId(),
				kind,
				title,
				content,
				step: get(currentState)
			}
		];
	});
}

export const isGuidedFlow = derived(currentState, ($state) =>
	STEP_ORDER.includes($state)
);

export const currentStepIndex = derived(currentState, ($state) =>
	STEP_ORDER.indexOf($state)
);

export const assistantThinking = writable<boolean>(false);

export function addMessage(
	role: 'assistant' | 'user' | 'divider',
	content: string,
	step?: ChatState,
	expression?: Expression
) {
	messages.update((msgs) => [
		...msgs,
		{ id: generateId(), role, content, step, expression }
	]);
}

export interface SendOptions {
	delay?: number; // ms before message appears
	thinkingDelay?: number; // ms to show 'thinking' before delay (defaults to delay)
	expression?: Expression;
	step?: ChatState;
}

/**
 * Envía un mensaje del asistente con un pequeño retardo y muestra el avatar en
 * modo 'thinking' mientras tanto. Devuelve una promesa que resuelve cuando el
 * mensaje fue añadido.
 */
export async function sendAssistantMessage(
	content: string,
	opts: SendOptions = {}
): Promise<void> {
	const delay = opts.delay ?? 650;
	assistantThinking.set(true);
	await new Promise((r) => setTimeout(r, delay));
	assistantThinking.set(false);
	addMessage('assistant', content, opts.step, opts.expression ?? 'idle');
}

export function addStepDivider(label: string, step: ChatState) {
	addMessage('divider', label, step);
}

export function advanceState() {
	currentState.update((state) => {
		if (state === 'SELECT_MODE') {
			const next = STEP_ORDER[0];
			// inject divider for traceability
			addMessage('divider', STEP_LABELS[next], next);
			return next;
		}
		const idx = STEP_ORDER.indexOf(state);
		if (idx >= 0 && idx < STEP_ORDER.length - 1) {
			const next = STEP_ORDER[idx + 1];
			// inject divider for traceability
			addMessage('divider', STEP_LABELS[next], next);
			return next;
		}
		return state;
	});
}

export function goToState(state: ChatState) {
	currentState.set(state);
}

export function resetChat() {
	if (typeof window !== 'undefined') {
		window.sessionStorage.removeItem(GUIDED_SESSION_KEY);
	}
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
	tipsHistory.set([]);
}

// ─── Persistencia en sessionStorage ──────────────────────────────────────────

const GUIDED_SESSION_KEY = 'slacko.guidedSession';

interface PersistedGuidedState {
	currentState: ChatState;
	messages: ChatMessage[];
	model: LPModel;
	solverResult: SolverResult | null;
	standardFormResult: StandardFormResult | null;
	tipsHistory: TipEntry[];
}

export function restoreGuidedState(): boolean {
	if (typeof window === 'undefined') return false;
	const raw = window.sessionStorage.getItem(GUIDED_SESSION_KEY);
	if (!raw) return false;
	try {
		const saved: PersistedGuidedState = JSON.parse(raw);
		currentState.set(saved.currentState);
		messages.set(saved.messages);
		model.set(saved.model);
		solverResult.set(saved.solverResult);
		standardFormResult.set(saved.standardFormResult);
		tipsHistory.set(saved.tipsHistory);
		return true;
	} catch {
		window.sessionStorage.removeItem(GUIDED_SESSION_KEY);
		return false;
	}
}

// Auto-save reactivo: persiste cada vez que cambia cualquier store del flujo guiado.
// No guarda el estado inicial vacío (SELECT_MODE sin mensajes) para no sobreescribir
// una sesión restaurada con el valor de reset.
const _allGuidedState = derived(
	[currentState, messages, model, solverResult, standardFormResult, tipsHistory] as [
		Readable<ChatState>,
		Readable<ChatMessage[]>,
		Readable<LPModel>,
		Readable<SolverResult | null>,
		Readable<StandardFormResult | null>,
		Readable<TipEntry[]>
	],
	([$state, $messages, $model, $solver, $standard, $tips]): PersistedGuidedState => ({
		currentState: $state,
		messages: $messages,
		model: $model,
		solverResult: $solver,
		standardFormResult: $standard,
		tipsHistory: $tips
	})
);

if (typeof window !== 'undefined') {
	_allGuidedState.subscribe((state) => {
		if (state.currentState === 'SELECT_MODE' && state.messages.length === 0) return;
		try {
			window.sessionStorage.setItem(GUIDED_SESSION_KEY, JSON.stringify(state));
		} catch {
			// sessionStorage lleno o no disponible — falla silenciosa
		}
	});
}
