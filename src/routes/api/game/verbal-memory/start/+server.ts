import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { connectToDatabase } from '$lib/db/client';
import { GameEngine } from '$lib/services/game-engine.service';
import type { DifficultyLevel } from '$lib/types';

export const POST: RequestHandler = async ({ request }) => {
    await connectToDatabase();

    const { userId, difficulty } = await request.json();

    if (!userId || !difficulty) {
        return json({ error: 'userId and difficulty are required' }, { status: 400 });
    }

    if (difficulty !== 'easy' && difficulty !== 'hard' && difficulty !== 'extra-hard') {
        return json({ error: 'difficulty must be "easy", "hard", or "extra-hard"' }, { status: 400 });
    }

    const engine = new GameEngine();
    const gameState = await engine.startGame(userId, difficulty as DifficultyLevel);

    return json({
        sessionId: gameState.session?._id,
        currentWord: gameState.currentWord,
        score: gameState.session?.score,
        lives: gameState.session?.lives,
        round: gameState.session?.round,
        // Debug info
        debug: {
            wordsShown: gameState.session?.wordsShown || [],
            seenWords: Array.from(gameState.session?.seenWords || []),
            isCurrentWordNew: gameState.isCurrentWordNew
        }
    });
};
