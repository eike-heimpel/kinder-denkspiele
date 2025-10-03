import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { VisualMemoryEngine } from '$lib/services/visual-memory.service';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const { sessionId, userSelections } = await request.json();

        if (!sessionId || !Array.isArray(userSelections)) {
            return json({ error: 'Missing sessionId or userSelections' }, { status: 400 });
        }

        const engine = new VisualMemoryEngine();
        const result = await engine.submitAnswer(sessionId, userSelections);

        if (!result.session.isActive) {
            return json({
                gameOver: true,
                score: result.session.score,
                lives: result.session.lives,
                round: result.session.round,
                previousTargets: result.previousTargets,
                isCorrect: result.isCorrect,
                message: `Spiel vorbei! Du hast ${result.session.score} Runden geschafft!`
            });
        }

        return json({
            gameOver: false,
            score: result.session.score,
            lives: result.session.lives,
            round: result.session.round,
            visualMemoryState: result.session.visualMemoryState,
            previousTargets: result.previousTargets,
            isCorrect: result.isCorrect
        });
    } catch (error) {
        console.error('Error submitting answer:', error);
        return json(
            { error: 'Failed to submit answer' },
            { status: 500 }
        );
    }
};

