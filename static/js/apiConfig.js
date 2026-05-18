import { getCookie } from './getCookie.js';
import { phReportError } from './reportError.js';

export const getStandardHeaders = () => ({
	'Content-Type': 'application/json',
	'X-CSRFToken': getCookie('csrftoken') || '',
	'X-Requested-With': 'XMLHttpRequest'
});

const ENDPOINTS = {
	update: '/basket/update/',
	/**
	 *
	 * @param {string} tierId
	 */
	membership: tierId => {
		return `/accounts/membership/initiate/${tierId}`;
	}
};

/**
 *
 * @param {string} [zone]
 * @param {string|null} [tierId]
 * @returns
 */
export const getLiveEndpoint = (zone = 'basket', tierId = null) => {
	if (zone === 'basket') {
		const wrapper = document.querySelector('.manifest-wrapper');
		const htmlWrapper = /** @type {HTMLElement} */ (wrapper);

		// Fallback to hardcoded string if DOM attribute not found
		return htmlWrapper.dataset.basketUpdateUrl || ENDPOINTS.update;
	}
	if (zone === 'membership' && typeof tierId === 'string') {
		return ENDPOINTS.membership(tierId);
	}
};

/**
 *
 * @param {AllowedAction} action
 * @param {string} [productId]
 * @param {string|number} [quantity=1]
 * @returns {BasketUpdateReport}
 */
export const createBasketUpdatePayload = (action, productId, quantity = 1) => {
	const endpoint = getLiveEndpoint('basket');
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
