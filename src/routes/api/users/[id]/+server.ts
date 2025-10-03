import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { connectToDatabase } from '$lib/db/client';
import { UserRepository } from '$lib/repositories/user.repository';

const userRepo = new UserRepository();

export const GET: RequestHandler = async ({ params }) => {
    await connectToDatabase();
    const user = await userRepo.findById(params.id);

    if (!user) {
        return json({ error: 'User not found' }, { status: 404 });
    }

    return json(user);
};

export const DELETE: RequestHandler = async ({ params }) => {
    await connectToDatabase();
    const deleted = await userRepo.delete(params.id);

    if (!deleted) {
        return json({ error: 'User not found' }, { status: 404 });
    }

    return json({ success: true });
};
