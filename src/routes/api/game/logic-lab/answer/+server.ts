import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { LogicLabEngine } from '$lib/services/logic-lab.service';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { sessionId, answerIndex } = await request.json();

		if (!sessionId || answerIndex === undefined) {
			return json({ error: 'sessionId and answerIndex are required' }, { status: 400 });
		}

		if (typeof answerIndex !== 'number' || answerIndex < 0 || answerIndex > 3) {
			return json({ error: 'answerIndex must be a number between 0 and 3' }, { status: 400 });
		}

		const engine = new LogicLabEngine();
		const result = await engine.submitAnswer(sessionId, answerIndex);

		if (!result) {
			return json({ error: 'Game session not found' }, { status: 404 });
		}

		return json(result);
	} catch (error) {
		console.error('Error submitting answer:', error);
		return json({ error: 'Failed to submit answer' }, { status: 500 });
	}
};
