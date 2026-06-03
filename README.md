# Video Intelligence Pipeline

Paste video URLs → download audio → transcribe with Whisper → translate /
summarize / categorize with Claude → store in **SQLite** → export a **multi-tab
Excel workbook** and a **styled HTML guide** (identical look to the Korea &
Seoul web app).

```
URLs (input/urls.csv)
        │
        ▼
  yt-dlp  ──►  FFmpeg  ──►  Whisper  ──►  Claude
 (metadata    (16k mono    (transcript)  (translate +
  + audio)      wav)                      categorize)
        │
        ▼
   SQLite  ──►  Excel (.xlsx)  +  Guide (.html)
 (source of truth)
```

## Install

```bash
cd video-intel-pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# FFmpeg is a system tool:
#   macOS: brew install ffmpeg   |   Ubuntu: sudo apt install ffmpeg   |   Windows: choco install ffmpeg
```

Set your key (optional but recommended):

```bash
cp .env.example .env   # edit it, then:
source .env
```

## Try it without any setup

```bash
python process_videos.py --demo
open output/video_guide.html       # and output/video_library.xlsx
```

`--demo` seeds sample data (no network, no API) so you can see the outputs.

## Real runs

1. Put links in `input/urls.csv` (a `url` column, or just one URL per line).
2. Run:

```bash
python process_videos.py                 # full pipeline, then export
python process_videos.py --skip-existing # don't re-process stored URLs
python process_videos.py --metadata-only # skip audio + Whisper (no ffmpeg needed)
python process_videos.py --export-only   # rebuild Excel + guide from the DB
python process_videos.py --guide-title "Korea & Seoul"
```

Outputs land in `output/`:
- `video_intel.db` — SQLite, the real store
- `video_library.xlsx` — All Videos + a tab per category + Needs Review + Errors
- `video_guide.html` — the shareable, searchable guide

## How categorization works

Each video is bucketed into one category from `video_intel/config.py` →
`CATEGORIES` (defaults match the Korea & Seoul guide; edit freely). Anything the
model is unsure about, or that scores low, lands in **Needs Review** so nothing
is silently mislabeled.

## Notes & etiquette

- Works on **public or your own** content. Don't bypass logins, paywalls, or
  privacy settings — use account cookies/authorization only for content you own.
- Links will sometimes fail (private, expired, region-locked). Those are caught
  and written to the **Errors** tab; the run continues.
- No `ANTHROPIC_API_KEY`? The pipeline still downloads + transcribes and stores
  everything, flagged for review — add the key later and re-run to enrich.

## Layout

```
process_videos.py            # CLI orchestrator
requirements.txt  .env.example
input/urls.csv               # your links
video_intel/
  config.py                  # paths, model, categories
  platforms.py               # URL -> platform
  download.py                # yt-dlp
  audio.py                   # ffmpeg -> 16k mono wav
  transcribe.py              # local Whisper
  analyze.py                 # Claude (translate/summarize/categorize) + fallback
  store.py                   # SQLite schema + upsert/query
  export_excel.py            # multi-tab workbook
  export_guide.py            # HTML guide (matches the web app)
  guide_assets.py            # the exact guide CSS/JS
downloads/  audio/  transcripts/  output/   # created on first run
```
