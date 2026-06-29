export const checkBasketRefresh = () => {
	const refreshMarker = document.querySelector('[data-basket-refresh="true"]');
	//@ts-ignore
	if (refreshMarker && window.htmx) {
		// @ts-ignore
		window.htmx.trigger('body', 'basketUpdated');
	}
};
