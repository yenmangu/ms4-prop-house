// init.js
import { intialiseCustomerForm } from './customerForm.js';
import { initialiseHireLogistics } from './hireLogistics.js';
import { initialiseHtmxListeners } from './htmxListener.js';

document.addEventListener('DOMContentLoaded', () => {
	initialiseHtmxListeners();
	intialiseCustomerForm();
	initialiseHireLogistics();
});
