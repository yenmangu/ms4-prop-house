document.addEventListener('DOMContentLoaded', () => {
	const tables = document.querySelectorAll('#result_list');
	if (!tables) return;

	const adminTables = /** @type {NodeListOf<HTMLTableElement>} */ (tables);

	adminTables.forEach(table => {
		const cols = table.querySelectorAll('th');
		cols.forEach(col => {
			const resizer = document.createElement('div');

			resizer.classList.add('resizer');
			col.appendChild(resizer);

			let x = 0;
			let w = 0;

			/**
			 *
			 * @param {MouseEvent} e
			 */
			const onMouseMove = e => {
				const dx = e.clientX - x;
				col.style.width = `${w + dx}px`;
			};
			const onMouseUp = () => {
				document.removeEventListener('mousemove', onMouseMove);
				document.removeEventListener('mouseup', onMouseUp);

				resizer.classList.remove('resizing');
			};

			resizer.addEventListener('mousedown', e => {
				x = e.clientX;
				w = parseInt(window.getComputedStyle(col).width, 10);

				document.addEventListener('mousemove', onMouseMove);
				document.addEventListener('mouseup', onMouseUp);

				resizer.classList.add('resizing');
				e.preventDefault();
			});
		});
	});
});
