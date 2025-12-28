# Scripts

Utility scripts for Mini Ema project.

## generate_character_images.py

Generates character image variations using Gemini's Edit Images API.

### Purpose

This script creates anime-style character portraits with different expressions and actions based on the original Ema avatar. It generates all combinations of:

**Expressions:**
- neutral
- smile
- serious
- confused
- surprised
- sad

**Actions:**
- none
- nod
- shake
- wave
- jump
- point

### Requirements

- Gemini API key set in `.env` file or `GEMINI_API_KEY` environment variable
- Original Ema avatar image at `assets/imgs/ema.png`

### Usage

```bash
# From project root
uv run python scripts/generate_character_images.py
```

The script will:
1. Load the base Ema avatar image from `assets/imgs/ema.png`
2. Generate 36 variations (6 expressions × 6 actions)
3. Save generated images to `assets/gen_imgs/` with filenames like `expression_action.png`

### Output

Generated images are saved as:
- `neutral_none.png`
- `smile_wave.png`
- `serious_nod.png`
- etc.

### Notes

- This script is independent of the main `mini_ema` package
- Uses `gemini-2.5-flash-image` model for image editing
- Each generation request may take a few seconds
- Failed generations are logged and can be retried by running the script again
