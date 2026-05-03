/**
 * @typedef {Object} ToastDetail
 * @property {string} message
 * @property {'success'|'danger'|'warning'|'info'} status
 */

import { attachPaymentListener, mountStripeElements } from './checkout.js';
import { intialiseCustomerForm } from './customerForm.js';
import { getToastElements } from './domElements.js';
import {
	showToast,
	showPaymentToast,
	showCustomerDetailsToast
} from './toast.js';

/**
 * @typedef {CustomEvent<ToastDetail>} ToastEvent
 */

export const initialiseHtmxListeners = () => {
	document.addEventListener('showToast', handleToastEvent);
	document.addEventListener('htmx:afterRequest', checkoutListener);
};

/**
 *
 * @param {Event} evt
 */
function handleToastEvent(evt) {
	const toastEvt = /** @type {ToastEvent} */ (evt);
	const { message, status } = toastEvt.detail;
	console.log('SHOW TOAST');
	const toastElements = getToastElements();
	if (toastElements) {
		showToast(toastElements, message, status);
	}
}

/**
 * Handles multi-stage checkout flow within the toast
 *
 * @param {Event} evt
 */
async function checkoutListener(evt) {
	const event = /** @type {AfterRequestEvent} */ (evt);
	const { detail } = event;
	const toastElements = getToastElements();

	if (!toastElements) {
		reportError('[DOM_ERROR]: Toast Elements not found in DOM');
		return;
	}

	// Success check
	if (!detail.successful) {
		showToast(
			toastElements,
			'Please try again. Contact supports if this persists.',
			'danger'
		);
		return;
	}

	// Contact form injection
	if (detail.elt.id === 'open-checkout') {
		const { bodyElement, titleElement } = toastElements;

		if (bodyElement && titleElement) {
			titleElement.innerText = '_01: Contact Information';
			bodyElement.innerHTML = detail.xhr.responseText;
			// Re-initialise customer form
			intialiseCustomerForm();
			// Show customer details toast
			showCustomerDetailsToast(toastElements);
		}
	}

	// Stripe Handshake (from payment-form)
	if (detail.elt.id === 'payment-form') {
		const response = JSON.parse(detail.xhr.responseText);
		const { clientSecret, stripePk } = response;
		try {
			const paymentUI = await showPaymentToast(toastElements, clientSecret);
			if (!paymentUI) return;

			const stripeInstance = await mountStripeElements(
				stripePk,
				clientSecret,
				paymentUI
			);
			if (stripeInstance && paymentUI.form) {
				const { stripe, elements } = stripeInstance;
				attachPaymentListener(stripe, elements, paymentUI.form);
			}
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Handshake failed.';

			showToast(
				toastElements,
				`Error: ${msg}. Contact support if this persists.`,
				'danger'
			);
		}
	}
}
