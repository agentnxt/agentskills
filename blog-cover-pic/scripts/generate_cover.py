#!/usr/bin/env python3
"""Generate blog cover images: feature, Open Graph, and Google Discover variants.

Supports per-element font, color, and size configuration, gradient control,
Google Fonts auto-download, and Font Awesome icon rendering.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import urllib.request
import urllib.error
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple, List

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1200
HEIGHT = 630

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
FONT_CACHE_DIR = os.path.join(BASE_DIR, ".font-cache")


# ---------------------------------------------------------------------------
# Google Fonts downloader
# ---------------------------------------------------------------------------

GITHUB_FONTS_API = "https://api.github.com/repos/google/fonts/contents/ofl/{family_dir}"


def download_google_font(family: str, weight: int = 700) -> str | None:
    """Download a Google Font TTF from the google/fonts GitHub repo and cache locally.

    The google/fonts repo at github.com/google/fonts hosts all font TTFs.
    This avoids the CSS API which only serves woff2 (not usable by Pillow).
    """
    os.makedirs(FONT_CACHE_DIR, exist_ok=True)

    safe_name = family.replace(" ", "_").lower()
    cache_path = os.path.join(FONT_CACHE_DIR, f"{safe_name}-{weight}.ttf")

    if os.path.isfile(cache_path):
        return cache_path

    # Convert family name to directory format: "Playfair Display" -> "playfairdisplay"
    family_dir = family.lower().replace(" ", "")

    try:
        # List files in the font directory via GitHub API
        api_url = GITHUB_FONTS_API.format(family_dir=family_dir)
        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": "agentspace-blog-cover-pic",
                "Accept": "application/vnd.github.v3+json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            files = json.loads(resp.read().decode("utf-8"))

        # Find the best TTF file:
        # 1. Prefer static weight-specific files (e.g., Inter-Bold.ttf for weight 700)
        # 2. Fall back to variable font (e.g., Inter[opsz,wght].ttf)
        weight_name_map = {
            100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular",
            500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black",
        }
        weight_name = weight_name_map.get(weight, "Regular")

        download_url = None
        variable_url = None

        for f in files:
            name = f.get("name", "")
            url = f.get("download_url")
            if not name.endswith(".ttf") or not url:
                continue
            # Skip italic variants
            if "Italic" in name and "Italic" not in family:
                continue
            # Check for static weight match
            if f"-{weight_name}." in name or f"_{weight_name}." in name:
                download_url = url
                break
            # Variable font (contains [] in name)
            if "[" in name and "Italic" not in name:
                variable_url = url

        # Also check static/ subdirectory if exists
        if not download_url:
            for f in files:
                if f.get("type") == "dir" and f.get("name") == "static":
                    static_url = f"{api_url}/static"
                    req2 = urllib.request.Request(
                        static_url,
                        headers={
                            "User-Agent": "agentspace-blog-cover-pic",
                            "Accept": "application/vnd.github.v3+json",
                        },
                    )
                    try:
                        with urllib.request.urlopen(req2, timeout=15) as resp2:
                            static_files = json.loads(resp2.read().decode("utf-8"))
                        for sf in static_files:
                            sname = sf.get("name", "")
                            surl = sf.get("download_url")
                            if not sname.endswith(".ttf") or not surl:
                                continue
                            if "Italic" in sname and "Italic" not in family:
                                continue
                            if f"-{weight_name}." in sname or f"_{weight_name}." in sname:
                                download_url = surl
                                break
                    except Exception:
                        pass
                    break

        # Use variable font as fallback
        if not download_url:
            download_url = variable_url

        if not download_url:
            print(f"Warning: No TTF found for Google Font '{family}' (weight {weight})", file=sys.stderr)
            return None

        print(f"Downloading Google Font: {family} (weight {weight})...")
        urllib.request.urlretrieve(download_url, cache_path)
        print(f"Cached at: {cache_path}")
        return cache_path

    except (urllib.error.URLError, OSError, ValueError) as e:
        print(f"Warning: Failed to download Google Font '{family}': {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Font Awesome (free/open-source icons)
# ---------------------------------------------------------------------------

FA_RELEASE_URL = "https://github.com/FortAwesome/Font-Awesome/releases/download/6.5.1/fontawesome-free-6.5.1-web.zip"
FA_CACHE_DIR = os.path.join(BASE_DIR, ".font-cache", "fontawesome")

# Maps icon style to the font file name inside the Font Awesome zip
FA_STYLE_MAP = {
    "solid": "fa-solid-900.ttf",
    "regular": "fa-regular-400.ttf",
    "brands": "fa-brands-400.ttf",
}

# Common icon name -> Unicode codepoint mapping (subset of Font Awesome Free)
# Full list: https://fontawesome.com/v6/icons?o=r&m=free
FA_ICONS = {
    # General
    "star": "\uf005", "heart": "\uf004", "check": "\uf00c", "xmark": "\uf00d",
    "gear": "\uf013", "home": "\uf015", "user": "\uf007", "envelope": "\uf0e0",
    "bell": "\uf0f3", "bookmark": "\uf02e", "calendar": "\uf133", "clock": "\uf017",
    "comment": "\uf075", "eye": "\uf06e", "fire": "\uf06d", "flag": "\uf024",
    "folder": "\uf07b", "image": "\uf03e", "link": "\uf0c1", "lock": "\uf023",
    "pen": "\uf304", "search": "\uf002", "share": "\uf064", "shield": "\uf132",
    "tag": "\uf02b", "trash": "\uf1f8", "thumbs-up": "\uf164", "bolt": "\uf0e7",
    "circle": "\uf111", "square": "\uf0c8", "arrow-right": "\uf061",
    "arrow-left": "\uf060", "arrow-up": "\uf062", "arrow-down": "\uf063",
    # Tech
    "code": "\uf121", "database": "\uf1c0", "server": "\uf233", "cloud": "\uf0c2",
    "terminal": "\uf120", "bug": "\uf188", "robot": "\uf544", "microchip": "\uf2db",
    "globe": "\uf0ac", "wifi": "\uf1eb", "laptop": "\uf109", "mobile": "\uf3ce",
    # Content
    "newspaper": "\uf1ea", "book": "\uf02d", "file": "\uf15b", "pen-to-square": "\uf044",
    "quote-left": "\uf10d", "quote-right": "\uf10e", "rss": "\uf09e",
    "lightbulb": "\uf0eb", "rocket": "\uf135", "trophy": "\uf091",
    # Brands (use style="brands")
    "github": "\uf09b", "twitter": "\uf099", "linkedin": "\uf08c",
    "youtube": "\uf167", "docker": "\uf395", "python": "\uf3e2",
    "js": "\uf3b8", "react": "\uf41b", "node": "\uf419", "rust": "\ue07a",
}


def download_fontawesome() -> str | None:
    """Download Font Awesome Free and cache it. Returns path to fonts dir or None."""
    fa_fonts_dir = os.path.join(FA_CACHE_DIR, "webfonts")

    # Check if already cached
    solid_path = os.path.join(fa_fonts_dir, FA_STYLE_MAP["solid"])
    if os.path.isfile(solid_path):
        return fa_fonts_dir

    os.makedirs(FA_CACHE_DIR, exist_ok=True)

    try:
        print("Downloading Font Awesome Free...")
        req = urllib.request.Request(FA_RELEASE_URL)
        with urllib.request.urlopen(req, timeout=30) as resp:
            zip_data = BytesIO(resp.read())

        with zipfile.ZipFile(zip_data) as zf:
            os.makedirs(fa_fonts_dir, exist_ok=True)
            for name in zf.namelist():
                if "/webfonts/" in name and name.endswith(".ttf"):
                    filename = os.path.basename(name)
                    target = os.path.join(fa_fonts_dir, filename)
                    with zf.open(name) as src, open(target, "wb") as dst:
                        dst.write(src.read())

        print(f"Font Awesome cached at: {fa_fonts_dir}")
        return fa_fonts_dir

    except (urllib.error.URLError, OSError, zipfile.BadZipFile) as e:
        print(f"Warning: Failed to download Font Awesome: {e}", file=sys.stderr)
        return None


def get_fa_icon_font(size: int, style: str = "solid") -> ImageFont.FreeTypeFont | None:
    """Get a Font Awesome font object for rendering icons."""
    fa_dir = download_fontawesome()
    if not fa_dir:
        return None
    font_file = FA_STYLE_MAP.get(style, FA_STYLE_MAP["solid"])
    font_path = os.path.join(fa_dir, font_file)
    if os.path.isfile(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    return None


def draw_fa_icon(
    img: Image.Image,
    icon_name: str,
    x: int,
    y: int,
    size: int = 40,
    color: str | tuple = "#FFFFFF",
    style: str = "solid",
    anchor: str = "lt",
):
    """Draw a Font Awesome icon on the image.

    Args:
        icon_name: Name like "star", "code", "github" (see FA_ICONS dict)
        x, y: Position
        size: Font size in pixels
        color: Hex string or RGB tuple
        style: "solid", "regular", or "brands"
        anchor: Pillow text anchor (default: left-top)
    """
    char = FA_ICONS.get(icon_name)
    if not char:
        print(f"Warning: Unknown Font Awesome icon '{icon_name}'", file=sys.stderr)
        return

    font = get_fa_icon_font(size, style)
    if not font:
        return

    draw = ImageDraw.Draw(img)
    draw.text((x, y), char, font=font, fill=color, anchor=anchor)


# ---------------------------------------------------------------------------
# Font resolution
# ---------------------------------------------------------------------------

FONT_SEARCH_PATHS = [
    # macOS
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def resolve_font(font_spec: str | None) -> str | None:
    """Resolve a font specification to a file path.

    Accepts:
      - None: fall through to system font discovery
      - A file path: "/path/to/font.ttf"
      - A Google Fonts name: "google:Inter" or "google:Playfair Display:400"
    """
    if not font_spec:
        for p in FONT_SEARCH_PATHS:
            if os.path.isfile(p):
                return p
        return None

    # Local file path
    if os.path.isfile(font_spec):
        return font_spec

    # Google Fonts: "google:FamilyName" or "google:FamilyName:weight"
    if font_spec.startswith("google:"):
        parts = font_spec[7:].split(":")
        family = parts[0].strip()
        weight = int(parts[1]) if len(parts) > 1 else 700
        path = download_google_font(family, weight)
        if path:
            return path
        # Fall through to system fonts
        for p in FONT_SEARCH_PATHS:
            if os.path.isfile(p):
                return p
        return None

    # Treat as a file path that doesn't exist — warn and fall back
    print(f"Warning: Font not found: '{font_spec}', falling back to system font", file=sys.stderr)
    for p in FONT_SEARCH_PATHS:
        if os.path.isfile(p):
            return p
    return None


def get_font(size: int, font_spec: str | None = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return a font object at the given size."""
    resolved = resolve_font(font_spec)
    if resolved:
        try:
            return ImageFont.truetype(resolved, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Text wrapping
# ---------------------------------------------------------------------------

def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int = 4) -> list[str]:
    """Word-wrap text to fit within max_width, capping at max_lines."""
    words = text.split()
    lines: list[str] = []
    current_line = ""

    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Truncate with ellipsis if too many lines
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last:
            candidate = last + "..."
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] <= max_width:
                lines[-1] = candidate
                break
            last = last[:-1]

    return lines


