import { phReportError } from './reportError.js';

/** @type {Record<keyof AddressPayload, string>} */
const addressFieldMap = {
	deliveryContactName: 'id_full_name',
	phoneNumber: 'id_phone_number',
	houseNameOrNumber: 'id_house_name_or_number',
	addressLine1: 'id_address_line_1',
	addressLine2: 'id_address_line_2',
	townOrCity: 'id_town_or_city',
	county: 'id_county',
	postcode: 'id_postcode',
	country: 'id_country'
};

const optionalFields = new Set([
	'deliveryContactName',
	'addressLine1',
	'addressLine2'
]);

export const intialiseCustomerForm = () => {
	const useAccountDetails = /** @type {HTMLInputElement|null} */ (
		document.getElementById('use_account_details')
	);
	const useSavedAddress = /** @type {HTMLInputElement|null} */ (
		document.getElementById('use_saved_address')
	);
	const useAccountName = /** @type {HTMLInputElement|null} */ (
		document.getElementById('use_account_name')
	);

	const updateState = () => {
		const accountDetailsEnabled = useAccountDetails?.checked ?? false;
		const savedAddressEnabled = useSavedAddress?.checked ?? false;
		const accountNameEnabled = useAccountName?.checked ?? false;
		updateFullNameState(
			accountDetailsEnabled,
			savedAddressEnabled,
			accountNameEnabled
		);
		updateEmailState(accountDetailsEnabled);
		updateAddressState(savedAddressEnabled);
	};

	bindCheckbox(useAccountDetails, updateState);

	bindCheckbox(useSavedAddress, updateState);
	bindCheckbox(useAccountName, updateState);
	updateState();
};

/**
 * @param {boolean} useAccountDetails
 * @param {boolean} useSavedAddress
 * @param {boolean} useAccountName
 */
const updateFullNameState = (
	useAccountDetails,
	useSavedAddress,
	useAccountName
) => {
	const fullNameInput = getInputById('id_full_name');
	if (!fullNameInput) {
		return;
	}
	if (!useAccountDetails) {
		unlockInput(fullNameInput, 'Required for hire');
		fullNameInput.value = '';
		fullNameInput.focus();
		return;
	}
	const accountDefaults = getAccountDefaults();
	const address = getAddress();
	const shouldUseDeliveryContact =
		useSavedAddress &&
		address &&
		address.deliveryContactName &&
		!useAccountName;
	fullNameInput.value = shouldUseDeliveryContact
		? address.deliveryContactName
		: accountDefaults.name;
	lockInput(fullNameInput);
};

/**
 * @param {boolean} useAccountDetails
 */

const updateEmailState = useAccountDetails => {
	const emailInput = getInputById('id_email');
	if (!emailInput) {
		return;
	}
	if (!useAccountDetails) {
		unlockInput(emailInput, 'Required for hire');
		emailInput.value = '';
		return;
	}
	const accountDefaults = getAccountDefaults();
	emailInput.value = accountDefaults.email;
	lockInput(emailInput);
};

/**
 * @param {boolean} useSavedAddress
 */
const updateAddressState = useSavedAddress => {
	const address = getAddress();

	if (!address) return;

	for (const [key, val] of Object.entries(address)) {
		if (key === 'deliveryContactName') {
			continue;
		}

		const inputId = addressFieldMap[/** @type {keyof AddressPayload} */ (key)];
		const input = getInputById(inputId);

		if (!input) {
			continue;
		}
		// Set required attribute based on `optionalFields` set
		input.required = !optionalFields.has(key);

		if (!useSavedAddress) {
			unlockInput(input, 'Required for hire');
			input.value = '';
			continue;
		}

		input.value = val ?? '';
		lockInput(input);
	}
};

/**
 *
 * @param {HTMLInputElement|null} checkbox
 * @param {(checked:boolean)=>void} callback
 */
const bindCheckbox = (checkbox, callback) => {
	if (!checkbox) return;

	checkbox.addEventListener('change', e => {
		const target = /** @type {HTMLInputElement} */ (e.target);
		callback(target.checked);
	});
};

/**
 *
 * @returns {AddressPayload|undefined}
 */
const getAddress = () => {
	const addressElement = document.getElementById('user-address-data');
	if (!addressElement || !addressElement.textContent) {
		return;
	}
	try {
		/** @type {AddressPayload} */
		const address = JSON.parse(addressElement.textContent);
		return address;
	} catch (error) {
		phReportError(
			new Error('[JSON_ERROR]: Address JSON payload could not be parsed'),
			'SYSTEM'
		);
		return;
	}
};

/**
 * Scrapes data passed from Django json_script tags
 * @returns
 */
const getAccountDefaults = () => {
	const nameEl = document.getElementById('user-name-data');
	const emailEl = document.getElementById('user-email-data');

	return {
		name: nameEl?.textContent ? JSON.parse(nameEl.textContent) : '',
		email: emailEl?.textContent ? JSON.parse(emailEl.textContent) : ''
	};
};

/**
 * @param {string} id
 * @returns {HTMLInputElement|null}
 */

const getInputById = id => {
	return /** @type {HTMLInputElement|null} */ (document.getElementById(id));
};

/**
 * @param {HTMLInputElement} input
 */

const lockInput = input => {
	input.toggleAttribute('readonly', true);
	input.classList.add('is-locked');
};

/**
 * @param {HTMLInputElement} input
 * @param {string} placeholder
 */
const unlockInput = (input, placeholder) => {
	input.toggleAttribute('readonly', false);
	input.classList.remove('is-locked');
	input.placeholder = placeholder;
};
