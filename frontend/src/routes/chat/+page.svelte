<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { isAuthenticated, clearTokens } from '$lib/api/client';
	import { goto } from '$app/navigation';
	import {
		currentState,
		messages,
		addMessage,
		resetChat,
		STEP_LABELS,
		currentStepIndex,
		STEP_ORDER,
		isGuidedFlow
	} from '$lib/stores/chat';
	import { clearTheory } from '$lib/stores/theory';

	import ChatMessage from '$lib/components/ChatMessage.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import ModelSidebar from '$lib/components/ModelSidebar.svelte';
	import SelectMode from '$lib/components/steps/SelectMode.svelte';
	import InputEnunciado from '$lib/components/steps/InputEnunciado.svelte';
	import DefineObjective from '$lib/components/steps/DefineObjective.svelte';
	import DefineVariables from '$lib/components/steps/DefineVariables.svelte';
	import BuildConstraints from '$lib/components/steps/BuildConstraints.svelte';
	import ValidateModel from '$lib/components/steps/ValidateModel.svelte';
	import ConvertForms from '$lib/components/steps/ConvertForms.svelte';
	import SolveAndGraph from '$lib/components/steps/SolveAndGraph.svelte';
	import Interpret from '$lib/components/steps/Interpret.svelte';
	import TheoryMode from '$lib/components/steps/TheoryMode.svelte';

	let chatContainer: HTMLDivElement;
	let sidebarOpen = $state(true);

	const inTheoryMode = $derived($currentState === 'THEORY_QUERY');

	onMount(() => {
		if (!isAuthenticated()) {
			goto('/login');
			return;
		}
		// Initial greeting
		if ($messages.length === 0) {
			addMessage(
				'assistant',
				'Hola! Soy **Slacko**, tu tutor de Investigación Operativa. ¿Cómo querés trabajar hoy?'
			);
		}
	});

	// Auto-scroll when messages change
	$effect(() => {
		// Subscribe to messages
		const _ = $messages;
		tick().then(() => {
			if (chatContainer) {
				chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
			}
		});
	});

	function logout() {
		clearTokens();
		goto('/login');
	}

	function handleNewChat() {
		clearTheory();
		resetChat();
		addMessage(
			'assistant',
			'Hola! Soy **Slacko**, tu tutor de Investigación Operativa. ¿Cómo querés trabajar hoy?'
		);
	}
</script>

<div class="flex h-screen overflow-hidden bg-surface">
	<!-- Sidebar (only for guided flow) -->
	{#if !inTheoryMode}
		<ModelSidebar open={sidebarOpen} />
	{/if}

	<!-- Main area -->
	<div class="flex-1 flex flex-col min-w-0">
		<!-- Header -->
		<header
			class="bg-surface-card border-b border-bot-border px-6 py-3 flex items-center gap-4 shrink-0"
		>
			{#if !inTheoryMode}
				<button
					onclick={() => (sidebarOpen = !sidebarOpen)}
					class="w-8 h-8 rounded-lg hover:bg-surface-warm flex items-center justify-center
						text-ink-muted hover:text-ink transition-colors cursor-pointer text-sm"
					title={sidebarOpen ? 'Ocultar modelo' : 'Mostrar modelo'}
				>
					{sidebarOpen ? '◀' : '▶'}
				</button>
			{/if}

			<div class="flex-1">
				<div class="flex items-center gap-3">
					<h1 class="font-display text-2xl text-ink">Slacko</h1>
					{#if inTheoryMode}
						<span
							class="text-[0.65rem] tracking-[0.18em] uppercase font-mono text-accent
								bg-accent/8 px-2 py-0.5 rounded-full border border-accent/30"
						>
							Modo teoría
						</span>
					{:else if $isGuidedFlow}
						<span class="text-xs text-ink-muted bg-surface-warm px-2 py-0.5 rounded-full">
							Paso {$currentStepIndex + 1} de {STEP_ORDER.length} — {STEP_LABELS[$currentState]}
						</span>
					{/if}
				</div>
				{#if !inTheoryMode}
					<div class="mt-1.5 max-w-md">
						<ProgressBar />
					</div>
				{/if}
			</div>

			<div class="flex items-center gap-2">
				<button
					onclick={handleNewChat}
					class="text-xs text-ink-muted hover:text-ink px-3 py-1.5 rounded-lg hover:bg-surface-warm
						transition-colors cursor-pointer"
				>
					Nuevo problema
				</button>
				<button
					onclick={logout}
					class="text-xs text-ink-muted hover:text-error px-3 py-1.5 rounded-lg hover:bg-surface-warm
						transition-colors cursor-pointer"
				>
					Salir
				</button>
			</div>
		</header>

		<!-- Body: theory mode takes the whole area, guided flow keeps the chat layout -->
		{#if inTheoryMode}
			<div bind:this={chatContainer} class="flex-1 overflow-y-auto">
				{#key $currentState}
					<TheoryMode />
				{/key}
			</div>
		{:else}
			<div bind:this={chatContainer} class="flex-1 overflow-y-auto">
				<div class="max-w-3xl mx-auto px-6 py-6 space-y-4">
					<!-- Rendered messages -->
					{#each $messages as msg (msg.id)}
						<ChatMessage role={msg.role} content={msg.content} />
					{/each}

					<!-- Current step form -->
					<div class="flex justify-start">
						<div class="max-w-[85%] w-full">
							{#key $currentState}
								{#if $currentState === 'SELECT_MODE'}
									<SelectMode />
								{:else if $currentState === 'INPUT_ENUNCIADO'}
									<InputEnunciado />
								{:else if $currentState === 'DEFINE_OBJECTIVE'}
									<DefineObjective />
								{:else if $currentState === 'DEFINE_VARIABLES'}
									<DefineVariables />
								{:else if $currentState === 'BUILD_CONSTRAINTS'}
									<BuildConstraints />
								{:else if $currentState === 'VALIDATE_MODEL'}
									<ValidateModel />
								{:else if $currentState === 'CONVERT_FORMS'}
									<ConvertForms />
								{:else if $currentState === 'SOLVE_AND_GRAPH'}
									<SolveAndGraph />
								{:else if $currentState === 'INTERPRET'}
									<Interpret />
								{/if}
							{/key}
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
