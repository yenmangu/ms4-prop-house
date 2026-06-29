// import { Toast } from 'bootstrap';
import * as bootstrap from 'bootstrap';
import { phReportError } from './reportError.js';

/**
 * Wrapper to build and expose the Bootstrap toast, and programatically
 * determine `autohide` and `delay` config based on status type.
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

	const autohide = status === 'success';

	const toast = new bootstrap.Toast(toastElement, {
		autohide: autohide,
		delay: 3000
	});

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

		toastElement.classList.add('toast--checkout');

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
	toastElement.classList.add('toast--checkout');
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

/**
 *
 * @param {HTMLElement} toastEl
 * @returns {Promise<boolean>}
 */
export const listenForClose = toastEl => {
	return new Promise(resolve => {
		toastEl.addEventListener(
			'hidden.bs.toast',
			() => {
				return resolve(true);
			},
			{ once: true }
		);
	});
};

/**
 *
 * @param {ToastElements} toastElements
 */
export const showHireFormToast = toastElements => {
	const { toastElement, titleElement } = toastElements;

	toastElement.classList.add('toast--checkout');
	titleElement.innerText = 'HIRE_DETAILS';
	titleElement.style.color = 'var(--clr-primary)';

	const toast = new bootstrap.Toast(toastElement, { autohide: false });
	if (toast) {
		toast.show();
	}
};

/**
 *
 * @param {string} [toastId='liveToast']
 */
export const destroyToast = (toastId = 'liveToast') => {
	const toastEl = document.getElementById(toastId);
	if (toastEl) {
		const toastInstance = bootstrap.Toast.getInstance(toastEl);
		if (toastInstance) {
			toastInstance.hide();
			toastInstance.dispose();
		}
	}
};

export const resetToast = () => {
	const toastEl = document.getElementById('liveToast');
	if (!toastEl) return;
	toastEl.className = 'toast industrial-toast';
	const titleEl = document.getElementById('toastTitle');
	const bodyEl = document.getElementById('toastBody');
	if (titleEl) {
		titleEl.className = 'me-auto';
		titleEl.style.color = '';
		titleEl.innerText = 'Notification';
	}
	if (bodyEl) {
		bodyEl.innerHTML = '';
	}
};
