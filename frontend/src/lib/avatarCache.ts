// Simple in-memory cache for GLB buffers to avoid redundant network requests in the same session
const cache = new Map<string, ArrayBuffer>();

export async function loadGLBCached(url: string): Promise<ArrayBuffer> {
	if (cache.has(url)) {
		console.log('[AvatarCache] Hit:', url);
		return cache.get(url)!;
	}

	console.log('[AvatarCache] Miss, fetching:', url);
	const res = await fetch(url);
	if (!res.ok) throw new Error(`Failed to fetch avatar: ${res.statusText}`);
	
	const buffer = await res.arrayBuffer();
	cache.set(url, buffer);
	return buffer;
}
