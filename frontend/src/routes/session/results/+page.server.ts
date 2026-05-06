import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { PUBLIC_BACKEND_URL } from '$env/static/public';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, url, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	const sessionId = url.searchParams.get('sessionId');
	if (!sessionId) throw redirect(302, '/dashboard');

	const res = await fetch(`${PUBLIC_BACKEND_URL}/api/sessions/${sessionId}/report`);
	if (!res.ok) {
		// If report not found, maybe it's still being generated
		// or handle error
		return { error: 'Report not found' };
	}
	const data = await res.json();

	return { report: data.report, sessionTurns: data.sessionTurns };
};
