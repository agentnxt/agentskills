# Assets

## Fonts

No fonts are bundled to keep the skill lightweight. The `generate_cover.py` script automatically discovers system fonts:

- **macOS:** Helvetica, Arial
- **Linux:** DejaVu Sans Bold, Liberation Sans Bold
- **Fallback:** Pillow built-in bitmap font (lower quality)

### Using a custom font

Pass `--font-path /path/to/MyFont.ttf` to `generate_cover.py`.

To make a font permanently available to this skill, download it into this directory:

```bash
# Example: download Inter font
curl -L -o assets/Inter-Bold.ttf "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.otf"

# Then use it:
python scripts/generate_cover.py --font-path {baseDir}/assets/Inter-Bold.ttf ...
```

## Logos

Place logo PNG files in this directory and reference them with `--logo {baseDir}/assets/logo.png`.
