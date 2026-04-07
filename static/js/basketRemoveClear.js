import { basketUpdateReport } from './basketUpdate.js';
import { getCookie } from './getCookie.js';
import { updateGlobalNav } from './globalNav.js';
import { phNotify, phReportError } from './reportError.js';

const SELECTORS = {
	BASKET_TABLE: '.basket-table',
	REMOVE_BUTTONS: 'button.basket-remove',
	CLEAR_ALL_BUTTON: '#basket_clear',
	TOTAL_DISPLAY: '.basket-total-value'
};

const NODE_BUTTON_ERROR = 'Node is not an HTMLButtonElement or is null';

const MISSING_ID_ERROR = 'Missing data-product-id attribute';

const HEADERS = {
	'Content-Type': 'application/json',
	'X-CSRFToken': getCookie('csrftoken'),
	'X-Requested-With': 'XMLHttpRequest'
};

const ROUTES = {
	REMOVE: '/basket/remove/',
	CLEAR: '/basket/clear/'
};

document.addEventListener('DOMContentLoaded', () => {
	const basketTableRef = document.querySelector(SELECTORS.BASKET_TABLE);
	if (!basketTableRef) return;

	const basketTable = /** @type {HTMLElement} */ (basketTableRef);

	if (!basketTable.dataset.basketCount) {
		phReportError(
			new Error(
				'[DATA_ERROR]: basket-count data attribute not present on basket-table table element.'
			),
			'SYSTEM'
		);
	}

	const serverCount = parseInt(basketTable.dataset.basketCount || '0', 10);

	const removeButtons = document.querySelectorAll(SELECTORS.REMOVE_BUTTONS);

	const clearAllButton = document.querySelector(SELECTORS.CLEAR_ALL_BUTTON);

	// Handshake validation
	const isIntegrityValid = _validateBasketIntegrity(serverCount, removeButtons);

	if (!clearAllButton) {
		phReportError(
			new TypeError(`[DOM_ERROR]: ${SELECTORS.CLEAR_ALL_BUTTON} not found.`)
		);
		return;
	}

	const validClearAllButton = _validateClearAllButton(clearAllButton);

	if (!validClearAllButton) {
		phReportError(
			new TypeError(`[DOM_ERROR]: ${SELECTORS.CLEAR_ALL_BUTTON} null.`)
		);
		return;
	}

	if (!isIntegrityValid) {
		// Disable clear button if validation fails - safety
		if (clearAllButton && clearAllButton instanceof HTMLButtonElement) {
			clearAllButton.disabled = true;
		}
		// Didn't pass validation, immediate return
		return;
	}

	_initialiseBasket(validClearAllButton, removeButtons);
});

/**
 *
 * @param {HTMLButtonElement} validClearAllBtn
 * @param {NodeListOf<Element>} removeButtons
 * @returns
 */
const _initialiseBasket = (validClearAllBtn, removeButtons) => {
	const validatedButtonList = /** @type {NodeListOf<HTMLButtonElement>} */ (
		removeButtons
	);
	_attachRemoveListeners(validatedButtonList);
	_attachClearAll(validClearAllBtn);
};

/**
 *
 * @param {Element} clearAllButton
 * @returns {HTMLButtonElement | null}
 */
const _validateClearAllButton = clearAllButton => {
	if (!(clearAllButton instanceof HTMLButtonElement)) {
		phReportError(
			new Error(
				'[DOM_ERROR]: #basket_clear button not found or is not HTMLButtonElement'
			),
			'SYSTEM'
		);
		return null;
	}
	return clearAllButton;
};

/**
 *
 * @param {number} serverCount
 * @param {NodeListOf<Element>} buttons
 *
 * @returns {boolean}
 */
