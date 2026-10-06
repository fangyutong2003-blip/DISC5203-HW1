"""Shared cross-platform helpers for the DISC 5203 coursework scripts."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont


def default_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return a readable font without assuming a Windows installation."""

    names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
    ]
    platform_paths = [
        Path("C:/Windows/Fonts"),
        Path("/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation2"),
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
        for directory in platform_paths:
            candidate = directory / name
            if candidate.exists():
                try:
                    return ImageFont.truetype(str(candidate), size)
                except OSError:
                    pass
    return ImageFont.load_default()
