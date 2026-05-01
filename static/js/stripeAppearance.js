/**
 * @typedef {import("@stripe/stripe-js").Appearance} Appearance
 *
 */

const APPEARANCE_VALS = {
	STARK_WHITE: 'rgb(242,242,242)',
	BASE_DARK: 'rgb(18,18,18)',
	SURFACE_GREY: 'rgb(30,30,30)',
	ORANGE_ACCENT: 'rgb(255,107,0)',
	ERROR_RED: 'rgb(220,53,69)'
};

/**
 *
 * @returns {Appearance}
 */
export const getPaymentAppearance = () => {
	return /** @type {Appearance} */ ({
		labels: 'floating',
		variables: {
			colorText: APPEARANCE_VALS.STARK_WHITE,
			colorBackground: APPEARANCE_VALS.BASE_DARK,
			colorPrimary: APPEARANCE_VALS.ORANGE_ACCENT,
			iconColor: APPEARANCE_VALS.ORANGE_ACCENT
		}
	});
};
