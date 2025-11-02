import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Use production URL if set, otherwise fallback to local development
const FASTAPI_URL = env.MAERCHENWEBER_API_URL || 'http://localhost:8000';
const API_KEY = env.MAERCHENWEBER_API_KEY;

export const GET: RequestHandler = async ({ url }) => {
	try {
		const userId = url.searchParams.get('userId');

		if (!userId) {
			return json({ error: 'userId query parameter is required' }, { status: 400 });
		}

		// Build headers - add API key if available (production mode)
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (API_KEY) {
			headers['X-API-Key'] = API_KEY;
		}

		const response = await fetch(`${FASTAPI_URL}/adventure/user/${userId}/sessions`, {
			method: 'GET',
			headers
		});

		if (!response.ok) {
			const error = await response.json();
			return json({ error: error.detail || 'Failed to fetch sessions' }, { status: response.status });
		}

		const data = await response.json();
		return json(data);
	} catch (error) {
		console.error('Error proxying to FastAPI:', error);
		return json(
			{ error: 'Failed to connect to story service. Is the FastAPI server running?' },
			{ status: 500 }
		);
	}
};
