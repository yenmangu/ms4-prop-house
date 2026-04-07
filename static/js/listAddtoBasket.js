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
	// TODO: Deprecated thanks to new basketUpdateReport module

	// const csrfToken = getCookie('csrftoken');

	// if (!csrfToken) {
	// 	throw new TypeError('CSRF token not found. Chek if cookies are enabled.');
	// }

	try {
		const data = await basketUpdateReport({
			product_id: productId,
			action: 'add'
		});

		// TODO: Remove deprecated

		// const response = await fetch(postEndpoint, {
		// 	method: 'POST',
		// 	headers: {
		// 		'Content-Type': 'application/json',
		// 		'X-CSRFToken': csrfToken
		// 	},
		// 	body: JSON.stringify({ product_id: productId })
		// });

		// if (!response.ok) {
		// 	const errorBody = await response.json().catch(() => {});
		// 	throw new Error(
		// 		errorBody?.error ||
		// 			`Failed to add product ${productId} to basket. Status: ${response.status}`
		// 	);
		// }

		// Temp console confirmation
		// console.log(`Product: ${productId} added to basket!`);

		// /** @type {BasketState} */
		// const {
		// 	total_items = 0,
		// 	total_price = '0.00',
		// 	message: serverMessage = 'Item added to basket'
		// } = await response.json();

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
