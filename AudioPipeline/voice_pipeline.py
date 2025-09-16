import json
import random
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from .config import DEFAULT_OUTPUT_DIR
from .voice_providers import get_random_voice_provider

try:
    from .background_processor import BackgroundAudioProcessor, AUDIO_PROCESSING_AVAILABLE
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    BackgroundAudioProcessor = None


def load_prompts(json_path: Path) -> List[Dict[str, Any]]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON file must contain a list of prompt objects")
    return data


def ensure_directory(path: Path) -> None:
    if not path.exists():
        print(f"Creating directory {path}")
        path.mkdir(parents=True, exist_ok=True)


def process_prompts(json_file: Path, add_background: bool = True, background_volume_db: float = -20.0) -> None:
    """Process prompts and generate audio files with optional background audio."""
    prompts = load_prompts(json_file)
    
    if add_background and not AUDIO_PROCESSING_AVAILABLE:
        print("Warning: Audio processing libraries not available. Background audio disabled.")
        add_background = False
    
    background_processor = BackgroundAudioProcessor() if add_background else None
    
    for prompt in prompts:
        text: str = prompt["text"]
        filename: str = prompt.get("filename") or f"prompt_{random.randint(1000,9999)}.mp3"
        folder: str = prompt.get("folder") or DEFAULT_OUTPUT_DIR
        folder_path = Path(folder)
        ensure_directory(folder_path)
        output_path = folder_path / filename

        provider, voice = get_random_voice_provider()
        print(f"Generating '{output_path}' using {provider.__class__.__name__} voice '{voice}'...")
        
        if add_background and background_processor:
            # Generate speech to temporary file first
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            try:
                # Generate speech audio
                provider.generate_audio(text, voice, temp_path)
                
                # Add background audio
                print(f"Adding background audio to '{output_path}'...")
                success = background_processor.process_audio_file(
                    temp_path, output_path, background_volume_db
                )
                
                if not success:
                    # Fallback: copy speech audio without background
                    import shutil
                    shutil.copy2(temp_path, output_path)
                    print(f"Background audio failed, saved speech-only audio to '{output_path}'")
                    
            finally:
                # Clean up temporary file
                if temp_path.exists():
                    temp_path.unlink()
        else:
            # Generate speech audio directly
            provider.generate_audio(text, voice, output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate audio files from prompts in JSON files.")
    parser.add_argument("json_files", nargs="+", help="Path(s) to JSON files containing prompts.")
    parser.add_argument("--no-background", action="store_true", 
                       help="Disable background audio overlay.")
    parser.add_argument("--background-volume", type=float, default=-20.0,
                       help="Background audio volume in dB (default: -20.0).")
    args = parser.parse_args()

    for json_path_str in args.json_files:
        process_prompts(
            Path(json_path_str), 
            add_background=not args.no_background,
            background_volume_db=args.background_volume
        )
