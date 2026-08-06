<script lang="ts">
	interface Props {
		values: Float32Array;
		color?: string;
		startHue?: number;
		endHue?: number;
		barWidth?: number;
		barSpacing?: number;
		center?: boolean;
	}

	let {
		values,
		color = undefined,
		startHue = undefined,
		endHue = undefined,
		barWidth = 0,
		barSpacing = 0,
		center = false
	}: Props = $props();

	let canvas = $state<HTMLCanvasElement | undefined>(undefined);
	let contentRect = $state<DOMRectReadOnly | undefined>(undefined);

	$effect(() => {
		if (!canvas || !contentRect) return;

		const ctx = canvas.getContext('2d');
		if (!ctx) return;

		// Update canvas size
		canvas.width = Math.round(contentRect.width) * 2;
		canvas.height = Math.round(contentRect.height) * 2;

		// Clear
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		let width = barWidth;
		let dets = values.length;

		if (!dets) {
			dets = Math.floor((canvas.width - barSpacing) / (Math.max(barWidth, 1) + barSpacing));
		}
		if (!barWidth) {
			width = (canvas.width - barSpacing) / dets - barSpacing;
		}

		if (color !== undefined) ctx.fillStyle = color;

		for (let i = 0; i < values.length; i++) {
			const amplitude = Math.abs(values[i]);
			const height = Math.max(1, amplitude * canvas.height);
			const x = barSpacing + i * (width + barSpacing);
			const y = center ? (canvas.height - height) / 2 : canvas.height - height;

			if (startHue !== undefined && endHue !== undefined) {
				const t = i / dets;
				const hue = (startHue ?? 0) + t * (endHue - startHue);
				ctx.fillStyle = `hsl(${hue % 360}, 100%, 50%)`;
			}
			ctx.fillRect(x, y, width, height);
		}
	});
</script>

<canvas bind:this={canvas} bind:contentRect style="height: 100%; width: 100%;"></canvas>
