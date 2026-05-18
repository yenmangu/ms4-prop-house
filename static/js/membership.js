import { getLiveEndpoint } from './apiConfig.js';
import { getToastElements } from './domElements.js';
import { phReportError } from './reportError.js';

export const initMembershipCheckout = () => {
	const membershipGrid = /** @type {HTMLElement} */ (
		document.getElementById('membership-grid')
	);

	let domError = new Error('[DOM_ERROR]: ');

	if (!membershipGrid) {
		domError.message += 'Membership grid not found in active DOM';
		phReportError(domError, 'SYSTEM');
		return;
	}

	membershipGrid.addEventListener('htmx:configRequest', evt => {
		const targetForm = /** @type {HTMLElement} */ (evt.target);

		if (targetForm && targetForm.id === 'create-intent') {
			const submitBtn = /** @type {HTMLButtonElement} */ (
				targetForm.querySelector('button[type="submit]')
			);

			if (!submitBtn) {
				domError.message +=
					'Submit button for membership form not found in active DOM';
				phReportError(domError, 'SYSTEM');
				evt.preventDefault();
				return;
			}

			const tierId = submitBtn.dataset.tierId;
			if (!tierId) {
				domError.message +=
					'tierId data attribute not present on button trigger.';
				phReportError(domError, 'SYSTEM');
				evt.preventDefault();
				return;
			}

			const toastUI = getToastElements();
			if (!toastUI) {
				domError.message += 'Toast slide elements not found in active DOM.';
				phReportError(domError, 'SYSTEM');
				evt.preventDefault();
			}
		}
	});
};
