import { createBasketUpdatePayload } from './apiConfig.js';
import { basketUpdateReport } from './basketUpdate.js';
import { getCookie } from './getCookie.js';
import { updateGlobalNav } from './globalNav.js';
import { phNotify, phReportError } from './reportError.js';

const addButtons = document.querySelectorAll('button.add-to-basket');

const postEndpoint = '/basket/add/';

/**
 * Handles the attachment of click events to all 'Add' buttons
 */
const handler = async () => {
	for (const button of addButtons) {
		if (button instanceof HTMLButtonElement) {
			// Add click handler

			button.addEventListener('click', async e => {
				e.preventDefault();
				const productId = button.dataset.productId;

				if (!productId) {
					throw new Error('Product Id data attribute not present');
				}

				await _addToBasket(productId);
			});
		}
	}
};

/**
 * Sends the POST requests to the Django backend
 * @param {string} productId
 */
const _addToBasket = async productId => {
	try {
		// Use payload creator
		const payload = createBasketUpdatePayload('add', productId);

		const data = await basketUpdateReport(payload);

		// Update UI logic
		updateGlobalNav(data.total_items, data.total_price);
		phNotify(data.message, 'success');
	} catch (err) {
		if (err instanceof Error) {
			phReportError(err, 'NETWORK');
		}
		throw err;
	}
};

window.addEventListener('DOMContentLoaded', handler);

export { _addToBasket };
