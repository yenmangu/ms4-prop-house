/**
 * @typedef {Object} ToastDetail
 * @property {string} message
 * @property {'success'|'danger'|'warning'|'info'} status
 */

import { attachPaymentListener, mountStripeElements } from './checkout.js';
import { showToast, showPaymentToast } from './toast.js';

/**
 * @typedef {CustomEvent<ToastDetail>} ToastEvent
 */

document.addEventListener(
	'showToast',
	/**
	 *
	 * @param {Event} evt
	 */
	evt => {
		const toastEvt = /** @type {ToastEvent} */ (evt);
		const { message, status } = toastEvt.detail;
		console.log('SHOW TOAST');

		showToast(message, status);
	}
);

document.addEventListener('htmx:afterRequest', stripeListener);

/**
 *
 * @param {Event} evt
 */
async function stripeListener(evt) {
	const paymentEvent = /** @type {AfterRequestEvent} */ (evt);
	const { detail } = paymentEvent;

	// Early return if request did not come from trigger
	if (detail.elt.id !== 'checkout-button') return;

	// success
	if (detail.successful) {
		const response = JSON.parse(detail.xhr.responseText);
		const { clientSecret, stripePk } = response;

		try {
			const paymentUI = await showPaymentToast(clientSecret);
			if (!paymentUI) {
				return;
			}

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
			console.error('Handshake failed:', err);
		}
	} else {
		showToast('Checkout failed to initialise.', 'danger');
	}
}
