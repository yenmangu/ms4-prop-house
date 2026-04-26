import { loadStripe } from '@stripe/stripe-js';
import { getStandardHeaders } from '../../staticfiles/js/apiConfig.js';

/**
 * @typedef {Object} StripeInstance
 * @property {import('@stripe/stripe-js').Stripe} stripe
 * @property {import('@stripe/stripe-js').StripeElements} elements
 */

async function initialiseCheckout() {
	const response = await fetch('/commerce/payment/create-intent/', {
		method: 'POST',
		headers: getStandardHeaders()
	});

	const { clientSecret } = await response.json();

	// initialise Sripe Elements with the clientSecret
	async function openCheckout() {}
}

/**
 *
 * @param {string} pk
 * @param {string} clientSecret
 * @param {Object} ui
 *
 * @returns {Promise<StripeInstance | void>}
 */

export const mountStripeElements = async (pk, clientSecret, ui) => {
	const stripe = await loadStripe(pk);
	if (!stripe) return;

	const appearance /** @type  */ = {
		theme: 'night',
		variables: { colorPrimary: '#052c33' }
	};

	const elements = stripe?.elements({
		clientSecret,
		appearance: {
			theme: 'night',
			variables: {
				colorPrimary: '#052c33'
			}
		}
	});

	if (!elements) return;
	const paymentElement = elements.create('payment');

	if (!paymentElement) return;
	paymentElement.mount('#payment-element');

	return { stripe, elements };
};
