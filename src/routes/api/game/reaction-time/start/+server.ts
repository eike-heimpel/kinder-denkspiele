import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { ReactionTimeEngine } from '$lib/services/reaction-time.service';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const { userId, difficulty } = await request.json();

        if (!userId || !difficulty) {
            return json({ error: 'Missing userId or difficulty' }, { status: 400 });
        }

        if (difficulty !== 'easy' && difficulty !== 'hard') {
            return json({ error: 'Invalid difficulty level' }, { status: 400 });
        }

        const engine = new ReactionTimeEngine();
        const gameSession = await engine.startGame(userId, difficulty);

        return json({
            sessionId: gameSession._id,
            score: gameSession.score,
            round: gameSession.round,
            reactionTimeState: gameSession.reactionTimeState
        });
    } catch (error) {
        console.error('Error starting reaction time game:', error);
        return json(
            { error: 'Failed to start game' },
            { status: 500 }
        );
    }
};

