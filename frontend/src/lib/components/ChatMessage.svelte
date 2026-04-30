<script lang="ts">
	let { role, content }: { role: 'assistant' | 'user'; content: string } = $props();
</script>

<div class="flex {role === 'user' ? 'justify-end' : 'justify-start'} fade-in">
	<div
		class="max-w-[75%] px-5 py-3 rounded-2xl leading-relaxed text-[0.95rem]
			{role === 'user'
			? 'bg-primary text-user-text rounded-br-md'
			: 'bg-bot-bg border border-bot-border text-ink rounded-bl-md shadow-sm'}"
	>
		{@html content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')}
	</div>
</div>
