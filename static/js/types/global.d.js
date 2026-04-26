/**
 * @namespace BasketTypes
 */

/**
 * @typedef {Object} BasketState
 * @property {string} status
 * @property {string} message
 * @property {number} total_items
 * @property {string} total_price
 * @property {boolean} [is_empty]
 */

/**
 * @typedef {Object} BasketUpdateReport
 * @property {AllowedAction} action
 * @property {string} endpoint
 * @property {string} [product_id] - Optional for 'clear' action
 * @property {number} [quantity=1]
 */

/**
 * @typedef {'add'|'remove'|'clear'} AllowedAction
 *
 */

/**
 * Typing declaration for HTMX AfterRequest detail property.
 *
 * @see https://htmx.org/events/#htmx:afterRequest
 *
 * @typedef {Object} AfterRequestDetail
 * @property {Element} elt
 * @property {unknown} target
 * @property {XMLHttpRequest} xhr
 * @property {object} requestConfig
 * @property {boolean} [successful]
 * @property {boolean} [isError]
 * @property {boolean} [failed]
 */

/**
 * @typedef {CustomEvent<AfterRequestDetail>} AfterRequestEvent
 */

/**
 * Type declaration for `detail` property of
 * HTMX AfterSettle Object
 * @see https://htmx.org/events/#htmx:afterSettle
 *
 * @typedef {object} AfterSettleDetail
 * @property {Element} elt
 * @property {XMLHttpRequest} xhr
 * @property {unknown} target
 * @property {object} requestConfig
 */

/**
 * @typedef {CustomEvent<AfterSettleDetail>} AfterSettleEvent
 */
