import { dev } from '$app/environment';

// Allow self-signed certificates for server-side fetches in dev and preview
// This is necessary because both frontend and backend use local self-signed certs
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

if (dev) {
	console.log('Development mode: NODE_TLS_REJECT_UNAUTHORIZED set to 0');
} else {
	console.log('Production/Preview mode: NODE_TLS_REJECT_UNAUTHORIZED set to 0 (for local testing)');
}

export {};
