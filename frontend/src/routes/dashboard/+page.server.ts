import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	const [profileRes, sessionsRes] = await Promise.all([
		fetch(`/api/proxy/api/profile/${session.user.id}`),
		fetch(`/api/proxy/api/sessions?userId=${session.user.id}&limit=5`)
	]);

	console.log(profileRes);
	console.log(sessionsRes);

	return {
		user: session.user,
		profile: await profileRes.json(),
		recentSessions: await sessionsRes.json()
	};
};
