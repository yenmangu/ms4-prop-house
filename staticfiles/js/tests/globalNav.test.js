import { updateGlobalNav } from '../globalNav.js';

describe('globalNav.js: updateGlobalNav', () => {
	beforeEach(() => {
		// Set up our document body to match your selectors
		document.body.innerHTML = `
      <div id="nav-basket-count" class="hidden">0</div>
      <div id="nav-basket-total">£0.00</div>
    `;
	});
	test('updates count and total correctly', () => {
		updateGlobalNav(5, '£25.00');

		const countBadge = /** @type {HTMLElement} */ (
			document.querySelector('#nav-basket-count')
		);
		const totalDisplay = /** @type {HTMLElement} */ (
			document.querySelector('#nav-basket-total')
		);

		expect(countBadge.innerText).toBe('5');
		expect(totalDisplay.innerText).toBe('£25.00');
		expect(countBadge.classList.contains('hidden')).toBe(false);
	});

	test('hides the badge when totalItems is 0', () => {
		updateGlobalNav(0, '£0.00');

		const countBadge = /** @type {HTMLElement} */ (
			document.querySelector('#nav-basket-count')
		);
		expect(countBadge.classList.contains('hidden')).toBe(true);
	});
});
