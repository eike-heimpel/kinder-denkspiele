import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ cookies }) => {
    cookies.delete('authenticated', { path: '/' });
    return json({ success: true });
};

