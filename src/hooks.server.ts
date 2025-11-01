import { redirect, type Handle } from '@sveltejs/kit';

const SITE_PASSWORD = import.meta.env.GLOBA_SITE_PASSWORD || 'kinderspiele2024';

export const handle: Handle = async ({ event, resolve }) => {
	const sessionCookie = event.cookies.get('authenticated');
	const adminCookie = event.cookies.get('admin_authenticated');
	const isLoginPage = event.url.pathname === '/login';
	const isAdminLoginPage = event.url.pathname === '/admin/login';
	const isAdminPage = event.url.pathname === '/admin';
	const isAuthApi = event.url.pathname.startsWith('/api/auth');
	const isAdminApi = event.url.pathname.startsWith('/api/admin');

	// Allow auth API endpoints to be accessed
	if (isAuthApi || isAdminApi) {
		return resolve(event);
	}

	// Admin page requires both site auth and admin auth
	if (isAdminPage && !adminCookie) {
		throw redirect(303, '/admin/login');
	}

	// Admin login page only requires site auth
	if (isAdminLoginPage && adminCookie) {
		throw redirect(303, '/admin');
	}

	// If not authenticated and not on login page, redirect to login
	if (!sessionCookie && !isLoginPage && !isAdminLoginPage) {
		throw redirect(303, '/login');
	}

	// If authenticated and on login page, redirect to home
	if (sessionCookie && isLoginPage) {
		throw redirect(303, '/');
	}

	return resolve(event);
};

