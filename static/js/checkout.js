/**
 * @typedef {import('@stripe/stripe-js').Stripe} Stripe
 * @typedef {import('@stripe/stripe-js').StripeConstructor} StripeConstructor
 * @typedef {import('@stripe/stripe-js').StripeElements} StripeElements
 * @typedef {import('@stripe/stripe-js').Appearance} Appearance
 */

import { getStandardHeaders } from '../../static/js/apiConfig.js';

/**
 * Returns the Stripe instance using the global window.Stripe constructor.
 * @param {string} pk
 * @returns {Stripe | null}
 */
export const getStripe = pk => {
	const stripeConstructor = /** @type {StripeConstructor} */ (window.Stripe);
	if (!stripeConstructor) {
		console.error(
			"Stripe.js not loaded. Ensure <script src='https://js.stripe.com/v3/'></script> is in your base template."
		);
		return null;
	}
	return stripeConstructor(pk);
};

/**
 * @typedef {Object} StripeInstance
 * @property {import('@stripe/stripe-js').Stripe} stripe
 * @property {import('@stripe/stripe-js').StripeElements} elements
 */

/**
 * Mounts Stripe Elements to the DOM using Client Secret from Payment Intent.
 * @param {string} pk
 * @param {string} clientSecret
 * @param {PaymentUI} paymentUI
 * @returns {Promise<StripeInstance | void>}
 */

export const mountStripeElements = async (pk, clientSecret, paymentUI) => {
	const stripe = getStripe(pk);
	if (!stripe) return;

	/** @type {Appearance} */
	const appearance = {
		theme: 'night',
		variables: { colorPrimary: '#052c33' }
	};

	const elements = stripe.elements({
		clientSecret,
		appearance
	});

	if (!elements) return;
	const paymentElement = elements.create('payment');

	if (!paymentElement) return;
	paymentElement.mount('#payment-element');

	const mountPoint =
		/** @type {HTMLElement} */ (
			paymentUI.form?.querySelector('#payment-element')
		) || paymentUI.form;

	try {
		await paymentElement.mount(mountPoint);
		return { stripe, elements };
	} catch (err) {
		console.log('Mounting failed: ', err);
	}

	// // Ensure the container exists before mounting
	// const container = document.getElementById('payment-element');
	// if (container) {
	// 	paymentElement.mount('#payment-element');
	// } else {
	// 	console.error('Target #payment-element not found in DOM.');
	// }

	// return { stripe, elements };
};

// /**
//  *
//  * @param {string} pk
//  * @returns
//  */

// async function initialiseCheckout(pk) {
// 	try {
// 		const response = await fetch('/checkout/create-payment-intent/', {
// 			method: 'POST',
// 			headers: getStandardHeaders()
// 		});

// 		if (!response.ok) throw new Error('Failed to create Payment Intent');

// 		const { clientSecret } = await response.json();

// 		return await mountStripeElements(pk, clientSecret);

// 		// initialise Sripe Elements with the clientSecret
// 	} catch (err) {
// 		console.error('Checkout Initialization Error:', err);
// 	}
// }
