import { phReportError } from './reportError.js';
import { getRenderDrawerState } from './util.js';

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

	form.querySelectorAll('input, select, textarea, button').forEach(element => {
		const formControl =
			/** @type {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement|HTMLButtonElement} */ (
				element
			);
		formControl.disabled = !isEnabled;
	});
};

/**
 * @typedef {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} ValueControl
 */

/**
 *
 * @param {Element|null} element
 * @returns {element is ValueControl}
 */
const isValueControl = element => {
	return (
		element instanceof HTMLInputElement ||
		element instanceof HTMLSelectElement ||
		element instanceof HTMLTextAreaElement
	);
};

/**
 *
 * @param {Element|null} element
 * @returns {element is HTMLInputElement}
 */
const isCheckableInput = element => {
	return (
		element instanceof HTMLInputElement &&
		(element.type === 'checkbox' || element.type === 'radio')
	);
};

/**
 *
 * @param {ValueControl} sourceInput
 * @param {ValueControl} targetInput
 */
const syncValueControl = (sourceInput, targetInput) => {
	targetInput.value = sourceInput.value;
};

/**
 *
 * @param {HTMLInputElement} sourceControl
 * @param {HTMLInputElement} targetControl
 */
const syncCheckedControl = (sourceControl, targetControl) => {
	targetControl.checked = sourceControl.checked;
};

/**
 *
 * @param {ValueControl} sourceControl
 * @param {HTMLFormElement} targetForm
 * @returns {Element|null}
 */
const getMatchingControl = (sourceControl, targetForm) => {
	if (!sourceControl.name) {
		return null;
	}

	if (isCheckableInput(sourceControl)) {
		return targetForm.querySelector(
			`input[name="${CSS.escape(sourceControl.name)}"][value="${CSS.escape(sourceControl.value)}"]`
		);
	}
	return targetForm.querySelector(`[name="${CSS.escape(sourceControl.name)}"]`);
};

/**
 *
 * @param {HTMLFormElement} sourceForm
 * @param {HTMLFormElement} targetForm
 */
const syncForms = (sourceForm, targetForm) => {
	const sourceControls = sourceForm.querySelectorAll('input, select, textarea');

	if (sourceControls.length === 0) {
		domError('Sync orchestration found no source controls in form');
		return;
	}

	for (const sourceControl of sourceControls) {
		if (!isValueControl(sourceControl)) {
			// Continue to next source control
			continue;
		}
		const targetControl = getMatchingControl(sourceControl, targetForm);

		// Early return if no target control - something has gone wrong
		if (!targetControl) {
			domError(
				`Sync orchestration found no matching control for ${sourceControl.name}`
			);
			return;
		}
		if (!isValueControl(targetControl)) {
			domError(`Sync orchestration could not validate ${targetControl}`);
			return;
		}

		// sourceControl and targetControl now must be valid

		if (isCheckableInput(sourceControl) && isCheckableInput(targetControl)) {
			syncCheckedControl(sourceControl, targetControl);
			// This checkbox is in sync, continue to next
			continue;
		}

		syncValueControl(sourceControl, targetControl);
	}
};

/**
 *
 * @param {HTMLFormElement} desktopForm
 * @param {HTMLFormElement} mobileForm
 * @param {boolean} mobileIsActive
 */
const syncCorrectSourceToTarget = (desktopForm, mobileForm, mobileIsActive) => {
	let source = desktopForm;
	let target = mobileForm;
	if (!mobileIsActive) {
		source = mobileForm;
		target = desktopForm;
	}
	syncForms(source, target);
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
	syncCorrectSourceToTarget(desktopForm, mobileForm, mobileIsActive);

	setFormEnabledState(desktopForm, !mobileIsActive);
	setFormEnabledState(mobileForm, mobileIsActive);
};

export const initialiseSidebarFormSync = () => {
	const renderDrawer = getRenderDrawerState();
	if (!renderDrawer) {
		return;
	}
	const drawerEl = document.getElementById(DRAWER_ID);

	if (!drawerEl) {
		domError('[syncForm.js]: Drawer element not found in current DOM');
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
