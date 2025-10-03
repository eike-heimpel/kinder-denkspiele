import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { connectToDatabase } from '$lib/db/client';
import { GameEngine } from '$lib/services/game-engine.service';

export const POST: RequestHandler = async ({ request }) => {
    await connectToDatabase();

    const { sessionId, answer } = await request.json();

    if (!sessionId || !answer) {
        return json({ error: 'sessionId and answer are required' }, { status: 400 });
    }

    if (answer !== 'seen' && answer !== 'new') {
        return json({ error: 'answer must be "seen" or "new"' }, { status: 400 });
    }

    const engine = new GameEngine();
    await engine.loadGame(sessionId); // Loads session and restores current word state
    const gameState = await engine.submitAnswer(answer); // Validates against stored word

    return json({
        currentWord: gameState.currentWord,
        score: gameState.session?.score,
        lives: gameState.session?.lives,
        round: gameState.session?.round,
        gameOver: gameState.gameOver,
        message: gameState.message
    });
};
