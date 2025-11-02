import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const FASTAPI_URL = env.MAERCHENWEBER_API_URL || 'http://localhost:8000';
const API_KEY = env.MAERCHENWEBER_API_KEY;

export const GET: RequestHandler = async ({ params }) => {
	const { sessionId, round } = params;

	try {
		// Build headers
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};

		if (API_KEY) {
			headers['X-API-Key'] = API_KEY;
		}

		const response = await fetch(`${FASTAPI_URL}/adventure/image/${sessionId}/${round}`, {
			method: 'GET',
			headers
		});

		if (!response.ok) {
			return json(
				{
					status: 'error',
					round: parseInt(round),
					image_url: null,
					error: `Backend error: ${response.status}`
				},
				{ status: response.status }
			);
		}

		const data = await response.json();
		return json(data);
	} catch (error) {
		console.error('Error polling for image:', error);
		return json(
			{
				status: 'error',
				round: parseInt(round),
				image_url: null,
				error: 'Failed to connect to backend'
			},
			{ status: 500 }
		);
	}
};
