import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { LogicLabEngine } from '$lib/services/logic-lab.service';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { userId, difficulty, initialGuidance } = await request.json();

		if (!userId || !difficulty) {
			return json({ error: 'userId and difficulty are required' }, { status: 400 });
		}

		if (difficulty !== 'easy' && difficulty !== 'hard') {
			return json({ error: 'difficulty must be "easy" or "hard"' }, { status: 400 });
		}

		const engine = new LogicLabEngine();
		const session = await engine.startGame({
			userId,
			difficulty,
			initialGuidance: initialGuidance?.trim() || undefined
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
