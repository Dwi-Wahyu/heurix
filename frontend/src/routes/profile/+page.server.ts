import { db } from '$lib/server/db';
import { userProfile } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request }) => {
    const session = await auth.api.getSession({ headers: request.headers });
    if (!session) {
        throw redirect(303, '/login');
    }

    const profile = await db.query.userProfile.findFirst({
        where: eq(userProfile.userId, session.user.id),
        with: {
            targetInstitution: true,
            targetPosition: true
        }
    });

    return {
        user: session.user,
        profile: profile ?? null
    };
};
