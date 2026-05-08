import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	const [sessionsRes, profileRes] = await Promise.all([
		fetch(`/api/proxy/api/sessions?userId=${session.user.id}&limit=50`),
		fetch(`/api/proxy/api/profiles?userId=${session.user.id}`)
	]);

	const sessions = await sessionsRes.json();
	const profile = profileRes.ok ? await profileRes.json() : null;

	return { 
		sessions, 
		user: session.user,
		profile
	};
};
