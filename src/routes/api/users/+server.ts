import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { connectToDatabase } from '$lib/db/client';
import { UserRepository } from '$lib/repositories/user.repository';

const userRepo = new UserRepository();

export const GET: RequestHandler = async () => {
    await connectToDatabase();
    const users = await userRepo.findAll();
    return json(users);
};

export const POST: RequestHandler = async ({ request }) => {
    await connectToDatabase();
    const { name, avatar } = await request.json();

    if (!name || typeof name !== 'string' || name.trim().length === 0) {
        return json({ error: 'Name is required' }, { status: 400 });
    }

    if (!avatar || typeof avatar !== 'string' || avatar.trim().length === 0) {
        return json({ error: 'Avatar is required' }, { status: 400 });
    }

    const user = await userRepo.create(name.trim(), avatar.trim());
    return json(user, { status: 201 });
};
