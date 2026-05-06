import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { PUBLIC_BACKEND_URL } from '$env/static/public';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	let apiUrl = PUBLIC_BACKEND_URL;
	// In local dev with self-signed certs, we might need to switch to https
	// if the backend is now running with the frontend certs.
	if (apiUrl.startsWith('http://172.17.0.1')) {
		// Try to see if we should use https
		// For server-side fetch, it depends on how the backend was started
	}

	const [profileRes, sessionsRes] = await Promise.all([
		fetch(`${apiUrl}/api/profile/${session.user.id}`),
		fetch(`${apiUrl}/api/sessions?userId=${session.user.id}&limit=5`)
	]);

	console.log(profileRes);
	console.log(sessionsRes);

	return {
		user: session.user,
		profile: await profileRes.json(),
		recentSessions: await sessionsRes.json()
	};
};
