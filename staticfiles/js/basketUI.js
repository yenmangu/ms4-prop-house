/**
 *
 * @param {HTMLElement} element
 * @param {string} className
 * @returns {Promise<void>}
 */
export const performAnimation = (element, className) => {
	return new Promise(resolve => {
		element.classList.add(className);

		/**
		 *
		 * @param {TransitionEvent} e
		 */
		const onTransitionEnd = e => {
			if (e.currentTarget !== element) return;
			element.removeEventListener('transitionend', onTransitionEnd);
			resolve();
		};

		element.addEventListener('transitionend', onTransitionEnd);

		setTimeout(resolve, 600);
	});
};

/**
 *
 * @param {BasketState} state
 */
export const updateBasketDOM = state => {
	const { total_items, total_price } = state;
	const totalDisplay = document.querySelector('.basket-total-value');
	if (totalDisplay instanceof HTMLElement) {
		totalDisplay.innerText = total_price;
	}

	if (total_items === 0) {
		window.location.reload();
	}
};
