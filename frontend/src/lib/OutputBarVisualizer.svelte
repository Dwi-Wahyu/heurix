<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import BarVisualizer from '$lib/visualizations/core/BarVisualizer.svelte';
  import { getOutputAnalyser } from '$lib/lipSync';

  let values = $state(new Float32Array(32));
  let rafId: number;

  onMount(() => {
    const analyser = getOutputAnalyser();
    const bufferLength = analyser.frequencyBinCount; // 64 utk fftSize=128
    const dataArray = new Uint8Array(bufferLength);

    function loop() {
      analyser.getByteFrequencyData(dataArray);
      // normalisasi 0-255 -> 0-1, ambil subset biar tidak terlalu padat (32 bar)
      const normalized = new Float32Array(32);
      const step = Math.floor(bufferLength / 32) || 1;
      for (let i = 0; i < 32; i++) {
        normalized[i] = (dataArray[i * step] || 0) / 255;
      }
      values = normalized;
      rafId = requestAnimationFrame(loop);
    }
    loop();
  });

  onDestroy(() => {
    if (rafId) cancelAnimationFrame(rafId);
  });
</script>

<div class="h-full w-full flex items-center justify-center">
  <BarVisualizer {values} color="#818CF8" barSpacing={3} center={true} />
</div>
