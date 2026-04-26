/**
 * @typedef {Object} ToastDetail
 * @property {string} message
 * @property {'success'|'danger'|'warning'|'info'} status
 */

import { mountStripeElements } from './checkout.js';
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
		const paymentUI = showPaymentToast(clientSecret);
		const mountPromise = mountStripeElements(stripePk, clientSecret, paymentUI);
		try {
			const stripeInstance = await mountPromise;
			if (!stripeInstance) return;
			const { stripe, elements } = stripeInstance;
			console.log('Stripe live on toast');
		} catch (e) {
			throw e;
		}
	} else {
		showToast('Checkout failed to initialise.', 'danger');
	}
}