def text_block_height(draw: ImageDraw.ImageDraw, lines: list[str], font, line_spacing: int = 8) -> int:
    """Calculate total height of a wrapped text block."""
    total = 0
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        total += bbox[3] - bbox[1]
        if i < len(lines) - 1:
            total += line_spacing
    return total


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font,
    x: int,
    y: int,
    fill: str | tuple,
    line_spacing: int = 8,
    anchor: str = "center",
):
    """Draw a multi-line text block."""
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        if anchor == "center":
            draw.text(((WIDTH - line_w) / 2, y), line, font=font, fill=fill)
        else:
            draw.text((x, y), line, font=font, fill=fill)
        y += line_h + line_spacing


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def lighten(rgb: tuple, factor: float = 0.3) -> tuple:
    """Lighten an RGB color."""
    return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)


def darken(rgb: tuple, factor: float = 0.3) -> tuple:
    """Darken an RGB color."""
    return tuple(max(0, int(c * (1 - factor))) for c in rgb)


# ---------------------------------------------------------------------------
# Gradient drawing
# ---------------------------------------------------------------------------

def draw_gradient(img: Image.Image, color_start: tuple, color_end: tuple, direction: str = "vertical"):
    """Draw a gradient background.

    Directions: vertical (top-to-bottom), horizontal (left-to-right),
                diagonal-down (top-left to bottom-right),
                diagonal-up (bottom-left to top-right).
    """
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        for x in range(0, WIDTH, 1):
            if direction == "vertical":
                ratio = y / HEIGHT
            elif direction == "horizontal":
                ratio = x / WIDTH
            elif direction == "diagonal-down":
                ratio = (x / WIDTH + y / HEIGHT) / 2
            elif direction == "diagonal-up":
                ratio = (x / WIDTH + (HEIGHT - y) / HEIGHT) / 2
            else:
                ratio = y / HEIGHT

            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            draw.point((x, y), fill=(r, g, b))


