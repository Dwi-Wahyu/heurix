import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import fs from 'fs';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';
import path from 'path';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),

		SvelteKitPWA({
			registerType: 'autoUpdate',
			injectRegister: 'script',
			manifest: {
				name: 'HiReady - Solnetz Dev',
				short_name: 'HiReady',
				description: 'Deskripsi aplikasi HiReady',
				theme_color: '#ffffff',
				background_color: '#ffffff',
				display: 'standalone',
				icons: [
					{
						src: 'web-app-manifest-192x192.png',
						sizes: '192x192',
						type: 'image/png',
						purpose: 'maskable'
					},
					{
						src: 'web-app-manifest-512x512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'maskable'
					}
				]
			},
			workbox: {
				globPatterns: [
					'client/**/*.{js,css,ico,png,svg,webp,webmanifest}'
					// 'prerendered/**/*.{html,json}'
				],
				maximumFileSizeToCacheInBytes: 20 * 1024 * 1024 // 5MB
			}
		})
	],
	ssr: {
		noExternal: ['svelte-chartjs', 'chart.js']
	},
	server: {
		// host: '0.0.0.0',
		host: '192.168.1.38',
		port: 5173,
		https: {
			key: fs.readFileSync(path.resolve(__dirname, 'certs/key.pem')),
			cert: fs.readFileSync(path.resolve(__dirname, 'certs/cert.pem'))
		}
	}
});
