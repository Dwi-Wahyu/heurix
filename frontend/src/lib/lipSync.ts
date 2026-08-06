import { PUBLIC_BACKEND_URL } from '$env/static/public';

// Singleton audio element to bypass mobile autoplay restrictions
let globalAudioPlayer: HTMLAudioElement | null = null;

// ── Analyser singleton untuk visualizer ──
let audioContext: AudioContext | null = null;
let analyserNode: AnalyserNode | null = null;
let sourceNode: MediaElementAudioSourceNode | null = null;

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
 * Lazy-init AudioContext + AnalyserNode yang tersambung ke globalAudioPlayer.
 * WAJIB dipanggil hanya sekali per audio element (createMediaElementSource
 * akan throw kalau dipanggil dua kali pada element yang sama).
 */
export function getOutputAnalyser(): AnalyserNode {
  if (!globalAudioPlayer) unlockAudio();
  if (analyserNode) return analyserNode;

  audioContext = new AudioContext();
  analyserNode = audioContext.createAnalyser();
  analyserNode.fftSize = 128; // -> 64 bin frequency data, cukup untuk bar chart ringkas
  analyserNode.smoothingTimeConstant = 0.7; // biar transisi antar bar tidak "patah-patah"

  sourceNode = audioContext.createMediaElementSource(globalAudioPlayer!);
  sourceNode.connect(analyserNode);
  // ── PENTING: sambungkan balik ke destination, kalau tidak audio jadi BISU ──
  analyserNode.connect(audioContext.destination);

  return analyserNode;
}

/** Panggil dari handleUserInteraction() di interview page agar AudioContext resume setelah gesture user. */
export function resumeAudioContext() {
  audioContext?.resume();
}

/**
 * Mengucapkan teks menggunakan backend edge-tts.
 * Memutar audio secara langsung, visualisasi ditangani terpisah oleh AnalyserNode.
 */
export async function speakWithBackend(
  text: string,
  pregeneratedData?: { audio: string; visemes: number[] }
): Promise<void> {
  // Pastikan audio player sudah siap
  if (!globalAudioPlayer) unlockAudio();

  try {
    let audio: string;

    if (pregeneratedData) {
      audio = pregeneratedData.audio;
    } else {
      const response = await fetch(`/api/proxy/api/speech`, {
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
    }

    if (!audio) throw new Error("Invalid response from backend (missing audio)");

    const audioBlob = b64toBlob(audio, "audio/mpeg");
    const audioUrl = URL.createObjectURL(audioBlob);
    
    const audioPlayer = globalAudioPlayer!;
    audioPlayer.src = audioUrl;

    return new Promise((resolve, reject) => {
      audioPlayer.onended = () => {
        URL.revokeObjectURL(audioUrl);
        resolve();
      };

      audioPlayer.onerror = (e) => {
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
