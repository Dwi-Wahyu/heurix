import { createAuthClient } from 'better-auth/svelte';
import { customSessionClient } from 'better-auth/client/plugins';
import type { auth } from '$lib/server/auth';

export const authClient = createAuthClient({
	plugins: [customSessionClient<typeof auth>()]
});
