import { db } from '$lib/server/db';
import * as schema from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';

export const load = async ({ url }) => {
    const avatarId = url.searchParams.get('avatarId');
    if (!avatarId) {
        throw error(400, 'Avatar ID is required');
    }

    try {
        const avatar = await db.query.interviewAvatar.findFirst({
            where: eq(schema.interviewAvatar.id, avatarId)
        });

        if (!avatar) {
            throw error(404, 'Avatar not found');
        }

        return {
            avatar
        };
    } catch (e) {
        console.error('Failed to load avatar:', e);
        throw error(500, 'Internal Server Error');
    }
};
