import { db } from '$lib/server/db';
import * as schema from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { error, redirect, isRedirect } from '@sveltejs/kit';
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

        // Always redirect if we can find an avatar
        if (profile?.targetInstitution?.defaultAvatarId) {
             throw redirect(302, `/session/disclaimer?avatarId=${profile.targetInstitution.defaultAvatarId}`);
        }

        // Fallback: Pick the first active avatar for the track
        const track = profile?.preferredTrack || profile?.targetInstitution?.track || 'corporate';
        const fallbackAvatar = await db.query.interviewAvatar.findFirst({
            where: eq(schema.interviewAvatar.track, track as any),
        });

        if (fallbackAvatar) {
            throw redirect(302, `/session/disclaimer?avatarId=${fallbackAvatar.id}`);
        }

        // Final fallback: any active avatar
        const anyAvatar = await db.query.interviewAvatar.findFirst();
        if (anyAvatar) {
            throw redirect(302, `/session/disclaimer?avatarId=${anyAvatar.id}`);
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
        if (isRedirect(e)) throw e;
        console.error('Failed to load avatars:', e);
        throw error(500, 'Internal Server Error');
    }
};
