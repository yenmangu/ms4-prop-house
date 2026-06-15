import * as bootstrap from 'bootstrap';
import { phReportError } from './reportError.js';
import { getRenderDrawerState } from './util.js';

/**
 *
 * @param {string} message
 */
const domError = message => {
	return phReportError(new Error(`[DOM_ERROR]: ${message}`), 'SYSTEM');
};

/**
 *
 * @param {Event} evt
 */
export const handleSidebar = evt => {
	const element = /** @type {HTMLElement} */ (evt.target);

	const renderDrawer = getRenderDrawerState();

	if (!renderDrawer) {
		return;
	}
	if (element && element.closest('.manifest-form')) {
		const drawerEl = /** @type {HTMLElement} */ (
			document.getElementById('mobileFilterDrawer')
		);
		if (!drawerEl) {
			domError('[sidebarOffcanvas]: Drawer element not found in current DOM');
			return;
		}
		try {
			const instance = bootstrap.Offcanvas.getInstance(drawerEl);

			if (instance) {
				instance.hide();
			}
		} catch (err) {
			if (err instanceof Error) {
				domError(
					`Failed to close offcanvas safely: ${err instanceof Error ? err.message : 'No Error reported'}`
				);
			}
		}
	}
};
