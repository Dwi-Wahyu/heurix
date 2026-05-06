import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import fs from 'fs';
import path from 'path';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		// host: '0.0.0.0',
		host: '192.168.1.227',
		port: 5173,
		https: {
			key: fs.readFileSync(path.resolve(__dirname, 'certs/key.pem')),
			cert: fs.readFileSync(path.resolve(__dirname, 'certs/cert.pem'))
		}
	}
});
