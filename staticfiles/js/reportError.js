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
	} else {
		displayUserNotification(`ACTION_FAILED: ${message}`, context);
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
 * Displays non technical error message to end user
 * @param {string} errorString
 * @param {string} context
 */

const displayUserNotification = (errorString, context) => {
	//
	let feedbackEl = document.querySelector('#system-feedback');
	if (!feedbackEl) {
		feedbackEl = document.createElement('div');
		feedbackEl.id = 'system-feedback';
		feedbackEl.className = 'industrial-toast';
		document.body.appendChild(feedbackEl);
	}

	if (!(feedbackEl instanceof HTMLElement)) {
		console.error(
			'[DOM_ERROR] - feedbackEl is not HTMLElement; cannot display errors naturally'
		);
		reportToConsole(new Error(errorString), context);
		return;
	}

	feedbackEl.innerText = errorString.toUpperCase();
	feedbackEl.classList.add('visible');

	const timeoutId = setTimeout(() => {
		feedbackEl.classList.remove('visible');
		delete feedbackEl.dataset.timeoutId;
	}, 5000);

	feedbackEl.dataset.timeoutId = timeoutId.toString();
};

/** @type {number|undefined} */
let toastTimeout;

/**
 *
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 */
const phNotify = (message, type = 'success') => {
	let feedbackEl = document.querySelector('#system-feedback');

	if (!feedbackEl) {
		feedbackEl = document.createElement('div');
		feedbackEl.id = 'system-feedback';
		document.body.appendChild(feedbackEl);
	}

	const feedbackHTMLElement = /** @type {HTMLElement} */ (feedbackEl);

	feedbackHTMLElement.className = `industrual-toast toast-${type}`;
	feedbackHTMLElement.innerText = message.toUpperCase();

	feedbackHTMLElement.classList.add('visible');

	if (toastTimeout) {
		clearTimeout(toastTimeout);
	}

	// Using `window` to explicitly set return type of number
	toastTimeout = window.setTimeout(() => {
		feedbackHTMLElement.classList.remove('visible');
	}, 4000);
};

export { phReportError, phNotify };
