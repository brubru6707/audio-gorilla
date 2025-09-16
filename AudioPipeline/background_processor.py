import os
import random
from pathlib import Path
from typing import List, Tuple

try:
    import librosa
    import numpy as np
    from pydub import AudioSegment
    from pydub.effects import normalize
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Audio processing libraries not available: {e}")
    print("Background audio will be disabled. Install pydub, librosa, and numpy to enable.")
    AUDIO_PROCESSING_AVAILABLE = False


class SimpleBackgroundProcessor:
    """Simplified background audio processor that works without FFmpeg for basic operations."""
    
    def __init__(self, background_dir: str | Path | None = None):
        """Initialize with background audio directory."""
        if background_dir is None:
            background_dir = Path(__file__).parent / "background"
        self.background_dir = Path(background_dir)
        self._background_files: List[Path] | None = None
    
    def get_background_files(self) -> List[Path]:
        """Get list of available background audio files."""
        if self._background_files is None:
            audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
            self._background_files = [
                f for f in self.background_dir.iterdir() 
                if f.is_file() and f.suffix.lower() in audio_extensions
            ]
        return self._background_files
    
    def select_random_background(self) -> Path | None:
        """Select a random background audio file."""
        files = self.get_background_files()
        if not files:
            print("Warning: No background audio files found.")
            return None
        return random.choice(files)
    
    def create_simple_mix(self, speech_file: Path, output_file: Path, background_volume_db: float = -20.0) -> bool:
        """Create a simple audio mix using librosa (no FFmpeg required)."""
        try:
            # Load speech audio with librosa
            speech_data, speech_sr = librosa.load(str(speech_file), sr=None)
            
            # Select random background
            background_file = self.select_random_background()
            if background_file is None:
                return False
            
            # Load background audio
            background_data, background_sr = librosa.load(str(background_file), sr=speech_sr)
            
            # Ensure background is long enough
            if len(background_data) < len(speech_data):
                # Loop background to match speech length
                loops_needed = (len(speech_data) // len(background_data)) + 1
                background_data = np.tile(background_data, loops_needed)
            
            # Select random segment from background
            if len(background_data) > len(speech_data):
                start_idx = random.randint(0, len(background_data) - len(speech_data))
                background_segment = background_data[start_idx:start_idx + len(speech_data)]
            else:
                background_segment = background_data[:len(speech_data)]
            
            # Apply volume reduction to background
            volume_factor = 10**(background_volume_db / 20)
            background_segment = background_segment * volume_factor
            
            # Mix the audio
            mixed_audio = speech_data + background_segment
            
            # Normalize to prevent clipping
            max_val = np.max(np.abs(mixed_audio))
            if max_val > 1.0:
                mixed_audio = mixed_audio / max_val
            
            # Save using librosa
            import soundfile as sf
            sf.write(str(output_file), mixed_audio, speech_sr)
            
            print(f"Successfully created mixed audio: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error creating simple mix: {e}")
            return False


class BackgroundAudioProcessor:
    """Handles background audio selection, preprocessing, and mixing with speech audio."""
    
    def __init__(self, background_dir: str | Path | None = None):
        """Initialize with background audio directory."""
        if not AUDIO_PROCESSING_AVAILABLE:
            raise ImportError("Audio processing libraries not available. Install pydub, librosa, and numpy.")
        
        if background_dir is None:
            background_dir = Path(__file__).parent / "background"
        self.background_dir = Path(background_dir)
        self._background_files: List[Path] | None = None
        self.simple_processor = SimpleBackgroundProcessor(background_dir)
    
    def get_background_files(self) -> List[Path]:
        """Get list of available background audio files."""
        return self.simple_processor.get_background_files()
    
    def select_random_background(self) -> Path | None:
        """Select a random background audio file."""
        return self.simple_processor.select_random_background()
    
    def get_random_segment(self, audio_path: Path, target_duration_ms: int) -> AudioSegment:
        """Extract a random segment from background audio."""
        try:
            # Load audio file
            audio = AudioSegment.from_file(str(audio_path))
            
            # If background is shorter than target, loop it
            if len(audio) < target_duration_ms:
                # Calculate how many times to repeat
                repeats = (target_duration_ms // len(audio)) + 1
                audio = audio * repeats
            
            # Select random start point
            max_start = len(audio) - target_duration_ms
            if max_start <= 0:
                start_ms = 0
            else:
                start_ms = random.randint(0, max_start)
            
            # Extract segment
            segment = audio[start_ms:start_ms + target_duration_ms]
            return segment
            
        except Exception as e:
            print(f"Error processing background audio {audio_path}: {e}")
            # Return silence as fallback
            return AudioSegment.silent(duration=target_duration_ms)
    
    def normalize_volume(self, audio: AudioSegment, target_lufs: float = -23.0) -> AudioSegment:
        """Normalize audio to target LUFS level."""
        try:
            # Convert to numpy array for librosa processing
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
            
            # Calculate current RMS
            rms = np.sqrt(np.mean(samples**2))
            if rms == 0:
                return audio
            
            # Calculate target RMS (approximate LUFS to RMS conversion)
            target_rms = 10**(target_lufs / 20) * 0.1  # Rough conversion
            
            # Apply gain
            gain_db = 20 * np.log10(target_rms / rms)
            normalized_audio = audio + gain_db
            
            return normalized_audio
            
        except Exception as e:
            print(f"Error normalizing volume: {e}")
            return audio
    
    def mix_with_background(self, speech_audio: AudioSegment, background_volume_db: float = -20.0) -> AudioSegment:
        """Mix speech audio with background audio."""
        try:
            # Select random background
            background_file = self.select_random_background()
            if background_file is None:
                return speech_audio
            
            # Get background segment
            background_segment = self.get_random_segment(background_file, len(speech_audio))
            
            # Normalize background to be quieter than speech
            background_segment = background_segment + background_volume_db
            
            # Ensure both have same sample rate and channels
            if speech_audio.frame_rate != background_segment.frame_rate:
                background_segment = background_segment.set_frame_rate(speech_audio.frame_rate)
            
            if speech_audio.channels != background_segment.channels:
                if speech_audio.channels == 1:
                    background_segment = background_segment.set_channels(1)
                else:
                    speech_audio = speech_audio.set_channels(2)
            
            # Mix the audio
            mixed_audio = speech_audio.overlay(background_segment)
            
            # Normalize the final mix to prevent clipping
            mixed_audio = normalize(mixed_audio)
            
            return mixed_audio
            
        except Exception as e:
            print(f"Error mixing background audio: {e}")
            return speech_audio
    
    def process_audio_file(self, input_path: Path, output_path: Path, background_volume_db: float = -20.0) -> bool:
        """Process a single audio file by adding background audio."""
        try:
            # Try simple librosa-based approach first (no FFmpeg required)
            if self.simple_processor.create_simple_mix(input_path, output_path, background_volume_db):
                return True
            
            # Fallback to pydub approach
            speech_audio = AudioSegment.from_file(str(input_path))
            mixed_audio = self.mix_with_background(speech_audio, background_volume_db)
            mixed_audio.export(str(output_path), format="mp3")
            
            print(f"Added background audio to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing audio file {input_path}: {e}")
            return False


def add_background_to_audio(input_path: Path, output_path: Path, background_volume_db: float = -20.0) -> bool:
    """Convenience function to add background audio to a single file."""
    processor = BackgroundAudioProcessor()
    return processor.process_audio_file(input_path, output_path, background_volume_db)