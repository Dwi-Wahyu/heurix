import { db } from '$lib/server/db';
import * as schema from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { error, redirect, isRedirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';

export const load = async ({ url, request }) => {
    const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

    const avatarId = url.searchParams.get('avatarId');
    if (!avatarId) {
        throw error(400, 'Avatar ID is required');
    }

    try {
        const [avatar, profile] = await Promise.all([
             db.query.interviewAvatar.findFirst({
                where: eq(schema.interviewAvatar.id, avatarId)
            }),
            db.query.userProfile.findFirst({
                where: eq(schema.userProfile.userId, session.user.id),
                with: {
                    targetInstitution: true
                }
            })
        ]);

        if (!avatar) {
            throw error(404, 'Avatar not found');
        }

        return {
            avatar,
            track: profile?.targetInstitution?.track || profile?.preferredTrack || 'corporate'
        };
    } catch (e) {
        if (isRedirect(e)) throw e;
        console.error('Failed to load disclaimer data:', e);
        throw error(500, 'Internal Server Error');
    }
};
