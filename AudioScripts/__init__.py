"""AudioScripts package

Provides modular tools for working with audio output generated from text
prompts.  See `generate_audio` module for the main CLI entrypoint.
"""
from .generate_audio import main as generate_audio_main  # re-export convenience