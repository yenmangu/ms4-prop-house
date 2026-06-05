// import { Toast } from 'bootstrap';
import * as bootstrap from 'bootstrap';
import { phReportError } from './reportError.js';

/**
 *
 * @param {ToastElements} toastElements
 * @param {string} message
 * @param {string} status
 * @returns
 */
export const showToast = (toastElements, message, status = 'success') => {
	if (!toastElements) return;
	const { toastElement, bodyElement, titleElement } = toastElements;

	bodyElement.innerText = message;
	titleElement.innerText = status.charAt(0).toUpperCase() + status.slice(1);

	titleElement.className =
		status === 'danger' ? 'me-auto text-danger' : 'me-auto text-success';

	titleElement.style.color = 'var(--clr-success)';

	const toast = new bootstrap.Toast(toastElement, { autohide: false });
	toast.show();
};

/**
 *
 * @param {ToastElements} toastElements
 * @param {string} clientSecret
 * @returns {Promise<PaymentUI>}
 */
export const showPaymentToast = async (toastElements, clientSecret) => {
	return new Promise(resolve => {
		if (!toastElements) return;
		const { toastElement, bodyElement, titleElement } = toastElements;
		const template = /** @type {HTMLTemplateElement} */ (
			document.getElementById('stripe-form-template')
		);

		// DEBUG;
		if (!template) {
			phReportError(new Error('[DOM_ERROR]: No template found'), 'SYSTEM');
		}

		// Clear previous content and clone the template
		bodyElement.innerHTML = '';

		const clone = template.content.cloneNode(true);

		// Inject the clone into the toast body
		bodyElement.appendChild(clone);

		if (!toastElement || !bodyElement || !template) {
			console.error('ERROR');
		}

		// Set your styling
		titleElement.innerText = 'Secure Checkout';
		titleElement.style.color = 'var(--clr-primary)';

		// Show toast without autohide
		const toast = new bootstrap.Toast(toastElement, { autohide: false });

		toastElement.addEventListener(
			'shown.bs.toast',
			() => {
				/** @type {PaymentUI} */
				const paymentUI = {
					form: document.getElementById('payment-form'),
					messageContainer: document.getElementById('payment-message'),
					clientSecret: clientSecret
				};
				if (toast) {
					paymentUI.toastInstance = toast;
				}
				resolve(paymentUI);
			},
			{ once: true }
		);
		toast.show();
	});
};

/**
 *
 * @param {ToastElements} toastElements
 * @returns
 */
export const showCustomerDetailsToast = async toastElements => {
	if (!toastElements) return;
	const { toastElement, bodyElement, titleElement } = toastElements;
	titleElement.innerText = 'Step _01: Contact Information';
	titleElement.style.color = 'var(--clr-primary)';

	const toast = new bootstrap.Toast(toastElement, { autohide: false });
	toast.show();
};

/**
 *
 * @param {bootstrap.Toast} toast
 */
export const hideToast = toast => {
	if (toast) {
		toast.hide();
	}
};
