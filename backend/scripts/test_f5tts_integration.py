import sys, os, asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.speech import (
    _guard_reference_audio,
    get_speech_service_for_avatar,
    SpeechService,
    F5TTSSpeechService
)
from app.services import f5tts_service
from app.models import InterviewAvatar


def test_guard_forbidden_tokens():
    for forbidden in ["reference_audio/ref_prabowo.mp3", "reference_audio/windah_voice.wav", "reference_audio/reporter_demo.wav"]:
        try:
            _guard_reference_audio(forbidden)
            assert False, f"Expected ValueError for {forbidden}"
        except ValueError as e:
            assert "terindikasi file demo" in str(e)
    
    # Valid path should pass without error
    _guard_reference_audio("reference_audio/my_custom_voice.wav")



def test_is_available_returns_bool():
    # Model files do not exist by default unless manually downloaded
    avail = f5tts_service.is_available()
    assert isinstance(avail, bool)


def test_factory_fallback_on_missing_reference():
    # Avatar with f5tts_indo_v2 but missing audio/text reference
    class MockAvatar:
        id = "avatar_1"
        ttsEngine = "f5tts_indo_v2"
        ttsReferenceAudioPath = None
        ttsReferenceText = None
        ttsVoiceId = "id-ID-ArdiNeural"

    service = get_speech_service_for_avatar(MockAvatar())
    assert isinstance(service, SpeechService)


def test_factory_fallback_on_forbidden_token():
    class MockAvatar:
        id = "avatar_2"
        ttsEngine = "f5tts_indo_v2"
        ttsReferenceAudioPath = "reference_audio/ref_prabowo.mp3"
        ttsReferenceText = "Halo nama saya..."
        ttsVoiceId = "id-ID-ArdiNeural"

    service = get_speech_service_for_avatar(MockAvatar())
    assert isinstance(service, SpeechService)


async def test_f5tts_service_fallback_to_edge_tts():

    # When synthesize fails (e.g. model not loaded/available), it should fallback to edge_tts
    f5_service = F5TTSSpeechService(
        ref_audio_path="reference_audio/formal_male_reference.wav",
        ref_text="Halo, ini adalah rekaman tes."
    )
    # Generate speech should succeed via fallback edge_tts
    b64, visemes = await f5_service.generate_speech_with_visemes("Halo ini tes fallback F5TTS.")
    assert b64 is not None
    assert isinstance(visemes, list)


if __name__ == "__main__":
    print("Running integration tests...")
    test_guard_forbidden_tokens()
    print("✓ test_guard_forbidden_tokens passed")
    test_is_available_returns_bool()
    print("✓ test_is_available_returns_bool passed")
    test_factory_fallback_on_missing_reference()
    print("✓ test_factory_fallback_on_missing_reference passed")
    test_factory_fallback_on_forbidden_token()
    print("✓ test_factory_fallback_on_forbidden_token passed")
    asyncio.run(test_f5tts_service_fallback_to_edge_tts())
    print("✓ test_f5tts_service_fallback_to_edge_tts passed")
    print("ALL TESTS PASSED SUCCESSFULLY!")
