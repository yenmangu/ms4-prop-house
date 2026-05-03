import { intialiseCustomerForm } from './customerForm.js';
import { initialiseHtmxListeners } from './htmxListener.js';

//
document.addEventListener('DOMContentLoaded', () => {
	initialiseHtmxListeners();
	intialiseCustomerForm();
});