def draw_gradient_fast(img: Image.Image, color_start: tuple, color_end: tuple, direction: str = "vertical"):
    """Draw a gradient background (fast line-based for vertical/horizontal)."""
    draw = ImageDraw.Draw(img)

    if direction in ("vertical",):
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    elif direction == "horizontal":
        for x in range(WIDTH):
            ratio = x / WIDTH
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            draw.line([(x, 0), (x, HEIGHT)], fill=(r, g, b))
    else:
        # Diagonal gradients — draw per-pixel in 4px blocks for speed
        for y in range(0, HEIGHT, 2):
            for x in range(0, WIDTH, 2):
                if direction == "diagonal-down":
                    ratio = (x / WIDTH + y / HEIGHT) / 2
                else:  # diagonal-up
                    ratio = (x / WIDTH + (HEIGHT - y) / HEIGHT) / 2
                r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
                draw.rectangle([x, y, x + 2, y + 2], fill=(r, g, b))


# ---------------------------------------------------------------------------
# Decorative elements
# ---------------------------------------------------------------------------

def draw_diagonal_stripe(draw: ImageDraw.ImageDraw, accent: tuple, alpha: int = 60):
    """Draw a decorative diagonal accent stripe."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    points = [(WIDTH * 0.6, 0), (WIDTH, 0), (WIDTH, HEIGHT * 0.4), (WIDTH * 0.3, HEIGHT)]
    ov_draw.polygon(points, fill=(*accent, alpha))
    return overlay


def draw_corner_circles(accent: tuple, alpha: int = 40) -> Image.Image:
    """Draw decorative corner circles."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    # Top-right circle
    r1 = 180
    ov_draw.ellipse(
        [WIDTH - r1 - 30, -r1 + 40, WIDTH + r1 - 30, r1 + 40],
        fill=(*accent, alpha),
    )
    # Bottom-left circle
    r2 = 140
    ov_draw.ellipse(
        [-r2 + 50, HEIGHT - r2 - 20, r2 + 50, HEIGHT + r2 - 20],
        fill=(*accent, alpha),
    )
    return overlay


