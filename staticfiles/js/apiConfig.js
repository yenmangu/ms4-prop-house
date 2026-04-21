import { getCookie } from './getCookie.js';
import { phReportError } from './reportError.js';

export const getStandardHeaders = () => ({
	'Content-Type': 'application/json',
	'X-CSRFToken': getCookie('csrftoken') || '',
	'X-Requested-With': 'XMLHttpRequest'
});

const ENDPOINTS = {
	update: '/basket/update/'
};

const getLiveEndpoint = () => {
	const wrapper = document.querySelector('.manifest-wrapper');
	const htmlWrapper = /** @type {HTMLElement} */ (wrapper);

	// Fallback to hardcoded string if DOM attribute not found
	return htmlWrapper.dataset.basketUpdateUrl || ENDPOINTS.update;
};

/**
 *
 * @param {AllowedAction} action
 * @param {string} [productId]
 * @param {string|number} [quantity=1]
 * @returns {BasketUpdateReport}
 */
export const createBasketUpdatePayload = (action, productId, quantity = 1) => {
	const endpoint = getLiveEndpoint();
	if (!endpoint) {
		throw new Error('[CONFIG_ERROR]: Basket update endpoint is not defined.');
	}
	return {
		action,
		product_id: productId,
		quantity:
			typeof quantity === 'number' ? quantity : parseInt(quantity, 10) || 1,
		endpoint: endpoint
	};
};
