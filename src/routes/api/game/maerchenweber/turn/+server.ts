import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const FASTAPI_URL = 'http://localhost:8000';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();

		const response = await fetch(`${FASTAPI_URL}/adventure/turn`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(body)
		});

		if (!response.ok) {
			const error = await response.json();
			return json({ error: error.detail || 'Failed to process turn' }, { status: response.status });
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