def draw_dot_pattern(accent: tuple, alpha: int = 25) -> Image.Image:
    """Draw a subtle dot grid pattern."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    spacing = 40
    dot_r = 2
    for x in range(0, WIDTH, spacing):
        for y in range(0, HEIGHT, spacing):
            ov_draw.ellipse(
                [x - dot_r, y - dot_r, x + dot_r, y + dot_r],
                fill=(*accent, alpha),
            )
    return overlay


def apply_vignette(img: Image.Image, strength: float = 0.4) -> Image.Image:
    """Apply a subtle vignette (darkened corners)."""
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(vignette)
    cx, cy = WIDTH / 2, HEIGHT / 2
    max_dist = math.sqrt(cx**2 + cy**2)
    for y in range(0, HEIGHT, 4):
        for x in range(0, WIDTH, 4):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ratio = dist / max_dist
            a = int(255 * ratio * strength)
            ov_draw.rectangle([x, y, x + 4, y + 4], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, vignette)
    return img


# ---------------------------------------------------------------------------
# Layout: Feature image (full design)
# ---------------------------------------------------------------------------

def generate_feature(
    title: str,
    subtitle: str,
    author: str,
    brand_color: tuple,
    accent_color: tuple,
    logo_path: str | None,
    fonts: dict,
    colors: dict,
    gradient_dir: str,
    gradient_start: tuple | None,
    gradient_end: tuple | None,
    icon: str | None = None,
    icon_style: str = "solid",
    icon_color: str | tuple | None = None,
) -> Image.Image:
    """Generate the blog feature/hero image with full design."""
    img = Image.new("RGBA", (WIDTH, HEIGHT))

    g_start = gradient_start or darken(brand_color, 0.1)
    g_end = gradient_end or brand_color
    draw_gradient_fast(img, g_start, g_end, gradient_dir)

    # Decorative elements
    stripe = draw_diagonal_stripe(ImageDraw.Draw(img), accent_color, alpha=50)
    img = Image.alpha_composite(img, stripe)
    circles = draw_corner_circles(accent_color, alpha=35)
    img = Image.alpha_composite(img, circles)
    dots = draw_dot_pattern(lighten(brand_color), alpha=20)
    img = Image.alpha_composite(img, dots)

    # Accent bar at top
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 6], fill=accent_color)

    # Logo
    if logo_path and os.path.isfile(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_h = 50
            logo_w = int(logo.width * (logo_h / logo.height))
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            img.paste(logo, (60, 30), logo)
        except Exception:
            pass

    # Font Awesome icon (top-right decorative, or centered above title if no logo)
    if icon:
        ic = icon_color or lighten(accent, 0.2)
        if logo_path and os.path.isfile(logo_path):
            draw_fa_icon(img, icon, WIDTH - 100, 25, size=50, color=ic, style=icon_style)
        else:
            draw_fa_icon(img, icon, WIDTH // 2, 40, size=60, color=ic, style=icon_style, anchor="mt")

    # Title
    title_font = get_font(fonts["title_size"], fonts["title_font"])
    margin = 60
    max_text_w = WIDTH - margin * 2
    title_lines = wrap_text(draw, title, title_font, max_text_w, max_lines=3)
    title_h = text_block_height(draw, title_lines, title_font)

    # Subtitle
    sub_lines = []
    sub_font = get_font(fonts["subtitle_size"], fonts["subtitle_font"])
    sub_h = 0
    if subtitle:
        sub_lines = wrap_text(draw, subtitle, sub_font, max_text_w, max_lines=2)
        sub_h = text_block_height(draw, sub_lines, sub_font)

    # Author
    author_font = get_font(fonts["author_size"], fonts["author_font"])
    author_h = 24 if author else 0

    # Vertical centering
    total_h = title_h + (sub_h + 16 if sub_h else 0) + (author_h + 24 if author else 0)
    start_y = (HEIGHT - total_h) / 2 + 10

    draw_text_block(draw, title_lines, title_font, 0, start_y, colors["title"], line_spacing=10)
    y = start_y + title_h + 16

    if sub_lines:
        draw_text_block(draw, sub_lines, sub_font, 0, y, colors["subtitle"], line_spacing=6)
        y += sub_h + 24

    if author:
        bbox = draw.textbbox((0, 0), author, font=author_font)
        aw = bbox[2] - bbox[0]
        draw.text(((WIDTH - aw) / 2, y), author, font=author_font, fill=colors["author"])

    # Bottom accent bar
    draw.rectangle([0, HEIGHT - 4, WIDTH, HEIGHT], fill=accent_color)

    img = apply_vignette(img, strength=0.3)
    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Layout: Open Graph image (simplified for social thumbnails)
# ---------------------------------------------------------------------------

def generate_og(
    title: str,
    brand_color: tuple,
    accent_color: tuple,
    logo_path: str | None,
    fonts: dict,
    colors: dict,
    gradient_dir: str,
    gradient_start: tuple | None,
    gradient_end: tuple | None,
) -> Image.Image:
    """Generate an OG image optimized for social sharing thumbnails."""
    img = Image.new("RGBA", (WIDTH, HEIGHT))

    g_start = gradient_start or brand_color
    g_end = gradient_end or darken(brand_color, 0.2)
    draw_gradient_fast(img, g_start, g_end, gradient_dir)

    # Semi-transparent dark overlay for contrast
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 80))
    img = Image.alpha_composite(img, overlay)

    # Accent stripe at bottom
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, HEIGHT - 8, WIDTH, HEIGHT], fill=accent_color)

    # Logo (smaller, top-center)
    if logo_path and os.path.isfile(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_h = 40
            logo_w = int(logo.width * (logo_h / logo.height))
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            img.paste(logo, ((WIDTH - logo_w) // 2, 40), logo)
        except Exception:
            pass

    # Title — larger text for thumbnail legibility
    title_font = get_font(fonts["og_title_size"], fonts["title_font"])
    draw = ImageDraw.Draw(img)
    margin = 80
    max_text_w = WIDTH - margin * 2
    title_lines = wrap_text(draw, title, title_font, max_text_w, max_lines=3)
    title_h = text_block_height(draw, title_lines, title_font, line_spacing=12)

    start_y = (HEIGHT - title_h) / 2 + 10
    draw_text_block(draw, title_lines, title_font, 0, start_y, colors["title"], line_spacing=12)

    return img.convert("RGB")


# ---------------------------------------------------------------------------
# Layout: Google Discover image (maximum contrast, text only)
# ---------------------------------------------------------------------------

def generate_google(
    title: str,
    brand_color: tuple,
    accent_color: tuple,
    fonts: dict,
    colors: dict,
    gradient_dir: str,
    gradient_start: tuple | None,
    gradient_end: tuple | None,
) -> Image.Image:
    """Generate a Google Discover-optimized image: large text, high contrast."""
    img = Image.new("RGBA", (WIDTH, HEIGHT))

    g_start = gradient_start or darken(brand_color, 0.4)
    g_end = gradient_end or darken(brand_color, 0.15)
    draw_gradient_fast(img, g_start, g_end, gradient_dir)

    # Thin accent line at top and bottom
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, WIDTH, 4], fill=accent_color)
    draw.rectangle([0, HEIGHT - 4, WIDTH, HEIGHT], fill=accent_color)

    # Title — very large for small thumbnails
    title_font = get_font(fonts["google_title_size"], fonts["title_font"])
    margin = 80
    max_text_w = WIDTH - margin * 2
    title_lines = wrap_text(draw, title, title_font, max_text_w, max_lines=3)
    title_h = text_block_height(draw, title_lines, title_font, line_spacing=14)

    start_y = (HEIGHT - title_h) / 2
    draw_text_block(draw, title_lines, title_font, 0, start_y, colors["title"], line_spacing=14)

    return img.convert("RGB")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate blog cover images with configurable fonts, colors, and gradients.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Font specification formats:
  /path/to/font.ttf          Local font file
  google:Inter               Google Font (bold weight)
  google:Playfair Display    Google Font with spaces
  google:Inter:400           Google Font with specific weight

Font Awesome icons (free/open-source):
  --icon code                Solid icon on feature image
  --icon github --icon-style brands   Brand icon
  Available: star, heart, code, rocket, globe, github, twitter, etc.

Examples:
  %(prog)s --title "Hello World" --slug hello \\
    --title-font "google:Inter" --subtitle-font "google:Lora" \\
    --title-color "#FFFFFF" --subtitle-color "#FFD700" \\
    --gradient-start "#1a1a2e" --gradient-end "#16213e" \\
    --gradient-direction diagonal-down \\
    --icon rocket --output-dir ./output
""",
    )

    # Content
    parser.add_argument("--title", required=True, help="Blog post title")
    parser.add_argument("--subtitle", default="", help="Tagline or summary")
    parser.add_argument("--author", default="", help="Author name")
    parser.add_argument("--slug", required=True, help="URL slug (used for filenames)")

    # Brand colors
    parser.add_argument("--brand-color", default="#1a1a2e", help="Primary brand color (hex)")
    parser.add_argument("--accent-color", default="#e94560", help="Accent color (hex)")

    # Per-element fonts (supports local paths or "google:FontName" or "google:FontName:weight")
    parser.add_argument("--font-path", default=None,
                        help="Default font for all text (local path or google:FontName)")
    parser.add_argument("--title-font", default=None,
                        help="Font for title (overrides --font-path)")
    parser.add_argument("--subtitle-font", default=None,
                        help="Font for subtitle (overrides --font-path)")
    parser.add_argument("--author-font", default=None,
                        help="Font for author (overrides --font-path)")

    # Per-element font sizes
    parser.add_argument("--title-size", type=int, default=48, help="Title font size (default: 48)")
    parser.add_argument("--subtitle-size", type=int, default=26, help="Subtitle font size (default: 26)")
    parser.add_argument("--author-size", type=int, default=20, help="Author font size (default: 20)")
    parser.add_argument("--og-title-size", type=int, default=56, help="OG image title size (default: 56)")
    parser.add_argument("--google-title-size", type=int, default=64, help="Google image title size (default: 64)")

    # Per-element text colors
    parser.add_argument("--title-color", default="#FFFFFF", help="Title text color (hex, default: #FFFFFF)")
    parser.add_argument("--subtitle-color", default=None,
                        help="Subtitle text color (hex, default: lightened accent color)")
    parser.add_argument("--author-color", default="#CCCCCC", help="Author text color (hex, default: #CCCCCC)")

    # Gradient configuration
    parser.add_argument("--gradient-start", default=None,
                        help="Gradient start color (hex, overrides brand-color-derived default)")
    parser.add_argument("--gradient-end", default=None,
                        help="Gradient end color (hex, overrides brand-color-derived default)")
    parser.add_argument("--gradient-direction", default="vertical",
                        choices=["vertical", "horizontal", "diagonal-down", "diagonal-up"],
                        help="Gradient direction (default: vertical)")

    # Font Awesome icon
    parser.add_argument("--icon", default=None,
                        help="Font Awesome icon name for feature image (e.g. 'code', 'rocket', 'github')")
    parser.add_argument("--icon-style", default="solid",
                        choices=["solid", "regular", "brands"],
                        help="Font Awesome icon style (default: solid; use 'brands' for github/twitter/etc)")
    parser.add_argument("--icon-color", default=None,
                        help="Icon color (hex, default: lightened accent)")

    # Other
    parser.add_argument("--logo", default=None, help="Path to logo PNG")
    parser.add_argument("--output-dir", required=True, help="Output directory")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    brand = hex_to_rgb(args.brand_color)
    accent = hex_to_rgb(args.accent_color)

    # Build fonts config — per-element font with fallback to --font-path
    fonts = {
        "title_font": args.title_font or args.font_path,
        "subtitle_font": args.subtitle_font or args.font_path,
        "author_font": args.author_font or args.font_path,
        "title_size": args.title_size,
        "subtitle_size": args.subtitle_size,
        "author_size": args.author_size,
        "og_title_size": args.og_title_size,
        "google_title_size": args.google_title_size,
    }

    # Build colors config
    subtitle_color = args.subtitle_color
    if subtitle_color:
        subtitle_color = subtitle_color
    else:
        subtitle_color = lighten(accent, 0.4)

    colors = {
        "title": args.title_color,
        "subtitle": subtitle_color,
        "author": args.author_color,
    }

    # Gradient config
    gradient_start = hex_to_rgb(args.gradient_start) if args.gradient_start else None
    gradient_end = hex_to_rgb(args.gradient_end) if args.gradient_end else None
    gradient_dir = args.gradient_direction

    # Pre-download Google Fonts if specified (so all 3 images share the cache)
    for spec in [fonts["title_font"], fonts["subtitle_font"], fonts["author_font"]]:
        if spec and spec.startswith("google:"):
            resolve_font(spec)

    # Feature image
    feature = generate_feature(
        args.title, args.subtitle, args.author, brand, accent,
        args.logo, fonts, colors, gradient_dir, gradient_start, gradient_end,
        icon=args.icon,
        icon_style=args.icon_style,
        icon_color=args.icon_color,
    )
    feature_path = os.path.join(args.output_dir, f"{args.slug}-feature.png")
    feature.save(feature_path)
    print(f"Feature image: {feature_path}")

    # OG image
    og = generate_og(
        args.title, brand, accent, args.logo, fonts, colors,
        gradient_dir, gradient_start, gradient_end,
    )
    og_path = os.path.join(args.output_dir, f"{args.slug}-og.png")
    og.save(og_path)
    print(f"OG image:      {og_path}")

    # Google image
    google = generate_google(
        args.title, brand, accent, fonts, colors,
        gradient_dir, gradient_start, gradient_end,
    )
    google_path = os.path.join(args.output_dir, f"{args.slug}-google.png")
    google.save(google_path)
    print(f"Google image:  {google_path}")

    print(f"\nAll images generated in {args.output_dir}")


if __name__ == "__main__":
    main()
