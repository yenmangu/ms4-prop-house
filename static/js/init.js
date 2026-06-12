// init.js
import { checkBasketRefresh } from './basketRefresh.js';
import { intialiseCustomerForm } from './customerForm.js';
import { initialiseDjangoMessageToasts } from './djangoMessages.js';
import { initialiseHireLogistics } from './hireLogistics.js';
import { initialiseHtmxListeners } from './htmxListener.js';
import { initialiseSidebarFormSync } from './syncForms.js';

document.addEventListener('DOMContentLoaded', () => {
	initialiseHtmxListeners();
	initialiseDjangoMessageToasts();
	initialiseSidebarFormSync();
	intialiseCustomerForm();
	initialiseHireLogistics();
	checkBasketRefresh();
});
