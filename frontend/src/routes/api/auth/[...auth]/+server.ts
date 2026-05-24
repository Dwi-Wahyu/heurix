// import { auth } from '$lib/server/auth';

// export const GET = ({ request }) => auth.handler(request);
// export const POST = ({ request }) => auth.handler(request);

import { auth } from '$lib/server/auth';
import { toSvelteKitHandler } from 'better-auth/svelte-kit';

export const GET = toSvelteKitHandler(auth);
export const POST = toSvelteKitHandler(auth);
