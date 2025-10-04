import { redirect, type Handle } from '@sveltejs/kit';

const SITE_PASSWORD = import.meta.env.VITE_SITE_PASSWORD || 'kinderspiele2024';

export const handle: Handle = async ({ event, resolve }) => {
	const sessionCookie = event.cookies.get('authenticated');
	const isLoginPage = event.url.pathname === '/login';
	const isAuthApi = event.url.pathname.startsWith('/api/auth');

	// Allow auth API endpoints to be accessed
	if (isAuthApi) {
		return resolve(event);
	}

	// If not authenticated and not on login page, redirect to login
	if (!sessionCookie && !isLoginPage) {
		throw redirect(303, '/login');
	}

	// If authenticated and on login page, redirect to home
	if (sessionCookie && isLoginPage) {
		throw redirect(303, '/');
	}

	return resolve(event);
};

