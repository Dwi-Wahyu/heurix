import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	const userId = session.user.id;

	try {
		// 1. Fetch User Profile
		const profileRes = await fetch(`/api/proxy/api/profile/${userId}`);
		const profile = profileRes.ok ? await profileRes.json() : null;

		// 2. Fetch Sessions for analysis
		const sessionsRes = await fetch(`/api/proxy/api/sessions?userId=${userId}&limit=50`);
		const sessions = sessionsRes.ok ? await sessionsRes.json() : [];

		return {
			profile,
			sessions,
			user: session.user
		};
	} catch (err) {
		console.error('Error loading progress data:', err);
		return {
			profile: null,
			sessions: [],
			user: session.user,
			error: 'Gagal memuat data progres.'
		};
	}
};
