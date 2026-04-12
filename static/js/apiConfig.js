import { getCookie } from './getCookie.js';

export const getStandardHeaders = () => ({
	'Content-Type': 'application/json',
	'X-CSRFToken': getCookie('csrftoken') || '',
	'X-Requested-With': 'XMLHttpRequest'
});
