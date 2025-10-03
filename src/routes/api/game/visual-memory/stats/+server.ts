import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { VisualMemoryEngine } from '$lib/services/visual-memory.service';

export const GET: RequestHandler = async ({ url }) => {
    try {
        const userId = url.searchParams.get('userId');
        const difficulty = url.searchParams.get('difficulty') as 'easy' | 'hard' | null;

        if (!userId) {
            return json({ error: 'Missing userId' }, { status: 400 });
        }

        const engine = new VisualMemoryEngine();

        if (difficulty) {
            const stats = await engine.getStats(userId, difficulty);
            return json(stats);
        } else {
            const stats = await engine.getStats(userId);
            return json(stats);
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
        return json(
            { error: 'Failed to fetch stats' },
            { status: 500 }
        );
    }
};

