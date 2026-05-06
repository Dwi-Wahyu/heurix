import { db } from '$lib/server/db';
import * as schema from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';

export const load = async () => {
    try {
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
        console.error('Failed to load avatars:', e);
        throw error(500, 'Internal Server Error');
    }
};
