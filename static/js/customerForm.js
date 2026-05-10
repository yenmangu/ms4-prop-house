export const intialiseCustomerForm = () => {
	const checkbox = /** @type {HTMLInputElement} */ (
		document.getElementById('use_account_details')
	);

	if (checkbox) {
		checkbox.addEventListener('change', e => {
			const checkEl = /** @type {HTMLInputElement} */ (e.target);
			updateFormState(checkEl.checked);
		});

		updateFormState(checkbox.checked);
	}
};

/**
 * Scrapes data passed from Django json_script tags
 * @returns
 */
const getDefaults = () => {
	const nameEl = document.getElementById('user-name-data');
	const emailEl = document.getElementById('user-email-data');

	return {
		name: nameEl ? JSON.parse(nameEl.textContent) : '',
		email: emailEl ? JSON.parse(emailEl.textContent) : ''
	};
};

/**
 *
 * @param {boolean} isAccountMode
 */
const updateFormState = isAccountMode => {
	const userDefaults = getDefaults();
	const fields = [
		{ id: 'id_full_name', value: userDefaults.name },
		{ id: 'id_email', value: userDefaults.email }
	];

	fields.forEach(field => {
		const input = /** @type {HTMLInputElement} */ (
			document.getElementById(field.id)
		);
		if (input) {
			input.value = isAccountMode ? field.value : '';
			input.toggleAttribute('readonly', isAccountMode);
			input.classList.toggle('is-locked', isAccountMode);
			input.placeholder = isAccountMode ? field.value : 'Required for hire';

			if (!isAccountMode && field.id === 'id_full_name') {
				input.focus();
			}
		}
	});
};
