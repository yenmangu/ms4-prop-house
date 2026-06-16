/**
 * @type {Record<number, StatusHandlerResult>}
 */

const HTMX_STATUS_HANDLERS = {
	400: {
		handled: true,
		message: 'Please check the form and try again.',
		status: 'warning'
	},
	401: {
		handled: true,
		message: 'Please log in before continuing to checkout.',
		status: 'warning'
	},
	403: {
		handled: true,
		message: 'You do not have permission to perform this action.',
		status: 'danger'
	},
	404: {
		handled: true,
		message: 'The requested checkout resource could not be found.',
		status: 'danger'
	},
	500: {
		handled: true,
		message: 'A server error occurred. Please try again shortly.',
		status: 'danger'
	}
};

/**
 *
 * @param {number} statusCode
 * @returns {StatusHandlerResult | undefined}
 */
export const getStatusHandlerResult = statusCode => {
	return HTMX_STATUS_HANDLERS[statusCode];
};
