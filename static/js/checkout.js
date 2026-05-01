/**
 * @typedef {import('@stripe/stripe-js').Stripe} Stripe
 * @typedef {import('@stripe/stripe-js').StripeConstructor} StripeConstructor
 * @typedef {import('@stripe/stripe-js').StripeElements} StripeElements
 * @typedef {import('@stripe/stripe-js').Appearance} Appearance
 */

import { getStandardHeaders } from '../../static/js/apiConfig.js';
import { getPaymentAppearance } from './stripeAppearance.js';

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

	const elementsAppearance = getPaymentAppearance();

	// /** @type {Appearance} */
	// const appearance = {
	// 	theme: 'night',
	// 	inputs: 'spaced',
	// 	labels: 'auto',

	// 	variables: {
	// 		colorPrimary: 'rgb(255,107,0)',
	// 		colorBackground: 'rgb(18,18,18)',
	// 		colorText: 'rgb(242,242,242)'
	// 	}
	// };

	const elements = stripe.elements({
		clientSecret,
		appearance: elementsAppearance
	});

	if (!elements) return;
	const paymentElement = elements.create('payment');

	if (!paymentElement) return;

	if (!paymentUI.form || paymentUI.form == null) {
		return;
	}
	const mountPoint = /** @type {HTMLElement} */ (
		paymentUI.form.querySelector('#payment-element')
	);

	if (!mountPoint) {
		console.error(
			'Mount point #payment-element not found within the injected form.'
		);
		return;
	}

	try {
		await paymentElement.mount(mountPoint);
		return { stripe, elements };
	} catch (err) {
		console.log('Mounting failed: ', err);
	}
};

/**
 *
 * @param {Stripe} stripe
 * @param {StripeElements} elements
 * @param {HTMLElement} form
 */
export const attachPaymentListener = (stripe, elements, form) => {
	form.addEventListener('submit', async event => {
		event.preventDefault();

		const submitBtn = /** @type {HTMLButtonElement} */ (
			form.querySelector('#submit-payment')
		);
		const spinner = /** @type {HTMLElement} */ (form.querySelector('#spinner'));
		const buttonTxt = /** @type {HTMLElement} */ (
			form.querySelector('#button-text')
		);
		const messageContainer = /** @type {HTMLElement} */ (
			document.getElementById('payment-message')
		);

		// UI Feedback
		submitBtn.disabled = true;
		spinner.classList.remove('d-none');
		buttonTxt.innerText = 'PROCESSING...';

		// Confirm Payment
		const { error } = await stripe.confirmPayment({
			elements,
			confirmParams: {
				return_url: `${window.location.origin}/checkout/checkout-success`
			}
		});

		// Handle errors
		if (error && typeof error.message === 'string') {
			messageContainer.classList.remove('d-none');
			messageContainer.innerText = error.message;

			// Re-enable UI
			submitBtn.disabled = false;
			spinner.classList.add('d-none');
			buttonTxt.innerText = 'Complete Purchase';
		}
	});
};
