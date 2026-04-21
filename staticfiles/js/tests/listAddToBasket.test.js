// @ts-check
import { _addToBasket } from '../listAddToBasket.js';
import * as globalNav from '../globalNav.js';
import * as reportError from '../reportError.js';

// Mock the dependencies
jest.mock('./globalNav.js');
jest.mock('./reportError.js');
jest.mock('./getCookie.js', () => ({
	getCookie: () => 'csrf-test-token'
}));

describe('listAddToBasket.js: _addToBasket', () => {
	/** @type {jest.SpyInstance} */
	let fetchSpy;
	beforeEach(() => {
		//  @ts-ignore
		jest.spyOn(global, 'fetch').mockImplementationOnce(() => {
			Promise.resolve({
				ok: true,
				json: () =>
					Promise.resolve({
						total_items: 0,
						total_price: '0.00'
					})
			});
		});

		jest.clearAllMocks();
	});

	afterEach(() => {
		// @ts-ignore
		fetchSpy.mockRestore();
	});

	test('calls updateGlobalNav with correct destructured data on success', async () => {
		const mockResponse = {
			total_items: 3,
			total_price: '15.99',
			message: 'Added!'
		};
		// @ts-ignore
		fetchSpy.mockResolvedValueOnce({
			ok: true,
			json: async () => mockResponse
		});

		await _addToBasket('prod_123');

		// Verify the "Contract"
		expect(globalNav.updateGlobalNav).toHaveBeenCalledWith(3, '15.99');
		expect(reportError.phNotify).toHaveBeenCalledWith('Added!', 'success');
	});

	test('reports error when the server returns 400/500', async () => {
		// @ts-ignore
		fetchSpy.mockResolvedValueOnce({
			ok: false,
			status: 400,
			json: async () => ({ error: 'Out of stock' })
		});

		try {
			await _addToBasket('prod_123');
		} catch (e) {
			// Logic should trigger phReportError
			expect(reportError.phReportError).toHaveBeenCalledWith(
				expect.any(Error),
				'NETWORK'
			);
		}
	});
});
