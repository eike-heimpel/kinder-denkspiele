import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Use production URL if set, otherwise fallback to local development
const FASTAPI_URL = env.MAERCHENWEBER_API_URL || 'http://localhost:8000';
const API_KEY = env.MAERCHENWEBER_API_KEY;

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();

		// Build headers - add API key if available (production mode)
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (API_KEY) {
			headers['X-API-Key'] = API_KEY;
		}

		console.log(`[Märchenweber] Calling backend: ${FASTAPI_URL}/adventure/start`);
		console.log(`[Märchenweber] API Key configured: ${!!API_KEY}`);

		// Call start endpoint (returns immediately with session_id)
		const response = await fetch(`${FASTAPI_URL}/adventure/start`, {
			method: 'POST',
			headers,
			body: JSON.stringify(body),
			signal: AbortSignal.timeout(10000) // 10 second timeout (should be fast now)
		});

		console.log(`[Märchenweber] Backend response status: ${response.status}`);

		if (!response.ok) {
			let errorDetail = 'Unknown error';
			try {
				const error = await response.json();
				errorDetail = error.detail || error.error || JSON.stringify(error);
			} catch (e) {
				const textError = await response.text();
				errorDetail = textError || `HTTP ${response.status}`;
			}

			console.error(`[Märchenweber] Backend error:`, errorDetail);
			return json(
				{
					error: `Backend error: ${errorDetail}`,
					status: response.status,
					backendUrl: FASTAPI_URL
				},
				{ status: response.status }
			);
		}

		const data = await response.json();

		// Data now has: { session_id, status: "generating", message }
		// Return this so frontend can start polling
		return json(data);
	} catch (error) {
		console.error('[Märchenweber] Error proxying to FastAPI:', error);

		// More detailed error message
		let errorMessage = 'Failed to connect to story service';
		if (error instanceof Error) {
			if (error.name === 'AbortError') {
				errorMessage = 'Request to backend timed out after 60 seconds';
			} else if (error.message.includes('fetch')) {
				errorMessage = `Network error: ${error.message}`;
			} else {
				errorMessage = error.message;
			}
		}

		return json(
			{
				error: errorMessage,
				backendUrl: FASTAPI_URL,
				hasApiKey: !!API_KEY,
				details: error instanceof Error ? error.message : String(error)
			},
			{ status: 500 }
		);
	}
};
