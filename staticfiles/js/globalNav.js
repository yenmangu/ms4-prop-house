/**
 * Synchronise global ui basket element with new basket data
 * @param {number} totalItems
 * @param {string} totalPrice
 */
const updateGlobalNav = (totalItems, totalPrice) => {
	const countBadge = /** @type {HTMLElement} */ (
		document.querySelector('#nav-basket-count')
	);

	const totalDisplay = /** @type {HTMLElement} */ (
		document.querySelector('#nav-basket-total')
	);

	if (countBadge) {
		countBadge.innerText = totalItems.toString();
		countBadge.classList.toggle('hidden', totalItems === 0);
	}

	if (totalDisplay && totalPrice) {
		totalDisplay.innerText = `${totalPrice}`;
	}
};

export { updateGlobalNav };
