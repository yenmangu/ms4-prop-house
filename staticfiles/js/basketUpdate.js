import { getStandardHeaders } from './apiConfig.js';
import { phReportError } from './reportError.js';

/**
 *
 * @param {BasketUpdateReport} report
 * @returns {Promise<BasketState>}
 */
export const basketUpdateReport = async report => {
	if (!report) {
		phReportError('No response from server', 'NETWORK');
	}
	const { product_id, action, quantity = 1, endpoint } = report;

	const response = await fetch(endpoint, {
		method: 'POST',
		headers: getStandardHeaders(),
		body: JSON.stringify({ product_id, action, quantity })
	});

	if (!response.ok) {
		const errorData = await response.json().catch(() => {});
		throw new Error(
			errorData.error || `BASKET_SYNC_PHYSICAL_FAILURE: ${response.status}`
		);
	}

	return await response.json();
};
