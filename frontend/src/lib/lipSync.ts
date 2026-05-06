import { FaceAnimator } from "./FaceAnimator";
import { PUBLIC_BACKEND_URL } from '$env/static/public';

// Singleton audio element to bypass mobile autoplay restrictions
let globalAudioPlayer: HTMLAudioElement | null = null;

/**
 * Mempersiapkan audio agar bisa diputar di mobile (harus dipicu user interaction)
 */
export function unlockAudio() {
  if (typeof window === 'undefined') return;
  if (!globalAudioPlayer) {
    globalAudioPlayer = new Audio();
    // Putar suara hening sejenak untuk "memberkati" audio player
    globalAudioPlayer.src = "data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhAAQACABAAAABkYXRhAgAAAAEA";
    globalAudioPlayer.play().catch(() => {
      console.log("Audio still locked, will try again on next interaction");
    });
  }
}

/**
 * Mengucapkan teks menggunakan backend edge-tts.
 * Sinkronisasi bibir menggunakan data amplitudo (visemes) dari backend.
 */
export async function speakWithBackend(
  text: string,
  animator: FaceAnimator,
  pregeneratedData?: { audio: string; visemes: number[] }
): Promise<void> {
  let fallbackInterval: any;
  let isBackendAudioPlaying = false;

  // Pastikan audio player sudah siap
  if (!globalAudioPlayer) unlockAudio();

  // --- OPTIMISTIC FALLBACK ---
  const startFallbackAnimation = () => {
    let toggle = false;
    fallbackInterval = setInterval(() => {
      if (!isBackendAudioPlaying) {
        toggle = !toggle;
        animator.setMouth(toggle ? 0.4 : 0.1);
      }
    }, 150);
  };

  const stopFallbackAnimation = () => {
    if (fallbackInterval) {
      clearInterval(fallbackInterval);
      fallbackInterval = null;
    }
  };

  try {
    startFallbackAnimation();
    
    let audio: string;
    let visemes: number[];

    if (pregeneratedData) {
      audio = pregeneratedData.audio;
      visemes = pregeneratedData.visemes;
    } else {
      let apiUrl = PUBLIC_BACKEND_URL;
      if (typeof window !== 'undefined' && window.location.protocol === 'https:' && apiUrl.startsWith('http://')) {
        apiUrl = apiUrl.replace('http://', 'https://');
      }

      const response = await fetch(`${apiUrl}/api/speech`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Backend API Error (${response.status}): ${errText}`);
      }

      const data = await response.json();
      audio = data.audio;
      visemes = data.visemes;
    }

    if (!audio || !visemes) throw new Error("Invalid response from backend (missing audio/visemes)");

    const audioBlob = b64toBlob(audio, "audio/mpeg");
    const audioUrl = URL.createObjectURL(audioBlob);
    
    const audioPlayer = globalAudioPlayer!;
    audioPlayer.src = audioUrl;

    stopFallbackAnimation();

    // Edge-TTS default sample rate ~24000Hz. Hop length di backend 512.
    const frameInterval = (512 / 24000) * 1000; 

    return new Promise((resolve, reject) => {
      audioPlayer.onplay = () => {
        isBackendAudioPlaying = true;
        const startTime = performance.now();

        const updateMouth = () => {
          if (!isBackendAudioPlaying) return;

          const elapsed = performance.now() - startTime;
          const frame = Math.floor(elapsed / frameInterval);

          if (frame < visemes.length) {
            const amplitude = visemes[frame];
            animator.setMouth(amplitude * 3.5);
            requestAnimationFrame(updateMouth);
          } else {
            animator.setMouth(0);
          }
        };
        requestAnimationFrame(updateMouth);
      };

      audioPlayer.onended = () => {
        isBackendAudioPlaying = false;
        URL.revokeObjectURL(audioUrl);
        animator.setMouth(0);
        resolve();
      };

      audioPlayer.onerror = (e) => {
        isBackendAudioPlaying = false;
        stopFallbackAnimation();
        animator.setMouth(0);
        reject(new Error("Audio playback failed or was blocked by browser"));
      };

      audioPlayer.play().catch((err) => {
        // Jika gagal karena autoplay, lempar error spesifik
        if (err.name === 'NotAllowedError') {
          reject(new Error("AUTOPLAY_BLOCKED"));
        } else {
          reject(err);
        }
      });
    });

  } catch (err) {
    stopFallbackAnimation();
    animator.setMouth(0);
    throw err;
  }
}

/** Helper untuk convert base64 ke Blob */
function b64toBlob(b64Data: string, contentType = "", sliceSize = 512): Blob {
  const byteCharacters = atob(b64Data);
  const byteArrays = [];

  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize);
    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: contentType });
}
