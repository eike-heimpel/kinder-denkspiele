import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { dev } from '$app/environment';

const SITE_PASSWORD = import.meta.env.VITE_SITE_PASSWORD || 'kinderspiele2024';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { password } = await request.json();

	if (password === SITE_PASSWORD) {
		// Set cookie that expires in 7 days
		cookies.set('authenticated', 'true', {
			path: '/',
			httpOnly: true,
			secure: !dev, // Only secure in production (HTTPS)
			sameSite: 'strict',
			maxAge: 60 * 60 * 24 * 7 // 7 days
		});

		return json({ success: true });
	}

	return json({ error: 'Falsches Passwort' }, { status: 401 });
};

