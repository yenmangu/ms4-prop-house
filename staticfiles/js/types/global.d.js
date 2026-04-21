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
