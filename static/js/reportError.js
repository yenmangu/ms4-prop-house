import { getToastElements } from './domElements.js';
import { showToast } from './toast.js';

const IS_DEV = true;

/**
 *
 * @param {Error|string} error
 * @param {'SYSTEM'|'USER'|'NETWORK'} context
 */
const phReportError = (error, context = 'SYSTEM') => {
	const message = error instanceof Error ? error.message : error;
	if (IS_DEV) {
		reportToConsole(error, context);
		phNotify(`[DEV_ERROR] [${context}]: ${message}`, 'danger');
	} else {
		const userFriendlyMessage =
			context === 'NETWORK'
				? 'Connection lost. Please check your internet.'
				: `An unexpected error occurred (${context})`;

		phNotify(userFriendlyMessage, 'danger');
	}
};

/**
 * @param {Error|string} error
 * @param {string} context
 */
const reportToConsole = (error, context) => {
	console.group(
		`%c [${context}_CRITICAL] `,
		'background: #b00; color: #fff; font-weight: bold;'
	);
	console.error(error);
	console.groupEnd();
};

// TODO: Remove belo during cleanup

// /** @type {number|undefined} */
// let toastTimeout;

/**
 *
 * @param {string} message
 * @param {'success'|'error'|'info'|'danger'} type
 */
const phNotify = (message, type = 'success') => {
	const toastElements = getToastElements();
	if (!toastElements) {
		console.error('DOM ERROR: ToastElements not found');
		return;
	}
	const formatted = message.toUpperCase();

	showToast(toastElements, message, type);
	console.error('[TEMP CONSOLE]: ', message);

	// Deprecated in favour of above
	// Moved to centralised bootstrap toast system.
	// TODO: Remove deporecated during cleanup

	// let feedbackEl = document.querySelector('#system-feedback');

	// if (!feedbackEl) {
	// 	feedbackEl = document.createElement('div');
	// 	feedbackEl.id = 'system-feedback';
	// 	document.body.appendChild(feedbackEl);
	// }

	// const feedbackHTMLElement = /** @type {HTMLElement} */ (feedbackEl);

	// feedbackHTMLElement.className = `industrual-toast toast-${type}`;
	// feedbackHTMLElement.innerText = message.toUpperCase();

	// feedbackHTMLElement.classList.add('visible');

	// if (toastTimeout) {
	// 	clearTimeout(toastTimeout);
	// }

	// // Using `window` to explicitly set return type of number
	// toastTimeout = window.setTimeout(() => {
	// 	feedbackHTMLElement.classList.remove('visible');
	// }, 4000);
};

export { phReportError, phNotify };
