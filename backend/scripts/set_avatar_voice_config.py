import sys, os, argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import InterviewAvatar

FORBIDDEN_TOKENS = ("prabowo", "windah", "reporter")


def main():
    parser = argparse.ArgumentParser(
        description="Terapkan konfigurasi voice cloning F5-TTS ke SEMUA avatar aktif."
    )
    parser.add_argument("--ref-audio", required=True, help="Path ke file audio referensi milik sendiri")
    parser.add_argument("--ref-text", default="auto", help="Transkrip PERSIS dari audio referensi (default: auto via Whisper)")
    parser.add_argument("--engine", default="f5tts_indo_v2")
    parser.add_argument("--dry-run", action="store_true", help="Tampilkan perubahan tanpa commit ke DB")
    args = parser.parse_args()

    lowered = args.ref_audio.lower()
    if any(tok in lowered for tok in FORBIDDEN_TOKENS):
        print(f"DITOLAK: '{args.ref_audio}' terindikasi file demo dokumentasi model (figur publik).")
        print("Gunakan rekaman referensi milik sendiri.")
        sys.exit(1)

    ref_audio_path = args.ref_audio
    if not os.path.exists(ref_audio_path):
        from app.services.speech import _resolve_reference_audio_path
        ref_audio_path = _resolve_reference_audio_path(args.ref_audio)

    if not os.path.exists(ref_audio_path):
        print(f"DITOLAK: file '{args.ref_audio}' tidak ditemukan di filesystem (dicoba juga: '{ref_audio_path}').")
        sys.exit(1)

    ref_text = args.ref_text
    if not ref_text or ref_text.strip().lower() in ("auto", "transkrip persis apa yang diucapkan di file wav ini"):
        print(f"Mengurai transkrip otomatis dari '{ref_audio_path}' menggunakan Whisper...")
        from app.services.transcriber import transcriber
        ref_text, _, _ = transcriber.transcribe_and_detect_fillers(ref_audio_path)
        print(f"Transkrip terdeteksi: '{ref_text}'")

    if not ref_text:
        print("ERROR: Transkrip kosong.")
        sys.exit(1)

    db = SessionLocal()
    try:
        avatars = db.query(InterviewAvatar).all()
        print(f"Ditemukan {len(avatars)} avatar.")
        for avatar in avatars:
            print(f"  - {avatar.id} ({avatar.name}): {avatar.ttsEngine} -> {args.engine}")
            if not args.dry_run:
                avatar.ttsEngine = args.engine
                avatar.ttsReferenceAudioPath = args.ref_audio
                avatar.ttsReferenceText = ref_text

        if args.dry_run:
            print("Dry-run, tidak ada perubahan disimpan.")
        else:
            db.commit()
            print("Konfigurasi diterapkan ke semua avatar.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
