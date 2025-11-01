import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { LogicLabEngine } from '$lib/services/logic-lab.service';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { userId, age, guidance } = await request.json();

		if (!userId || !age) {
			return json({ error: 'userId and age are required' }, { status: 400 });
		}

		if (typeof age !== 'number' || age < 4 || age > 10) {
			return json({ error: 'age must be between 4 and 10' }, { status: 400 });
		}

		const engine = new LogicLabEngine();
		const session = await engine.startGame({
			userId,
			age,
			guidance: guidance?.trim() || undefined
		});

		const state = session.logicLabState!;

		return json({
			sessionId: session._id?.toString(),
			problem: {
				question: state.currentProblem.question,
				options: state.currentProblem.options,
				type: state.currentProblem.type,
				difficulty: state.currentProblem.difficultyLevel
			},
			score: session.score,
			lives: session.lives,
			round: session.round,
			totalRounds: state.totalProblems,
			// Debug info for parents
			difficultyLevel: state.currentDifficultyLevel,
			consecutiveCorrect: state.consecutiveCorrect,
			consecutiveIncorrect: state.consecutiveIncorrect
		});
	} catch (error) {
		console.error('Error starting Logic Lab game:', error);
		return json({ error: 'Failed to start game' }, { status: 500 });
	}
};
