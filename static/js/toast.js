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

	const toast = new bootstrap.Toast(toastElement);
	toast.show();
};
