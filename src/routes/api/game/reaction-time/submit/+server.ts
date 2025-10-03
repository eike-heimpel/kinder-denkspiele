import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { ReactionTimeEngine } from '$lib/services/reaction-time.service';

export const POST: RequestHandler = async ({ request }) => {
    try {
        const { sessionId, reactionTime, isFalseStart } = await request.json();

        if (!sessionId || (reactionTime === undefined && !isFalseStart)) {
            return json({ error: 'Missing sessionId or reactionTime' }, { status: 400 });
        }

        const engine = new ReactionTimeEngine();
        const updatedSession = await engine.submitReaction(sessionId, reactionTime || 0, isFalseStart || false);

        if (!updatedSession.isActive) {
            return json({
                gameOver: true,
                score: updatedSession.score,
                reactionTimeState: updatedSession.reactionTimeState,
                message: `Durchschnittliche Reaktionszeit: ${updatedSession.score}ms`
            });
        }

        return json({
            gameOver: false,
            score: updatedSession.score,
            reactionTimeState: updatedSession.reactionTimeState
        });
    } catch (error) {
        console.error('Error submitting reaction:', error);
        return json(
            { error: 'Failed to submit reaction' },
            { status: 500 }
        );
    }
};

