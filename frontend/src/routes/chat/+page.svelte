<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { isAuthenticated, clearTokens } from '$lib/api/client';
	import { goto } from '$app/navigation';
	import {
		currentState,
		messages,
		addMessage,
		sendAssistantMessage,
		assistantThinking,
		resetChat,
		restoreGuidedState,
		STEP_LABELS,
		currentStepIndex,
		STEP_ORDER,
		isGuidedFlow
	} from '$lib/stores/chat';
	import { clearTheory } from '$lib/stores/theory';
	import { isDarkMode, toggleDarkMode } from '$lib/stores/theme';

	import ChatMessage from '$lib/components/ChatMessage.svelte';
	import TypingIndicator from '$lib/components/TypingIndicator.svelte';
	import ProgressBar from '$lib/components/ProgressBar.svelte';
	import ModelSidebar from '$lib/components/ModelSidebar.svelte';
	import TipsHistoryPanel from '$lib/components/TipsHistoryPanel.svelte';
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
	import TutorialMode from '$lib/components/steps/TutorialMode.svelte';
	import LLMChatMode from '$lib/components/steps/LLMChatMode.svelte';

	let chatContainer: HTMLDivElement;
	let sidebarOpen = $state(false);

	let typedTitle = $state('');

	$effect(() => {
		if ($currentState === 'SELECT_MODE') {
			typedTitle = '';

			function generateTypingFrames() {
				const target = 'Slacko';
				const frames: { text: string; delay: number }[] = [];
				
				// 30% chance of typing it perfectly without any typos
				const shouldMakeTypo = Math.random() < 0.7;
				
				if (!shouldMakeTypo) {
					let currentText = '';
					for (let i = 0; i < target.length; i++) {
						currentText += target[i];
						frames.push({
							text: currentText,
							delay: 70 + Math.random() * 70 // Faster speed when there are no typos
						});
					}
					return frames;
				}
				
				// Choose a random index for the typo: 2 ('a'), 3 ('c'), or 4 ('k')
				const typoIndex = 2 + Math.floor(Math.random() * 3);
				
				// Extra letters typed before realizing: 0 (immediate), 1, or 2 extra letters
				const rand = Math.random();
				const extraLettersCount = rand < 0.4 ? 0 : (rand < 0.8 ? 1 : 2);
				
				const typosMap: Record<number, string> = {
					2: 's', // Sla -> Sls
					3: 'x', // Slac -> Slax
					4: 'j'  // Slack -> Slacj
				};
				const wrongChar = typosMap[typoIndex] || 'x';
				
				let currentText = '';
				
				// 1. Type normally up to the typo index (original slower speed)
				for (let i = 0; i < typoIndex; i++) {
					currentText += target[i];
					frames.push({
						text: currentText,
						delay: 120 + Math.random() * 100
					});
				}
				
				// 2. Type the typo letter (original slower speed)
				currentText += wrongChar;
				frames.push({
					text: currentText,
					delay: 100 + Math.random() * 100
				});
				
				// 3. Type extra letters thinking it was correct (original slower speed)
				for (let j = 0; j < extraLettersCount; j++) {
					const nextCharIndex = typoIndex + 1 + j;
					if (nextCharIndex < target.length) {
						currentText += target[nextCharIndex];
						frames.push({
							text: currentText,
							delay: 110 + Math.random() * 90
						});
					}
				}
				
				// 4. Pause before realizing the mistake (original slower speed)
				if (frames.length > 0) {
					frames[frames.length - 1].delay = 450 + Math.random() * 150;
				}
				
				// 5. Backspace the wrong characters (original slower speed)
				const charsToDelete = currentText.length - typoIndex;
				for (let d = 0; d < charsToDelete; d++) {
					currentText = currentText.slice(0, -1);
					frames.push({
						text: currentText,
						delay: 80 + Math.random() * 60 // backspace is fast
					});
				}
				
				// 6. Pause before typing the correct letters (original slower speed)
				if (frames.length > 0) {
					frames[frames.length - 1].delay = 350 + Math.random() * 150;
				}
				
				// 7. Finish typing the rest of the word correctly (faster speed once corrected!)
				for (let i = typoIndex; i < target.length; i++) {
					currentText += target[i];
					frames.push({
						text: currentText,
						delay: 70 + Math.random() * 70
					});
				}
				
				return frames;
			}

			const frames = generateTypingFrames();
			let frameIndex = 0;
			let timeoutId: ReturnType<typeof setTimeout>;

			function typeNextFrame() {
				if (frameIndex < frames.length) {
					const currentFrame = frames[frameIndex];
					typedTitle = currentFrame.text;
					const nextDelay = currentFrame.delay;
					frameIndex++;
					timeoutId = setTimeout(typeNextFrame, nextDelay);
				}
			}

			// Start with an initial delay to feel like the page has loaded first
			timeoutId = setTimeout(typeNextFrame, 200 + Math.random() * 150);

			return () => clearTimeout(timeoutId);
		}
	});

	const inTheoryMode = $derived($currentState === 'THEORY_QUERY');
	const inTutorialMode = $derived($currentState === 'TUTORIAL');
	const inLLMChatMode = $derived($currentState === 'LLM_CHAT');
	const inFullMode = $derived(inTheoryMode || inTutorialMode || inLLMChatMode);

	onMount(() => {
		if (!isAuthenticated()) {
			goto('/login');
			return;
		}
		const restored = restoreGuidedState();
		if (!restored && $messages.length === 0) {
			sendAssistantMessage(
				'Hola! Soy **Slacko**, tu tutor de Programación Lineal. ¿Cómo querés trabajar hoy?',
				{ delay: 600, expression: 'happy' }
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
		sendAssistantMessage(
			'Hola! Soy **Slacko**, tu tutor de Programación Lineal. ¿Cómo querés trabajar hoy?',
			{ delay: 600, expression: 'happy' }
		);
	}
</script>

<div class="flex h-screen overflow-hidden bg-surface">
	<!-- Sidebar (only for guided flow) -->
	{#if !inFullMode && $currentState !== 'SELECT_MODE'}
		<ModelSidebar open={sidebarOpen} />
	{/if}

	<div class="flex flex-col flex-1 min-w-0">
		<!-- Header (full width at top) -->
		<header
			class="relative bg-surface-card border-b border-bot-border px-6 flex items-center justify-between shrink-0 h-[76px]"
		>
			<!-- Left side: sidebar toggle + Slacko title + badges -->
			<div class="flex items-center gap-4">
				{#if !inFullMode && $currentState !== 'SELECT_MODE'}
					<button
						onclick={() => (sidebarOpen = !sidebarOpen)}
						class="w-8 h-8 rounded-lg hover:bg-surface-warm flex items-center justify-center
							text-ink-muted hover:text-ink transition-colors cursor-pointer text-sm"
						title={sidebarOpen ? 'Ocultar modelo' : 'Mostrar modelo'}
					>
						{sidebarOpen ? '◀' : '▶'}
					</button>
				{/if}

				<div class="flex items-center gap-3">
					<h1 class="font-display text-2xl text-ink">Slacko</h1>
					{#if inTheoryMode}
						<span
							class="text-[0.65rem] tracking-[0.18em] uppercase font-mono text-accent
								bg-accent/8 px-2 py-0.5 rounded-full border border-accent/30"
						>
							Modo teoría
						</span>
					{:else if inTutorialMode}
						<span
							class="text-[0.65rem] tracking-[0.18em] uppercase font-mono text-ink
								bg-ink/8 px-2 py-0.5 rounded-full border border-ink/30"
						>
							Tutorial
						</span>
					{:else if inLLMChatMode}
						<span
							class="llm-chip-badge text-[0.65rem] tracking-[0.18em] uppercase font-mono px-2 py-0.5 rounded-full"
						>
							Chat con IA
						</span>
					{:else if $isGuidedFlow && $currentState !== 'SELECT_MODE'}
						<span class="text-xs text-ink-muted bg-surface-warm px-2 py-0.5 rounded-full">
							Paso {$currentStepIndex + 1} de {STEP_ORDER.length} — {STEP_LABELS[$currentState]}
						</span>
					{/if}
				</div>
			</div>

			<!-- Right side: action buttons -->
			<div class="flex items-center gap-2">
				<button
					onclick={toggleDarkMode}
					class="w-8 h-8 rounded-lg hover:bg-surface-warm flex items-center justify-center
						text-ink-muted hover:text-ink transition-colors cursor-pointer"
					title={$isDarkMode ? 'Modo claro' : 'Modo oscuro'}
				>
					{#if $isDarkMode}
						<!-- Sun icon -->
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
					{:else}
						<!-- Moon icon -->
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
					{/if}
				</button>
				<button
					onclick={handleNewChat}
					class="text-xs text-ink-muted hover:text-ink px-3 py-1.5 rounded-lg hover:bg-surface-warm
						transition-colors cursor-pointer"
				>
					Menú principal
				</button>
				<button
					onclick={logout}
					class="text-xs text-ink-muted hover:text-error px-3 py-1.5 rounded-lg hover:bg-surface-warm
						transition-colors cursor-pointer"
				>
					Salir
				</button>
			</div>

			<!-- ProgressBar absolutely positioned at the bottom of the header (only in guided flow) -->
			{#if !inFullMode && $currentState !== 'SELECT_MODE'}
				<div class="absolute bottom-2 left-6 max-w-md w-[calc(100%-3rem)]">
					<ProgressBar />
				</div>
			{/if}
		</header>

		<!-- Below header: theory/tutorial full-width, guided flow with tips panel al costado -->
		<div class="flex flex-1 min-h-0">
			{#if inTheoryMode}
				<div bind:this={chatContainer} class="flex-1 overflow-y-auto">
					{#key $currentState}
						<TheoryMode />
					{/key}
				</div>
			{:else if inTutorialMode}
				<div bind:this={chatContainer} class="flex-1 overflow-y-auto">
					{#key $currentState}
						<TutorialMode />
					{/key}
				</div>
			{:else if inLLMChatMode}
				<div bind:this={chatContainer} class="flex-1 overflow-y-auto">
					{#key $currentState}
						<LLMChatMode />
					{/key}
				</div>
			{:else}
				<div bind:this={chatContainer} id="chat-container" class="relative flex-1 overflow-y-auto">
					<div class="px-6 py-6 space-y-4 {$currentState === 'SELECT_MODE' ? 'min-h-full flex flex-col justify-center' : ''}">
						{#if $currentState === 'SELECT_MODE'}
							<!-- Background Image at the top of the main menu with a gradient fading to the page background (crossfaded between themes) -->
							<div class="absolute top-0 left-0 right-0 h-[420px] pointer-events-none select-none z-0 overflow-hidden">
								<!-- Light mode background (static base) -->
								<div class="absolute inset-0">
									<img src="/background.jpg" alt="" class="w-full h-full object-cover object-top opacity-35" />
									<div class="absolute inset-0" style="background: linear-gradient(to bottom, transparent 0%, transparent 40%, #faf9f7 100%);"></div>
								</div>
								
								<!-- Dark mode background (transitions on top) -->
								<div class="absolute inset-0 bg-crossfade-container {$isDarkMode ? 'opacity-100' : 'opacity-0'}">
									<img src="/background-dark.jpg" alt="" class="w-full h-full object-cover object-top opacity-35" />
									<div class="absolute inset-0" style="background: linear-gradient(to bottom, transparent 0%, transparent 40%, #0b0b14 100%);"></div>
								</div>
							</div>

							<div class="relative z-10 text-center mb-6 select-none">
								<h1 class="relative inline-block font-display text-5xl md:text-6xl text-ink tracking-tight font-normal">
									{typedTitle}<span class="cursor-blink"></span>
								</h1>
								<p class="text-[0.65rem] tracking-[0.25em] uppercase font-mono mt-2 {$isDarkMode ? 'text-accent' : 'text-primary'}">
									TUTOR DE PROGRAMACIÓN LINEAL
								</p>
							</div>

							<!-- Container with fixed height to keep title/subtitle in final stable positions (responsive alignment) -->
							<div class="relative z-10 h-[96px] flex items-end justify-center shrink-0">
								<div class="w-full max-w-[90vw] md:max-w-4xl lg:max-w-5xl flex justify-start">
									{#each $messages as msg (msg.id)}
										<ChatMessage role={msg.role} content={msg.content} expression={msg.expression} step={msg.step} />
									{/each}

									{#if $assistantThinking}
										<TypingIndicator />
									{/if}
								</div>
							</div>
						{:else}
							<!-- Rendered messages (con expresión por mensaje) -->
							{#each $messages as msg (msg.id)}
								<ChatMessage role={msg.role} content={msg.content} expression={msg.expression} step={msg.step} />
							{/each}

							<!-- Indicador de tipeo mientras Slacko 'piensa' -->
							{#if $assistantThinking}
								<TypingIndicator />
							{/if}
						{/if}

						<!-- Paso activo (queda al final; los pasos anteriores quedan trazados
							 en los divisores y mensajes del scroll) -->
						<div class="relative z-10 flex {$currentState === 'SELECT_MODE' ? 'justify-center' : 'justify-start'}">
							<div class="{$currentState === 'SELECT_MODE' ? 'max-w-md mt-8' : 'max-w-[85%]'} w-full">
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

			{#if !inFullMode && $currentState !== 'SELECT_MODE'}
				<TipsHistoryPanel />
			{/if}
		</div>
	</div>
</div>

<style>
	.llm-chip-badge {
		position: relative;
		background: var(--color-surface-card);
		color: var(--color-ink);
		border: 1px solid transparent;
	}
	.llm-chip-badge::before {
		content: '';
		position: absolute;
		inset: -1px;
		border-radius: 9999px;
		padding: 1px;
		background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
		-webkit-mask:
			linear-gradient(#000 0 0) content-box,
			linear-gradient(#000 0 0);
		mask:
			linear-gradient(#000 0 0) content-box,
			linear-gradient(#000 0 0);
		-webkit-mask-composite: xor;
		mask-composite: exclude;
		pointer-events: none;
	}

	.cursor-blink {
		position: absolute;
		display: inline-block;
		width: 0.28em;
		height: 2px;
		background-color: var(--color-primary);
		bottom: 0.15em;
		margin-left: 0.08em;
		animation: blink 1.8s step-end infinite;
	}

	:global(.dark) .cursor-blink {
		background-color: var(--color-accent);
	}


	@keyframes blink {
		from, to {
			opacity: 1;
		}
		50% {
			opacity: 0;
		}
	}
</style>
