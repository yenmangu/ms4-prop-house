import { phReportError } from './reportError.js';

/**
 * Centralised DOM query for 'toast' elements
 *
 * @param {string} [id='liveToast']
 * @returns {ToastElements|void}
 */
export const getToastElements = (id = 'liveToast') => {
	const toastElement = document.getElementById(id);
	const bodyElement = document.getElementById('toastBody');
	const titleElement = document.getElementById('toastTitle');

	if (!toastElement) {
		phReportError(new Error('[DOM_ERROR]: Toast element not found'));
		return;
	}

	if (!bodyElement) {
		phReportError(new Error('[DOM_ERROR]: Toast body element not found'));
		return;
	}

	if (!titleElement) {
		phReportError(new Error('[DOM_ERROR]: Toast title element not found'));
		return;
	}

	return { toastElement, bodyElement, titleElement };
};
