import type { PageServerLoad, Actions } from './$types';
import { redirect, fail } from '@sveltejs/kit';
import { PUBLIC_BACKEND_URL } from '$env/static/public';
import { auth } from '$lib/server/auth';

export const load: PageServerLoad = async ({ fetch, request }) => {
	const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

	const [instRes, posRes] = await Promise.all([
		fetch(`${PUBLIC_BACKEND_URL}/api/institutions`),
		fetch(`${PUBLIC_BACKEND_URL}/api/positions`)
	]);

	return {
		institutions: await instRes.json(),
		positions: await posRes.json()
	};
};

export const actions: Actions = {
	default: async ({ request, fetch }) => {
		const session = await auth.api.getSession({ headers: request.headers });
		if (!session) throw redirect(302, '/login');

		const data = await request.formData();
		const institutionId = data.get('institutionId') as string;
		const positionId = data.get('positionId') as string;
		const preferredTrack = data.get('path') as string;

		if (!institutionId || !positionId || !preferredTrack) {
			return fail(400, { message: 'Pilih institusi, posisi, dan jalur terlebih dahulu.' });
		}

		// Simpan ke profil user via backend
		await fetch(`${PUBLIC_BACKEND_URL}/api/profile`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				userId: session.user.id,
				targetInstitutionId: institutionId,
				targetPositionId: positionId,
				preferredTrack: preferredTrack
			})
		});

		throw redirect(302, '/dashboard');
	}
};
