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
};

export { phReportError, phNotify };
