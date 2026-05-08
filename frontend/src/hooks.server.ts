import { dev } from '$app/environment';
import { PUBLIC_BACKEND_URL } from '$env/static/public';

// Allow self-signed certificates for server-side fetches in dev and preview
// This is necessary because both frontend and backend use local self-signed certs
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

if (dev) {
	console.log('--- [INFO] Local Development SSL bypass enabled (NODE_TLS_REJECT_UNAUTHORIZED=0) ---');
}

import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	// Jika request dimulai dengan /api/proxy
	if (event.url.pathname.startsWith('/api/proxy')) {
		const backendUrl = PUBLIC_BACKEND_URL;
		const path = event.url.pathname.replace('/api/proxy', '');

		// Ambil data dari backend asli
		const response = await fetch(`${backendUrl}${path}${event.url.search}`, {
			method: event.request.method,
			headers: event.request.headers,
			body: event.request.method !== 'GET' ? await event.request.blob() : undefined
		});

		return response;
	}

	return resolve(event);
};
