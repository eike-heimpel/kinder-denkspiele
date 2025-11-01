import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { LogicLabEngine } from '$lib/services/logic-lab.service';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { userId } = await request.json();

		if (!userId) {
			return json({ error: 'userId is required' }, { status: 400 });
		}

		const engine = new LogicLabEngine();
		await engine.resetProgress(userId);

		return json({ success: true });
	} catch (error) {
		console.error('Error resetting Logic Lab progress:', error);
		return json({ error: 'Failed to reset progress' }, { status: 500 });
	}
};
