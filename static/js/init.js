// init.js
import { checkBasketRefresh } from './basketRefresh.js';
import { intialiseCustomerForm } from './customerForm.js';
import { initialiseDjangoMessageToasts } from './djangoMessages.js';
import { initialiseHireLogistics } from './hireLogistics.js';
import { initialiseHtmxListeners } from './htmxListener.js';

document.addEventListener('DOMContentLoaded', () => {
	initialiseHtmxListeners();
	initialiseDjangoMessageToasts();
	intialiseCustomerForm();
	initialiseHireLogistics();
	checkBasketRefresh();
});
