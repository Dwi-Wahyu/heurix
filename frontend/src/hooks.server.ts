import { dev } from '$app/environment';

if (dev) {
	// Allow self-signed certificates in development for server-side fetches
	process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
	console.log('Development mode: NODE_TLS_REJECT_UNAUTHORIZED set to 0');
}

export {};
