import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { PUBLIC_BACKEND_URL } from '$env/static/public';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	const res = await fetch(`${PUBLIC_BACKEND_URL}/api/sessions?userId=${session.user.id}&limit=50`);
	const sessions = await res.json();

	return { sessions };
};