const _validateBasketIntegrity = (serverCount, buttons) => {
	const browserCount = buttons.length;
	// Case: empty
	// Both report entry, silent return, no need to continue
	if (serverCount === 0 && browserCount === 0) {
		return false;
	}

	// Case: mismatch
	// Immediate exit if values don't match
	if (serverCount !== browserCount) {
		const integrityError = new Error(
			`[VALIDATION_ERROR]: Server reports ${serverCount} items, but Browser found ${browserCount}.`
		);
		phReportError(integrityError, 'SYSTEM');
		return false;
	}

	// Case: attribute validation (deep check)
	// Errors reported in _validateButtonList
	if (!_validateButtonList(buttons)) {
		return false;
	}

	// Case: success
	return true;
};

/**
 *
 * @param {HTMLButtonElement | unknown} button
 * @param {string} key
 * @returns {boolean | Record<string, any>}
 */
const _validateButton = (button, key) => {
	// Return either true or object { [key]:string, error:string }
	if (!(button instanceof HTMLButtonElement)) {
		return {
			[key]: 'Node is not an HTMLButtonElement or is null'
		};
	}

	// Check for required data attribute
	if (
		!button.dataset.productId ||
		typeof button.dataset.productId == 'undefined'
	) {
		return { key: MISSING_ID_ERROR };
	}

	return true;
};

/**
 *
 * @param {NodeListOf<HTMLButtonElement>
 * | NodeListOf<Node>
 * | unknown} buttonList
 * @returns {boolean}
 */
const _validateButtonList = buttonList => {
	if (!(buttonList instanceof NodeList)) {
		return false;
	}

	/** @type {Record<string, any>[]} */
	const validationErrors = [];

	buttonList.forEach((button, key) => {
		const stringKey = key.toString();

		const validOrError = _validateButton(button, stringKey);
		if (validOrError !== true)
			validationErrors.push({ [stringKey]: NODE_BUTTON_ERROR });
	});

	if (validationErrors.length > 0) {
		_handleValidationError(validationErrors);
		return false;
	}

	return true;
};

/**
 *
 * @param {HTMLButtonElement} validClearAllBtn
 *
 */
const _attachClearAll = validClearAllBtn => {
	validClearAllBtn.addEventListener('click', _clearAllHandler);
};

/**
 * Attach remove listener to validated & verified button
 * @param {NodeListOf<HTMLButtonElement>} removeButtons
 */
const _attachRemoveListeners = removeButtons => {
	removeButtons.forEach(button => {
		button.addEventListener('click', e => {
			const productId = /** @type {string} */ (button.dataset.productId);
			_removeHandler(button, productId);
		});
	});
};

/**
 * Generic Promise-based animator for the basket elements
 * @param {HTMLElement} element
 * @param {string} [className='fade-out']
 * @returns {Promise<void>}
 */
const _performAnimationTransition = (element, className = 'fade-out') => {
	return new Promise(resolve => {
		//
		element.classList.add(className);

		/**
		 *
		 * @param {Event} e
		 */
		const onTransitionEnd = e => {
			// Ensure we trigger for only main opacity/transform change
			if (e.target !== element) return;

			element.removeEventListener('transitionend', onTransitionEnd);
			resolve();
		};

		element.addEventListener('transitionend', onTransitionEnd);

		setTimeout(() => {
			element.removeEventListener('transitionend', onTransitionEnd);
			resolve();
		}, 600);
	});
};

/**
 * Purges entire manifest using animation utility
 * @param {Event} event
 */
const _clearAllHandler = async event => {
	//
	const button = /** @type {HTMLButtonElement} */ (event.currentTarget);
	const endpoint = button.dataset.endpoint;
	const tbody = /** @type {HTMLElement} */ (
		document.querySelector('.basket-table tbody')
	);

	if (!endpoint) {
		phReportError(
			new Error(
				'[DOM_ERROR]: data-endpoint attribute not set on clear all button'
			),
			'SYSTEM'
		);
		return;
	}

	if (!tbody || tbody == null) {
		phReportError(
			new Error('[DOM_ERROR]: tbody not found in DOM. Reporting error.'),
			'SYSTEM'
		);
		return;
	}

	try {
		const animation = _performAnimationTransition(tbody, 'manifest-purge');

		const success = await _clearAllBasket(endpoint);

		if (success) {
			await animation;
		}

		window.location.reload();
	} catch (error) {
		tbody.classList.remove('basket-purge');
		button.disabled = false;
		button.classList.remove('busy');
		const err = /** @type {Error} */ (error);
		phReportError(err, 'NETWORK');
	}
};

