// import { Toast } from 'bootstrap';
import * as bootstrap from 'bootstrap';
import { phNotify } from './reportError.js';

/**
 *
 * @param {string} message
 * @param {string} status
 * @returns
 */
export const showToast = (message, status = 'success') => {
	const toastElement = document.getElementById('liveToast');
	const bodyElement = document.getElementById('toastBody');
	const titleElement = document.getElementById('toastTitle');

	if (!toastElement) {
		reportError(new Error('[DOM_ERROR]: Toast element not found'));
		return;
	}

	if (!bodyElement) {
		reportError(new Error('[DOM_ERROR]: Toast body element not found'));
		return;
	}

	if (!titleElement) {
		reportError(new Error('[DOM_ERROR]: Toast title element not found'));
		return;
	}

	bodyElement.innerText = message;
	titleElement.innerText = status.charAt(0).toUpperCase() + status.slice(1);

	titleElement.className =
		status === 'danger' ? 'me-auto text-danger' : 'me-auto text-success';

	titleElement.style.color = 'var(--clr-success)';

	const toast = new bootstrap.Toast(toastElement);
	toast.show();
};

/**
 *
 * @param {string} clientSecret
 */
export const showPaymentToast = async clientSecret => {
	const container = document.createElement('div');

	const toastElement = document.getElementById('liveToast');
	const bodyElement = document.getElementById('toastBody');
	const titleElement = /** @type {HTMLElement} */ (
		document.getElementById('toastTitle')
	);
	const template = /** @type {HTMLTemplateElement} */ (
		document.getElementById('stripe-form-template')
	);

	if (!toastElement || !bodyElement || !template) return;

	// 1. Clear previous content and clone the template
	bodyElement.innerHTML = '';
	const clone = template.content.cloneNode(true);

	// 2. Inject the clone into the toast body
	bodyElement.appendChild(clone);

	// 3. Set your "Industrial" styling
	titleElement.innerText = 'Secure Checkout';
	titleElement.style.color = 'var(--clr-primary)';

	// 4. Show toast without autohide
	const toast = new bootstrap.Toast(toastElement, { autohide: false });
	toast.show();

	return {
		form: document.getElementById('payment-form'),
		messageContainer: document.getElementById('payment-message'),
		clientSecret: clientSecret
	};
};
