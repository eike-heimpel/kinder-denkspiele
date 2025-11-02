import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const BACKEND_URL = 'http://localhost:8000';

export const GET: RequestHandler = async ({ params }) => {
	const { sessionId, round } = params;

	try {
		const response = await fetch(`${BACKEND_URL}/adventure/image/${sessionId}/${round}`);

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
