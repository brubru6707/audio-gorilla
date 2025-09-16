import os
import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import requests
from gtts import gTTS

from .config import HUME_API_KEY, HUME_SECRET_KEY, ELEVENLABS_API_KEY


class VoiceProvider(ABC):
    """Abstract base class for a voice provider service."""

    @abstractmethod
    def list_voices(self) -> List[str]:
        """Return a list of available voice identifiers."""

    @abstractmethod
    def generate_audio(self, text: str, voice: str, output_path: Path) -> None:
        """Generate audio for the given text using the specified voice and save to output_path."""


class ElevenLabsProvider(VoiceProvider):
    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self._voices_cache: List[str] | None = None

    def _headers(self) -> dict[str, str]:
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def list_voices(self) -> List[str]:
        if self._voices_cache is None:
            url = f"{self.BASE_URL}/voices"
            try:
                response = requests.get(url, headers=self._headers(), timeout=15)
                response.raise_for_status()
                data = response.json()
                self._voices_cache = [voice["voice_id"] for voice in data.get("voices", [])]
            except Exception as exc:
                print(f"Failed to fetch ElevenLabs voices: {exc}. Falling back to default voices list.")
                # A minimal fallback list of public voices
                self._voices_cache = [
                    "21m00Tcm4TlvDq8ikWAM",  # Rachel
                    "2EiwWnXFnvU5JabPnv8n",  # Clyde
                    "CwhRBWXzGAHq8TQ4Fs17",  # Roger
                    "EXAVITQu4vr4xnSDxMaL",  # Sarah
                ]
        return self._voices_cache

    def generate_audio(self, text: str, voice: str, output_path: Path) -> None:
        url = f"{self.BASE_URL}/text-to-speech/{voice}?optimize_streaming_latency=0"
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
            },
        }
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            response.raise_for_status()
            # ElevenLabs returns audio/mpeg content
            output_path.write_bytes(response.content)
        except Exception as exc:
            print(f"ElevenLabs TTS failed ({exc}). Falling back to gTTS.")
            self._fallback_gtts(text, output_path)

    @staticmethod
    def _fallback_gtts(text: str, output_path: Path) -> None:
        tts = gTTS(text=text)
        tts.save(str(output_path))


class HumeAIProvider(VoiceProvider):
    """Placeholder implementation for Hume.ai voice generation.

    As the Hume.ai TTS API is not publicly documented in detail, we provide a stub that falls back to gTTS.
    """

    # Assuming hypothetical Hume.ai endpoints. If real endpoints are available, swap here.
    BASE_URL = "https://api.hume.ai/v0/voice"

    def __init__(self, api_key: str | None = None, secret_key: str | None = None):
        self.api_key = api_key or HUME_API_KEY
        self.secret_key = secret_key or HUME_SECRET_KEY
        # Example voice IDs (replace with actual if available)
        self._voices = [
            "hume_voice_1",
            "hume_voice_2",
            "hume_voice_3",
        ]

    def list_voices(self) -> List[str]:
        return self._voices

    def _headers(self) -> dict[str, str]:
        return {
            "X-Hume-Api-Key": self.api_key,
            "X-Hume-Secret": self.secret_key,
            "Content-Type": "application/json",
        }

    def generate_audio(self, text: str, voice: str, output_path: Path) -> None:
        url = f"{self.BASE_URL}/{voice}:generate"
        payload = {"text": text}
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            response.raise_for_status()
            output_path.write_bytes(response.content)
        except Exception as exc:
            print(f"Hume.ai TTS failed ({exc}). Falling back to gTTS.")
            self._fallback_gtts(text, output_path)

    @staticmethod
    def _fallback_gtts(text: str, output_path: Path) -> None:
        tts = gTTS(text=text)
        tts.save(str(output_path))


# Helper function to get a random provider + voice combination

def get_random_voice_provider() -> tuple[VoiceProvider, str]:
    providers: List[VoiceProvider] = [HumeAIProvider(), ElevenLabsProvider()]
    provider = random.choice(providers)
    voice = random.choice(provider.list_voices())
    return provider, voice
