import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { LogicLabEngine } from '$lib/services/logic-lab.service';

export const GET: RequestHandler = async ({ url }) => {
	try {
		const sessionId = url.searchParams.get('sessionId');

		if (!sessionId) {
			return json({ error: 'sessionId is required' }, { status: 400 });
		}

		const engine = new LogicLabEngine();
		const stats = await engine.getStats(sessionId);

		if (!stats) {
			return json({ error: 'Game session not found' }, { status: 404 });
		}

		return json(stats);
	} catch (error) {
		console.error('Error retrieving stats:', error);
		return json({ error: 'Failed to retrieve stats' }, { status: 500 });
	}
};
