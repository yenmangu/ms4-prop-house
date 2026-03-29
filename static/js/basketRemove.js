import { getCookie } from './getCookie.js';
import { phReportError } from './reportError.js';

const removeButtons = document.querySelectorAll('button.basket-remove');

const REMOVE_ROUTE = '/basket/remove/';

/**
 * Handles attachment of event listeners to the remove item buttons
 * @param {HTMLButtonElement} button
 * @param {string} productId
 */
const handler = async (button, productId) => {
	// Define row once
	// Directly manipulate target button reference passed from loop

	const row = /** @type {HTMLTableRowElement | null } */ (button.closest('tr'));

	button.disabled = true;
	button.classList.add('busy');

	// Start animation object
	/** @type {Promise<boolean|null|void>} */
	let animationPromise = Promise.resolve(null);

	try {
		// Dynamically update product table
		if (row) {
			animationPromise = handleAnimation(row);
		}

		const data = await removeBasketLine(productId);

		await animationPromise;

		if (data.total_price === undefined || data.total_price === null) {
			throw new Error(`BASKET_DATA_ERROR: missing total_price`);
		}

		updateTotalDisplay(data.total_price);
	} catch (error) {
		if (row) {
			row.classList.remove('fade-out');
		}
		button.disabled = false;
		button.classList.remove('busy');
		const err = /** @type {Error} */ (error);
		phReportError(err, 'NETWORK');
	}
};

/**
 *
 * @param {HTMLTableRowElement} row
 * @returns {Promise<boolean|null>}
 */
const handleAnimation = async row => {
	return new Promise((resolve, reject) => {
		row.classList.add('fade-out');
		row.addEventListener(
			'transitionend',
			() => {
				row.remove();
				const remainingRows = document.querySelectorAll(
					'table.basket-table tbody tr'
				);
				if (remainingRows.length === 0) {
					window.location.reload();
				}
				resolve(true);
			},
			{ once: true }
		);

		// Safety timeout
		// If css fails to load - prevent promise from hanging forever
		setTimeout(() => resolve(false), 1000);
	});
};

/**
 *
 * @param {string} totalPrice
 */
const updateTotalDisplay = totalPrice => {
	const totalDisplay = document.querySelector('.basket-total-value');
	if (!(totalDisplay instanceof HTMLElement)) {
		throw new Error(`DOM_ERROR: ${totalDisplay} not HTMLElement`);
	}
	if (totalDisplay && totalPrice !== undefined) {
		totalDisplay.innerText = totalPrice;
	}
};

/**
 * Communicates with the Django backend to de-register a unit from the basket
 *
 * @param {string} productId
 * @returns {Promise<Record<string, any>>} JSON response containing new total
 */
const removeBasketLine = async productId => {
	const csrfToken = getCookie('csrftoken');

	if (!csrfToken) {
		throw new Error('BASKET_SECURITY_FAILURE: CSRF_TOKEN_NOT_FOUND');
	}

	const response = await fetch(REMOVE_ROUTE, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrfToken,
			'X-Requested-With': 'XMLHttpRequest'
		},
		body: JSON.stringify({ product_id: productId })
	});

	if (!response.ok) {
		// Attempt to parse server error message
		const errorBody = await response.json().catch(() => {});
		throw new Error(errorBody.error || `BASKET_HTTP_ERROR: ${response.status}`);
	}
	return await response.json();
};

document.addEventListener('DOMContentLoaded', () => {
	if (!(removeButtons instanceof NodeList) || !removeButtons) {
		throw new TypeError('Remove buttons not found or not configured correctly');
	}
	/** @type {Record<string, any>[]} */
	const validationErrors = [];

	removeButtons.forEach((button, key) => {
		const stringKey = key.toString();
		// Validate the buttons before attempting to attach listeners
		if (!(button instanceof HTMLButtonElement)) {
			validationErrors.push({
				[stringKey]: 'Node is not an HTMLButtonElement or is null'
			});
			return;
		}

		// Check for required data attribute
		if (
			!button.dataset.productId ||
			typeof button.dataset.productId == 'undefined'
		) {
			validationErrors.push({
				[stringKey]: 'Missing data-product-id attribute'
			});
			return;
		}

		// Only attach listeners if validation passes

		button.addEventListener('click', e => {
			const productId = /** @type {string} */ (button.dataset.productId);
			handler(button, productId);
		});
	});

	// Act on any gathered errors
	if (validationErrors.length > 0) {
		handleValidationError(validationErrors);
	}
});

/**
 *
 * @param {Record<string,any>[]} validationErrors
 */
function handleValidationError(validationErrors) {
	// Iterate and handle validationErrors
	// FOR NOW - handle in console
	console.group(
		'%c [BASKET_SYSTEM_INITIALISATION_ERROR] ',
		'color: #ff3333; font-weight: bold; background: #222222'
	);
	validationErrors.forEach(e => {
		const key = Object.keys(e)[0];
		console.warn(`NodeIndex [${key}]: ${e[key]}`);
	});
	console.groupEnd();
}
