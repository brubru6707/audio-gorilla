import os

# Load API keys from environment variables or default to provided keys (for demo purposes).
# In production, avoid hardcoding keys. Use environment variables or a secure secret manager.

HUME_API_KEY = os.getenv("HUME_API_KEY", "7RnQ6KBKiHXlzK5tvbhNZ6COiKBlpQ4zDrGeYeiCGDv2l7Aj")
HUME_SECRET_KEY = os.getenv("HUME_SECRET_KEY", "oHl0pnGEMzFuC9y2NqfAAe6KCiftKobrbT7FczdI4WO4yuY2gHTEgVldKy2x4Kzk")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_3767888bd13ba1e621c8dd758ae3c2f4faaf9a58f5a0fa66")

# Default output directory for generated audio (can be overridden by JSON input)
DEFAULT_OUTPUT_DIR = os.getenv("AUDIO_OUTPUT_DIR", "generated_audio")
