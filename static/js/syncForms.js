import { phReportError } from './reportError.js';

const DESKTOP_FORM_ID = 'sidebar-form-desktop';
const MOBILE_FORM_ID = 'sidebar-form-mobile';
const DRAWER_ID = 'mobileFilterDrawer';

/**
 *
 * @param {string} message
 */
const domError = message => {
	return phReportError(new Error(`[DOM_ERROR]: ${message}`), 'SYSTEM');
};

/**
 *
 * @param {HTMLFormElement} form
 * @param {boolean} isEnabled
 */
const setFormEnabledState = (form, isEnabled) => {
	if (!form) {
		return;
	}

	form.querySelectorAll('input, select, textarea,button').forEach(element => {
		const formControl =
			/** @type {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement|HTMLButtonElement} */ (
				element
			);
		formControl.disabled = !isEnabled;
	});
};

/**
 *
 * @param {boolean} mobileIsActive
 */
const syncSidebarForms = mobileIsActive => {
	const desktopForm = document.getElementById(DESKTOP_FORM_ID);
	const mobileForm = document.getElementById(MOBILE_FORM_ID);

	// Validate the assumption, not cast
	if (!(desktopForm instanceof HTMLFormElement)) {
		return;
	}
	if (!(mobileForm instanceof HTMLFormElement)) {
		return;
	}

	setFormEnabledState(desktopForm, !mobileIsActive);
	setFormEnabledState(mobileForm, mobileIsActive);
};

export const initialiseSidebarFormSync = () => {
	const drawerEl = document.getElementById(DRAWER_ID);

	if (!drawerEl) {
		domError('Drawer element not found in current DOM');
		return;
	}

	syncSidebarForms(false);

	drawerEl.addEventListener('shown.bs.offcanvas', () => {
		syncSidebarForms(true);
	});

	drawerEl.addEventListener('hidden.bs.offcanvas', () => {
		syncSidebarForms(false);
	});
};
