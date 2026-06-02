<script lang="ts">
	let {
		provider,
		model
	}: {
		provider?: string;
		model?: string;
	} = $props();

	const providerLabels: Record<string, string> = {
		gemini: 'Gemini',
		groq: 'Groq',
		cerebras: 'Cerebras',
		sambanova: 'SambaNova',
		zai: 'Z.ai',
		openrouter: 'OpenRouter',
		deterministic: 'sin LLM'
	};

	function cleanModelName(modelName: string): string {
		if (!modelName) return '';
		
		let clean = modelName;
		if (clean.includes('/')) {
			const parts = clean.split('/');
			if (parts[0] === 'openrouter') {
				clean = parts.slice(1).join('/');
			} else {
				clean = parts[parts.length - 1];
			}
		}

		const modelMap: Record<string, string> = {
			'gemini-3.5-flash': 'Gemini 3.5 Flash',
			'gemini-3.1-flash': 'Gemini 3.1 Flash',
			'gemini-2.5-flash': 'Gemini 2.5 Flash',
			'llama-3.3-70b-versatile': 'Llama 3.3 70B',
			'llama-3.3-70b': 'Llama 3.3 70B',
			'llama-3.1-405b': 'Llama 3.1 405B',
			'glm-4.6': 'GLM-4.6'
		};

		const key = clean.toLowerCase();
		for (const [k, v] of Object.entries(modelMap)) {
			if (key.includes(k.toLowerCase()) || k.toLowerCase().includes(key)) {
				return v;
			}
		}

		// Fallback clean-up
		clean = clean.replace(/-instruct/gi, '')
		             .replace(/:free/gi, '')
		             .replace(/-/g, ' ');
		
		return clean.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
	}

	const display = $derived.by(() => {
		if (provider === 'deterministic') return 'sin LLM';
		if (model) {
			const cleanedModel = cleanModelName(model);
			const provName = provider ? providerLabels[provider] ?? provider : '';
			if (provName && provName.toLowerCase() !== 'openrouter' && !cleanedModel.toLowerCase().includes(provName.toLowerCase())) {
				return `${cleanedModel} (${provName})`;
			}
			return cleanedModel;
		}
		if (provider) {
			const fallbackLabels: Record<string, string> = {
				gemini: 'Gemini 3.5 Flash',
				groq: 'Llama 3.3 70B (Groq)',
				cerebras: 'Llama 3.3 70B (Cerebras)',
				sambanova: 'Llama 3.1 405B (SambaNova)',
				zai: 'GLM-4.6 (Z.ai)',
				openrouter: 'OpenRouter'
			};
			return fallbackLabels[provider] ?? provider;
		}
		return null;
	});

	const isDeterministic = $derived(provider === 'deterministic');
</script>

{#if display}
	<span class="prov" class:det={isDeterministic} title={isDeterministic ? 'Respondido con el matcher determinístico del wiki (sin LLM)' : `Procesado con ${display}`}>
		<span class="rail" aria-hidden="true"></span>
		<span class="lbl">Modelo:</span>
		<span class="name">{display}</span>
	</span>
{/if}

<style>
	.prov {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		font-family: var(--font-mono);
		font-size: 0.65rem;
		color: var(--color-ink-muted);
		opacity: 0.8;
		transition: opacity 0.18s ease;
		padding: 0.18rem 0.5rem 0.18rem 0;
	}

	.prov:hover {
		opacity: 1;
	}

	.rail {
		width: 14px;
		height: 1px;
		background: linear-gradient(
			to right,
			transparent,
			var(--color-primary),
			var(--color-accent)
		);
	}

	.lbl {
		font-style: italic;
		font-family: var(--font-display);
		font-size: 0.7rem;
		letter-spacing: 0;
		text-transform: none;
		color: var(--color-ink-muted);
	}

	.name {
		color: var(--color-ink-light);
		font-weight: 500;
		letter-spacing: 0.02em;
	}

	.prov.det .rail {
		background: linear-gradient(
			to right,
			transparent,
			var(--color-ink-muted)
		);
	}

	.prov.det .name {
		color: var(--color-ink-muted);
		font-style: italic;
		text-transform: none;
		letter-spacing: 0.08em;
	}
</style>
