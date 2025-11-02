import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const FASTAPI_URL = 'http://localhost:8000';

export const GET: RequestHandler = async ({ url }) => {
	try {
		const userId = url.searchParams.get('userId');

		if (!userId) {
			return json({ error: 'userId query parameter is required' }, { status: 400 });
		}

		const response = await fetch(`${FASTAPI_URL}/adventure/user/${userId}/sessions`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
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
