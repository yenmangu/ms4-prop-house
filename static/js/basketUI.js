/**
 *
 * @param {HTMLElement} element
 * @param {string} className
 * @returns {Promise<void>}
 */
export const performAnimation = (element, className) => {
	const DEBUG = false;
	let debugId = '';
	/**
	 * Explicitly typed for Browser Web API
	 * @type {number | null}
	 */
	let safetyTimer = null;

	// Debug animation
	if (DEBUG) {
		debugId = `ANIMATION_DEBUG_${element.dataset.unit || 'target'}`;
		console.time(debugId);
		console.log(`[${debugId}] Starting transition at:`, performance.now());
	}

	return new Promise(resolve => {
		element.classList.add(className);

		/**
		 *
		 * @param {TransitionEvent} e
		 */
		const onTransitionEnd = e => {
			if (e.currentTarget !== element) return;
			element.removeEventListener('transitionend', onTransitionEnd);
			if (safetyTimer) clearTimeout(safetyTimer);

			if (DEBUG) {
				console.log(`[${debugId}] transitionend event fired.`);
				console.timeEnd(debugId);
			}

			resolve();
		};

		element.addEventListener('transitionend', onTransitionEnd);
		// Specify window.setTimeout function, not NodeJS
		safetyTimer = window.setTimeout(() => {
			if (DEBUG) {
				console.warn(
					`[${debugId}] Safety timeout reached. Transition may have failed or snapped.`
				);
				console.timeEnd(debugId);
				resolve();
			}
		}, 1200);
		element.classList.add(className);
	});
};
