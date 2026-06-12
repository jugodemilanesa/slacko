/**
 * Acción Svelte para revelar un elemento cuando entra en viewport.
 * Agrega la clase `is-visible` (escalonable con `data-reveal-delay`).
 *
 * Uso:  <div class="reveal" use:reveal>...</div>
 *       <div class="reveal" use:reveal style="--reveal-delay: 120ms">...</div>
 */
export function reveal(node: HTMLElement, options: { once?: boolean } = {}) {
	const once = options.once ?? true;

	if (typeof IntersectionObserver === 'undefined') {
		node.classList.add('is-visible');
		return {};
	}

	const observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					node.classList.add('is-visible');
					if (once) observer.unobserve(node);
				} else if (!once) {
					node.classList.remove('is-visible');
				}
			}
		},
		{ threshold: 0.18, rootMargin: '0px 0px -8% 0px' }
	);

	observer.observe(node);
	return {
		destroy() {
			observer.disconnect();
		}
	};
}
