/**
 * @typedef {Object} ToastDetail
 * @property {string} message
 * @property {'success'|'danger'|'warning'|'info'} status
 */

import { showToast } from './toast.js';

/**
 * @typedef {CustomEvent<ToastDetail>} ToastEvent
 */

document.addEventListener(
	'showToast',
	/**
	 *
	 * @param {Event} evt
	 */
	evt => {
		const toastEvt = /** @type {ToastEvent} */ (evt);
		const { message, status } = toastEvt.detail;
		console.log('SHOW TOAST');

		showToast(message, status);
	}
);
