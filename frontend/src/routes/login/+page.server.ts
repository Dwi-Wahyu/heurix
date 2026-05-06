import { fail, redirect } from '@sveltejs/kit';
import { auth } from '$lib/server/auth';
import { APIError } from 'better-auth/api';
import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/server/db';

export const load: PageServerLoad = async ({ locals }) => {
	console.log(locals);

	if (locals.user) {
		return redirect(302, `/dashboard`);
	}

	return { user: locals.user };
};
