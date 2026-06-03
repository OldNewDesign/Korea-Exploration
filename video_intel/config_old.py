"""Central configuration: paths, environment, models, categories."""
import os
from pathlib import Path

# ---- folders -------------------------------------------------------------
BASE_DIR     = Path(os.environ.get("VIP_BASE_DIR", Path.cwd())).resolve()
INPUT_DIR    = BASE_DIR / "input"
DOWNLOADS    = BASE_DIR / "downloads"
AUDIO_DIR    = BASE_DIR / "audio"
TRANSCRIPTS  = BASE_DIR / "transcripts"
OUTPUT_DIR   = BASE_DIR / "output"
DB_PATH      = OUTPUT_DIR / "video_intel.db"
EXCEL_PATH   = OUTPUT_DIR / "video_library.xlsx"
GUIDE_PATH   = OUTPUT_DIR / "video_guide.html"

# ---- AI ------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
# Change to whatever model you have access to (see https://docs.claude.com/en/api/overview)
ANALYZE_MODEL     = os.environ.get("VIP_MODEL", "claude-sonnet-4-6")

# Whisper model size: tiny | base | small | medium | large-v3 | turbo
WHISPER_MODEL     = os.environ.get("VIP_WHISPER_MODEL", "small")

# ---- categorization ------------------------------------------------------
# Defaults mirror the Korea & Seoul guide. Last item is the fallback bucket.
CATEGORIES = [
    "Places to Eat", "Cafes & Desserts", "Recipes & Cooking", "Hikes & Nature",
    "Activities & Experiences", "Animal Cafes & Zoos", "Museums & Art",
    "Historic & Cultural", "Beauty & Wellness", "Workouts & Fitness",
    "Running Spots & Gear", "Shopping & Markets", "DIY Crafts & Photobooths",
    "Travel Tips & Guides", "Fragrance & Cologne", "Watches & Accessories", "Other",
]

GUIDE_TITLE = os.environ.get("VIP_GUIDE_TITLE", "My Video Guide")


def ensure_dirs():
    for d in (INPUT_DIR, DOWNLOADS, AUDIO_DIR, TRANSCRIPTS, OUTPUT_DIR):
        d.mkdir(parents=True, exist_ok=True)
