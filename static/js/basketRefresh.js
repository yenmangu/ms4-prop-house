export const checkBasketRefresh = () => {
	const refreshMarker = document.querySelector('[data-zone="basket-refresh"]');
	//@ts-ignore
	if (refreshMarker && window.htmx) {
		// @ts-ignore
		window.htmx.trigger('body', 'basketUpdated');
	}
};
