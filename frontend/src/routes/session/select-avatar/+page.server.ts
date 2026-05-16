import { db } from '$lib/server/db';
import * as schema from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { error, redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';

export const load = async ({ request }) => {
    const session = await auth.api.getSession({ headers: request.headers });
	if (!session) throw redirect(302, '/login');

    try {
        // Get user profile to check for default institution avatar
        const profile = await db.query.userProfile.findFirst({
            where: eq(schema.userProfile.userId, session.user.id),
            with: {
                targetInstitution: true
            }
        });

        if (profile?.targetInstitution?.defaultAvatarId) {
             throw redirect(302, `/session/disclaimer?avatarId=${profile.targetInstitution.defaultAvatarId}`);
        }

        const avatars = await db.select({
            id: schema.interviewAvatar.id,
            name: schema.interviewAvatar.name,
            track: schema.interviewAvatar.track,
            glbUrl: schema.interviewAvatar.glbUrl,
            thumbnailUrl: schema.interviewAvatar.thumbnailUrl,
        })
        .from(schema.interviewAvatar)
        .where(eq(schema.interviewAvatar.isActive, true));

        return {
            avatars
        };
    } catch (e) {
        if (e instanceof redirect) throw e;
        console.error('Failed to load avatars:', e);
        throw error(500, 'Internal Server Error');
    }
};
