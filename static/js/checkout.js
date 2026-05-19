/**
 * @typedef {import('@stripe/stripe-js').Stripe} Stripe
 * @typedef {import('@stripe/stripe-js').StripeConstructor} StripeConstructor
 * @typedef {import('@stripe/stripe-js').StripeElements} StripeElements
 * @typedef {import('@stripe/stripe-js').Appearance} Appearance
 * @typedef {import('@stripe/stripe-js').SetupIntent} SetupIntent
 */

import { getStandardHeaders } from '../../static/js/apiConfig.js';
import { phReportError } from './reportError.js';
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
 * @param {string} clientSecret
 * @param {SubscriptionIntentMetadata} [metadata={}]
 */
export const attachPaymentListener = (
	stripe,
	elements,
	form,
	clientSecret,
	metadata
) => {
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

		// Determine operation routing based on Stripe token structure rules
		const isSubscription = clientSecret.startsWith('seti_');

		const confirmParams = {
			elements,
			confirmParams: {
				return_url: isSubscription
					? `${window.location.origin}/accounts/membership/success`
					: `${window.location.origin}/checkout/checkout-success`
			}
		};

		// Confirm Payment/Subscription Setup
		// Disgusting JSDoc typecast to `any` to get around Stripe's
		// incredibly strict return type.
		/** @type {any} */
		const result = isSubscription
			? await stripe.confirmSetup({
					elements: elements,
					redirect: 'if_required'
				})
			: await stripe.confirmPayment(confirmParams);

		// Handle errors first
		if (result.error) {
			const error = result.error;
			if (typeof error.message === 'string') {
				messageContainer.classList.remove('d-none');
				messageContainer.innerText = error.message;
			}

			// Re-enable UI
			submitBtn.disabled = false;
			if (spinner) spinner.classList.add('d-none');
			if (buttonTxt) buttonTxt.innerText = 'PAY NOW';
			return;
		}

		if (isSubscription) {
			// Nice and friendly `SetupIntent` type again
			const setupIntent = /** @type {SetupIntent} */ (result.setupIntent);
			if (
				setupIntent &&
				(setupIntent.status === 'succeeded' ||
					setupIntent.status === 'processing')
			) {
				let tierId;
				if (metadata && metadata.tierId) {
					tierId = metadata.tierId;
				} else {
					phReportError(
						new Error(
							'[DOM_ERROR]: tierId property not found in metadata, but required for subscription intent'
						),
						'SYSTEM'
					);
					if (metadata && metadata.toastInstance) {
						metadata.toastInstance.hide();
					}
					// Return immediately
					return;
				}

				// @ts-ignore
				window.htmx.ajax(
					'GET',
					`/accounts/membership/success/?inline=1&tier_id=${tierId}&setup_intent=${setupIntent.id}`,
					{
						target: `#membership-card-${tierId}`,
						swap: 'outerHTML'
					}
				);

				if (metadata && metadata.toastInstance) {
					metadata.toastInstance.hide();
				}

				return;
			}
		}

		// Deprecated because above now handles subscriptions
		// const { error } = await stripe.confirmPayment({
		// 	elements,
		// 	confirmParams: {
		// 		return_url: `${window.location.origin}/checkout/checkout-success`
		// 	}
		// });
	});
};
