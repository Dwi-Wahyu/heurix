import tailwindcss from '@tailwindcss/vite';
import { enhancedImages } from '@sveltejs/enhanced-img';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
// import fs from 'fs';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';

export default defineConfig({
	plugins: [
		enhancedImages(),
		tailwindcss(),
		sveltekit(),

		SvelteKitPWA({
			registerType: 'autoUpdate',
			injectRegister: 'script',
			manifest: {
				name: 'Heurix - Pejantan Tangguh',
				short_name: 'Heurix',
				description: 'Simulasi Wawancara Immersif Dengan AI',
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
	}
	// server: {
	// 	https: {
	// 		key: fs.readFileSync('./certs/key.pem'),
	// 		cert: fs.readFileSync('./certs/cert.pem')
	// 	}
	// }
});
