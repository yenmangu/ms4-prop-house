/**
 * @typedef {Object} ToastDetail
 * @property {string} message
 * @property {'success'|'danger'|'warning'|'info'} status
 */
import { attachPaymentListener, mountStripeElements } from './checkout.js';
import { intialiseCustomerForm } from './customerForm.js';
import { getToastElements } from './domElements.js';
import { phReportError } from './reportError.js';
import { handleSidebar } from './sidebarOffcanvas.js';
import { getStatusHandlerResult } from './statusHandler.js';
import {
	showToast,
	showPaymentToast,
	showCustomerDetailsToast,
	listenForClose
} from './toast.js';

/**
 * @typedef {CustomEvent<ToastDetail>} ToastEvent
 */

export const initialiseHtmxListeners = () => {
	document.addEventListener('showToast', handleToastEvent);
	document.addEventListener('htmx:afterRequest', checkoutListener);
	document.addEventListener('htmx:beforeProcess', handleSidebar);
};

/**
 *
 * @param {Event} evt
 */
function handleToastEvent(evt) {
	const toastEvt = /** @type {ToastEvent} */ (evt);
	const { message, status } = toastEvt.detail;
	const toastElements = getToastElements();
	if (toastElements) {
		showToast(toastElements, message, status);
	}
}

/**
 *
 * @param {number} statusCode
 * @param {ToastElements} toastUI
 * @param {boolean}[successful = true]
 * @returns {boolean}
 */
const handleStatus = (statusCode, toastUI, successful = true) => {
	const statusHandlerResult = getStatusHandlerResult(statusCode);
	if (statusHandlerResult) {
		showToast(toastUI, statusHandlerResult.message, statusHandlerResult.status);
		return true;
	}
	if (!successful) {
		showToast(
			toastUI,
			'Please try again. Contact support if this persists.',
			'danger'
		);
		return true;
	}
	return false;
};

/**
 * Handles multi-stage checkout flow within the toast
 *
 * @param {Event} evt
 */
async function checkoutListener(evt) {
	const event = /** @type {AfterRequestEvent} */ (evt);
	const { detail } = event;
	const toastUI = getToastElements();

	if (!toastUI) {
		phReportError('[DOM_ERROR]: Toast Elements not found in DOM');
		return;
	}

	// Status check
	const responseCode = detail.xhr.status;

	const statusHandled = handleStatus(responseCode, toastUI, detail.successful);
	if (statusHandled) {
		return;
	}

	// Stage 1
	// Contact form injection
	if (detail.elt.id === 'open-checkout') {
		const checkoutBtn = /** @type {HTMLButtonElement} */ (detail.elt);

		// Disable the checkout button
		checkoutBtn.disabled = true;
		checkoutBtn.classList.add('opacity-50');

		toastUI.titleElement.innerText = '_01: Contact Information';
		toastUI.bodyElement.innerHTML = detail.xhr.responseText;

		// @ts-ignore
		if (window.htmx) {
			// @ts-ignore
			window.htmx.process(toastUI.bodyElement);
		} else {
			console.error('[SYSTEM_ERROR]: HTMX not found on window object');
		}

		// Re-initialise customer form
		intialiseCustomerForm();
		// Show customer details toast
		showCustomerDetailsToast(toastUI);

		toastUI.toastElement.addEventListener(
			'hidden.bs.toast',
			() => {
				checkoutBtn.disabled = false;
				checkoutBtn.classList.remove('opacity-50');
			},
			{ once: true }
		);
	}

	// Stage 2
	// Stripe Handshake (from create-intent)
	if (detail.elt.id && detail.elt.id.startsWith('create-intent')) {
		const submitBtn = /** @type {HTMLButtonElement} */ (
			detail.elt.querySelector('button[type="submit"]')
		);

		// Lock button and provide UX

		let originalSubmitContent = '';
		if (submitBtn) {
			originalSubmitContent = submitBtn.innerHTML.trim();
			submitBtn.disabled = true;
			submitBtn.innerHTML = 'Initialising secure payment portal...';
		}

		const response = JSON.parse(detail.xhr.responseText);

		const { clientSecret, stripePk } = response;
		try {
			const closePromise = listenForClose(toastUI.toastElement);

			const paymentUI = await showPaymentToast(toastUI, clientSecret);

			if (!paymentUI) return;

			const stripeInstance = await mountStripeElements(
				stripePk,
				clientSecret,
				paymentUI
			);

			// Typesafe and gated tierId assignment
			let tierId;

			/** @type {SubscriptionIntentMetadata} */
			let metadata = {};

			const element = /** @type {HTMLElement} */ (detail.elt);
			if (element.dataset && element.dataset.tier) {
				tierId = element.dataset.tier;
				metadata.tierId = tierId;
				metadata.toastInstance = paymentUI.toastInstance
					? paymentUI.toastInstance
					: undefined;
			}

			if (stripeInstance && paymentUI.form) {
				const { stripe, elements } = stripeInstance;

				attachPaymentListener(
					stripe,
					elements,
					paymentUI.form,
					clientSecret,
					metadata
				);
			}

			closePromise.then(isClosed => {
				if (!isClosed || !submitBtn) {
					return;
				}
				submitBtn.disabled = false;
				submitBtn.innerHTML = originalSubmitContent;
			});
		} catch (err) {
			if (submitBtn) {
				submitBtn.innerHTML = originalSubmitContent;
				submitBtn.disabled = false;
			}
			const msg = err instanceof Error ? err.message : 'Handshake failed.';
			if (err instanceof Error) {
				console.error(err);
				phReportError(new Error(msg), 'SYSTEM');
			}

			showToast(
				toastUI,
				`Error: ${msg}. Contact support if this persists.`,
				'danger'
			);
		}
	}
}
