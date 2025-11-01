import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { VisualMemoryEngine } from '$lib/services/visual-memory.service';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const { userId, difficulty } = await request.json();

        if (!userId || !difficulty) {
            return json({ error: 'Missing userId or difficulty' }, { status: 400 });
        }

        if (difficulty !== 'easy' && difficulty !== 'hard' && difficulty !== 'extra-hard') {
            return json({ error: 'Invalid difficulty level' }, { status: 400 });
        }

        const engine = new VisualMemoryEngine();
        const gameSession = await engine.startGame(userId, difficulty);

        return json({
            sessionId: gameSession._id,
            score: gameSession.score,
            lives: gameSession.lives,
            round: gameSession.round,
            visualMemoryState: gameSession.visualMemoryState
        });
    } catch (error) {
        console.error('Error starting visual memory game:', error);
        return json(
            { error: 'Failed to start game' },
            { status: 500 }
        );
    }
};

