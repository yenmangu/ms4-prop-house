export const getRenderDrawerState = () => {
	const drawerStateScript = document.getElementById('drawer-render-state');

	if (!(drawerStateScript instanceof HTMLScriptElement)) {
		return false;
	}

	return JSON.parse(drawerStateScript.textContent || 'false');
};