/**
 *
 * @param {string} endpoint
 * @returns {Promise<boolean>}
 */
const _clearAllBasket = async endpoint => {
	const csrfToken = getCookie('csrftoken');
	if (!csrfToken) {
		phReportError(
			new Error('BASKET_SECURITY_FAILURE: CSRF_TOKEN_NOT_FOUND'),
			'NETWORK'
		);
		return false;
	}

	const response = await fetch(endpoint, {
		method: 'POST',
		headers: {
			'X-CSRFToken': csrfToken,
			'Content-Type': HEADERS['Content-Type']
		}
	});

	if (!response.ok) {
		throw new Error('CLEAR_FAILED: Server rejected basket clear request');
	}

	return true;
};

/**
 * Handles attachment of event listeners to the remove item buttons
 * @param {HTMLButtonElement} button
 * @param {string} productId
 */
const _removeHandler = async (button, productId) => {
	// Define row once
	// Directly manipulate target button reference passed from loop

	const row = /** @type {HTMLTableRowElement | null } */ (button.closest('tr'));
	if (!row) return;

	button.disabled = true;
	button.classList.add('busy');

	try {
		// Start animation and network request in parallel
		// Not awaited: both run concurrently
		const animationPromise = _performAnimationTransition(row, 'fade-out');
		const dataPromise = _removeBasketLine(productId);

		// Wait for data first (ensure server succeeds)

		const response = await dataPromise;

		// Defensively destructure with defaults
		const {
			total_items = 0,
			total_price = '0.00',
			message: serverMessage = 'Action Complete'
		} = response;

		// Update global nav with destructured variables
		updateGlobalNav(total_items, total_price);

		phNotify(serverMessage || 'Item removed from basket', 'success');

		// Wait for animation to finish so row is ready to be removed
		await animationPromise;

		// Row removal
		row.remove();

		// Check remaining rows
		const remainingRows = document.querySelectorAll(SELECTORS.REMOVE_BUTTONS);
		if (remainingRows.length === 0) {
			window.location.reload();
			return;
		}

		// Update total price display
		if (total_price !== undefined && total_price !== null) {
			_updateTotalDisplay(total_price);
		}
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
 * @param {string} totalPrice
 */
const _updateTotalDisplay = totalPrice => {
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
 * @returns {Promise<BasketState>} JSON response containing new total
 */
const _removeBasketLine = async productId => {
	// TODO: Remove deprecated
	// const csrfToken = getCookie('csrftoken');

	// if (!csrfToken) {
	// 	throw new Error('BASKET_SECURITY_FAILURE: CSRF_TOKEN_NOT_FOUND');
	// }

	// const response = await fetch(ROUTES.REMOVE, {
	// 	method: 'POST',
	// 	headers: {
	// 		'Content-Type': HEADERS['Content-Type'],
	// 		'X-CSRFToken': csrfToken
	// 		// 'X-Requested-With': HEADERS['X-Requested-With']
	// 	},
	// 	body: JSON.stringify({ product_id: productId })
	// });

	// if (!response.ok) {
	// 	// Attempt to parse server error message
	// 	const errorBody = await response.json().catch(() => {});
	// 	throw new Error(errorBody.error || `BASKET_HTTP_ERROR: ${response.status}`);
	// }
	// return await response.json();

	// New consuming basketUpdateReport utility.
	// Pass intent directly to basketUpdateReport.
	// Automatically re wraps into Promise<BasketState>.

	return await basketUpdateReport({
		product_id: productId,
		action: 'remove'
	});
};

/**
 *
 * @param {Record<string,any>[]} validationErrors
 */
function _handleValidationError(validationErrors) {
	// Iterate and handle validationErrors
	// FOR NOW - handle in console

	validationErrors.forEach(error => {
		phReportError(new TypeError('[]'));
	});

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
