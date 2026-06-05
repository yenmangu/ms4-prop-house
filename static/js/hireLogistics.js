// hireLogistics.js

import { performAnimation } from './basketUI.js';
import { phReportError } from './reportError.js';

export const initialiseHireLogistics = () => {
	// Check this is a logistics section/page
	const isLogistics = /** @type {HTMLElement} */ (
		document.querySelector('[data-zone="logistics"]')
	);
	if (!isLogistics) return;

	// Early return if out of stock
	const hasStock = isLogistics.dataset.available === 'true';
	if (!hasStock) return;

	const triggerBtn = /** @type {HTMLButtonElement} */ (
		document.querySelector('[data-action="reveal-hire"]')
	);
	const cancelBtn = /** @type {HTMLButtonElement} */ (
		document.querySelector('[data-action="cancel-hire"]')
	);

	const hireGate = /** @type {HTMLElement} */ (
		document.querySelector('[data-unit="hire-logistics-gate"]')
	);

	// Report error if stock available and triggerBtn is supposed to exist
	if (!triggerBtn) {
		phReportError(
			new Error('[DOM_ERROR]: Trigger Button Element  not found on page.'),
			'SYSTEM'
		);
	}

	triggerBtn.addEventListener('click', async () => {
		if (!hireGate) {
			phReportError(
				new Error('[DOM_ERROR]: Hire elements not found on page.'),
				'SYSTEM'
			);
		}

		hireGate.classList.remove('hidden');
		triggerBtn.classList.add('hidden');

		requestAnimationFrame(() => {
			requestAnimationFrame(async () => {
				await performAnimation(hireGate, 'gate-open');
			});
		});
	});

	if (cancelBtn) {
		cancelBtn.addEventListener('click', async () => {
			hireGate.classList.remove('gate-open');

			hireGate.addEventListener(
				'transitionend',
				() => {
					hireGate.classList.add('hidden');

					triggerBtn.classList.remove('hidden');
				},
				{ once: true }
			);
		});
	}
};
