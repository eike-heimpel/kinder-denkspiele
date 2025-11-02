import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const FASTAPI_URL = env.MAERCHENWEBER_API_URL || 'http://localhost:8000';
const API_KEY = env.MAERCHENWEBER_API_KEY;

export const GET: RequestHandler = async ({ params }) => {
	try {
		const { sessionId } = params;

		// Build headers
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (API_KEY) {
			headers['X-API-Key'] = API_KEY;
		}

		console.log(`[Märchenweber] Polling status for session: ${sessionId}`);

		const response = await fetch(`${FASTAPI_URL}/adventure/status/${sessionId}`, {
			method: 'GET',
			headers,
			signal: AbortSignal.timeout(5000) // 5 second timeout for polling
		});

		if (!response.ok) {
			let errorDetail = 'Unknown error';
			try {
				const error = await response.json();
				errorDetail = error.detail || error.error || JSON.stringify(error);
			} catch (e) {
				const textError = await response.text();
				errorDetail = textError || `HTTP ${response.status}`;
			}

			console.error(`[Märchenweber] Status polling error:`, errorDetail);
			return json(
				{
					error: `Backend error: ${errorDetail}`,
					status: response.status
				},
				{ status: response.status }
			);
		}

		const data = await response.json();
		console.log(`[Märchenweber] Status: ${data.status}`);

		return json(data);
	} catch (error) {
		console.error('[Märchenweber] Error polling status:', error);

		return json(
			{
				error: 'Failed to poll story status',
				details: error instanceof Error ? error.message : String(error)
			},
			{ status: 500 }
		);
	}
};
