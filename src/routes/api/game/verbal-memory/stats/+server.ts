import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { connectToDatabase } from '$lib/db/client';
import { GameSessionRepository } from '$lib/repositories/game-session.repository';
import type { DifficultyLevel } from '$lib/types';

const sessionRepo = new GameSessionRepository();

export const GET: RequestHandler = async ({ url }) => {
    await connectToDatabase();

    const userId = url.searchParams.get('userId');
    const difficulty = url.searchParams.get('difficulty') as DifficultyLevel;

    if (!userId || !difficulty) {
        return json({ error: 'userId and difficulty are required' }, { status: 400 });
    }

    const stats = await sessionRepo.getStatsByUser(userId, 'verbal-memory', difficulty);
    return json(stats);
};
