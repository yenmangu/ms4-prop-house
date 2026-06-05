import { getToastElements } from './domElements.js';
import { showToast } from './toast.js';

/**
 *
 * @param {string} tags
 * @returns {'success'|'info'|'warning'|'danger'}
 */
const normaliseMessageStatus = tags => {
	const tagList = tags.split(' ');
	if (tagList.includes('error')) {
		return 'danger';
	}
	if (tagList.includes('warning')) {
		return 'warning';
	}
	if (tagList.includes('info')) {
		return 'info';
	}
	return 'success';
};

export const initialiseDjangoMessageToasts = () => {
	const messageScript = document.getElementById('django-messages-data');
	if (!messageScript) {
		return;
	}

	const toastElements = getToastElements();
	if (!toastElements) {
		return;
	}
	/** @type {MessageData[]} */
	const messages = JSON.parse(messageScript.textContent || '[]');

	messages.forEach(messageData => {
		showToast(
			toastElements,
			messageData.message,
			normaliseMessageStatus(messageData.tags)
		);
	});
};
