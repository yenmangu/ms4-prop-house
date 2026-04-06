import { getCookie } from './getCookie.js';
import { updateGlobalNav } from './globalUI.js';

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

				await addToBasket(productId);
			});
		}
	}
};

/**
 * Sends the POST requests to the Django backend
 * @param {string} productId
 */
const addToBasket = async productId => {
	const csrfToken = getCookie('csrftoken');

	if (!csrfToken) {
		throw new TypeError('CSRF token not found. Chek if cookies are enabled.');
	}
	try {
		const response = await fetch(postEndpoint, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': csrfToken
			},
			body: JSON.stringify({ product_id: productId })
		});
		console.log(response);
		if (!response.ok) {
			throw new Error(
				`Failed to add product ${productId} to basket. Status: ${response.status}`
			);
		}
		const data = await response.json();
		console.log('DATA: ', data);

		// Temp console confirmation
		console.log(`Product: ${productId} added to basket!`);
		// Update UI logic
		// Parse response
	} catch (err) {
		throw err;
	}
};

window.addEventListener('DOMContentLoaded', handler);
