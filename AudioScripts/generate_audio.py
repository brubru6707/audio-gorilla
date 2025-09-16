"""AudioScripts.generate_audio
A modular command-line tool for turning text prompts into audio files.

Current features
----------------
1. Provider-agnostic design.  A common `TTSProvider` interface allows easy
   swapping in of different speech engines (e.g. Amazon Polly, ElevenLabs,
   Azure, etc.).  A simple Google Text-to-Speech implementation (`GTTSProvider`)
   is bundled to work out-of-the-box and without paid credits.
2. Accepts either a single prompt string or a JSON file containing an array of
   prompts (see examples below).
3. Outputs `.mp3` files into the *AudioScripts/PromptAudios* directory.  This
   directory is created automatically on first run.
4. Hooks in place for future audio post-processing such as adding background
   noise or distortion using *pydub*.

Usage
-----
Single prompt:
    python -m AudioScripts.generate_audio --prompt "Hello world!"

Prompts from JSON file:
    python -m AudioScripts.generate_audio --prompt_file prompts.json

Choose a provider (defaults to gTTS):
    python -m AudioScripts.generate_audio --provider gtts --prompt "Hi!"

JSON file format
----------------
[
  "First prompt to synthesise",
  "Second prompt"
]

Dependences
-----------
This script relies on *gTTS* (Google Text-to-Speech) and *pydub* for optional
post-processing.  Install them with:
    pip install gTTS pydub
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Sequence

# Load variables from a .env file if present (for API keys, etc.).
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ModuleNotFoundError:  # pragma: no cover
    # python-dotenv is optional; environment variables can still be set normally.
    pass

# Optional imports – do not crash if user hasn't installed them yet.
try:
    from gtts import gTTS  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    gTTS = None  # pyright: ignore[reportGeneralTypeIssues]

try:
    from pydub import AudioSegment  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    AudioSegment = None  # pyright: ignore[reportGeneralTypeIssues]

# ElevenLabs TTS (premium, human-like voices)
try:
    import requests  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    requests = None  # pyright: ignore[reportGeneralTypeIssues]

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
AUDIO_OUTPUT_DIR = SCRIPT_DIR / "PromptAudios"
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Provider abstraction
# ---------------------------------------------------------------------------
class TTSProvider(ABC):
    """Abstract base class for a text-to-speech provider implementation."""

    @abstractmethod
    def synthesize(self, text: str, output_file: Path) -> None:  # pragma: no cover
        """Convert *text* to speech and save to *output_file* (mp3/wav).

        Implementations must create *output_file* (including parent dirs).
        """
        raise NotImplementedError


class GTTSProvider(TTSProvider):
    """Google Text-to-Speech provider using the *gTTS* Python package."""

    DEFAULT_LANG = "en"

    def __init__(self, lang: str = DEFAULT_LANG) -> None:
        if gTTS is None:
            raise RuntimeError(
                "gTTS package not installed.  Install with `pip install gTTS`."
            )
        self.lang = lang

    def synthesize(self, text: str, output_file: Path) -> None:
        tts = gTTS(text=text, lang=self.lang)
        tts.save(str(output_file))


# ---------------------------------------------------------------------------
# ElevenLabs provider (https://elevenlabs.io) – superior neural voices
# ---------------------------------------------------------------------------


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs speech synthesis.

    Requires environment variable *ELEVENLABS_API_KEY* with your API key.
    Optionally choose a voice with *voice_id* (default: the "Rachel" voice).
    """

    DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"  # "Rachel" – stable, English (US)

    def __init__(self, voice_id: str | None = None, model: str = "eleven_monolingual_v1") -> None:
        if requests is None:
            raise RuntimeError("`requests` package is required. Install with `pip install requests`.")

        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "Set the ELEVENLABS_API_KEY environment variable with your ElevenLabs API key."
            )

        self.voice_id = voice_id or self.DEFAULT_VOICE
        self.model = model

    def synthesize(self, text: str, output_file: Path) -> None:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "model_id": self.model,
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            raise RuntimeError(
                f"ElevenLabs API error ({response.status_code}): {response.text[:200]}"
            )

        output_file.write_bytes(response.content)


PROVIDERS = {
    "gtts": GTTSProvider,
    "11labs": ElevenLabsProvider,
    # Future providers can be added here without changing the rest of the code:
    # "polly": PollyProvider,
    # "azure": AzureTTSProvider,
    # etc.
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def slugify(text: str, max_length: int = 50) -> str:
    """Create a filesystem-friendly slug from *text*."""
    # Collapse whitespace, remove non-alphanum, truncate.
    slug = re.sub(r"\s+", " ", text.strip())
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = slug.replace(" ", "-")
    return slug[:max_length] or "prompt"


def load_prompts(args: argparse.Namespace) -> Sequence[str]:
    if args.prompt_file:
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list) or not all(isinstance(p, str) for p in data):
            raise ValueError("JSON file must contain a list of strings.")
        prompts: List[str] = data  # type: ignore[assignment]
    elif args.prompt:
        prompts = [args.prompt]
    else:
        raise SystemExit("Either --prompt or --prompt_file is required.")
    return prompts


# ---------------------------------------------------------------------------
# Optional post-processing hooks
# ---------------------------------------------------------------------------

def apply_post_processing(audio_path: Path, noise: bool = False, distortion: bool = False) -> None:
    """Apply audio effects in-place using *pydub*.

    Currently only stubbed; extend as needed.
    """
    if not noise and not distortion:
        return  # Nothing to do.
    if AudioSegment is None:
        raise RuntimeError("pydub is required for post-processing. Install with `pip install pydub`. ")

    audio = AudioSegment.from_file(audio_path)
    if noise:
        # Very basic white noise overlay (placeholder implementation).
        noise_segment = AudioSegment.silent(duration=len(audio)).apply_gain(-20)
        audio = audio.overlay(noise_segment)
    if distortion:
        audio = audio + 10  # simple gain increase as a placeholder for real distortion.
    audio.export(audio_path, format="mp3")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate audio files from text prompts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prompt", type=str, help="Single prompt text to synthesise.")
    group.add_argument("--prompt_file", type=str, help="Path to JSON file with a list of prompts.")

    parser.add_argument(
        "--provider",
        default="gtts",
        choices=PROVIDERS.keys(),
        help="Which TTS provider backend to use.",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language code for the speech (provider-specific; gTTS supports standard ISO codes).",
    )
    parser.add_argument("--noise", action="store_true", help="Add background noise (experimental).")
    parser.add_argument("--distortion", action="store_true", help="Add distortion effect (experimental).")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:  # pragma: no cover
    args = parse_args(argv)

    prompts = load_prompts(args)
    provider_cls = PROVIDERS[args.provider]
    provider: TTSProvider
    if provider_cls is GTTSProvider:
        provider = provider_cls(lang=args.lang)
    else:
        provider = provider_cls()  # type: ignore[call-arg]

    for idx, prompt in enumerate(prompts, start=1):
        filename = f"{idx:03d}_{slugify(prompt)}.mp3"
        output_path = AUDIO_OUTPUT_DIR / filename
        print(f"[TTS] Synthesising {prompt!r} -> {output_path}")
        provider.synthesize(prompt, output_path)
        apply_post_processing(output_path, noise=args.noise, distortion=args.distortion)

    print(f"\nAll done!  Generated {len(prompts)} file(s) in {AUDIO_OUTPUT_DIR.relative_to(SCRIPT_DIR.parent)}")


if __name__ == "__main__":  # pragma: no cover
    main()