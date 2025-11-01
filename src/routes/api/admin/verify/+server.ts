import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const SITE_PASSWORD = import.meta.env.GLOBA_SITE_PASSWORD || 'kinderspiele2024';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { password } = await request.json();

	if (password === SITE_PASSWORD) {
		cookies.set('admin_authenticated', 'true', {
			path: '/',
			httpOnly: true,
			secure: true,
			sameSite: 'strict',
			maxAge: 60 * 60 * 2 // 2 hours
		});

		return json({ success: true });
	}

	return json({ success: false, error: 'Falsches Passwort' }, { status: 401 });
};
