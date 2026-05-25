"""Shared helpers for the matplotlib → GIF pipeline.

We render via matplotlib's FuncAnimation → MP4 (ffmpeg) → palette-quantized
GIF (ffmpeg two-pass). The GIF is what embeds in Markdown; the MP4 stays
around as a higher-quality alternative.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.animation import FuncAnimation  # noqa: E402


def save_animation(
    anim: FuncAnimation,
    out_stem: str,
    *,
    fps: int = 10,
    width_px: int = 720,
) -> tuple[str, str]:
    """Save `anim` as both MP4 and a palette-quantized GIF beside `out_stem`.

    Returns (mp4_path, gif_path).
    """
    mp4_path = f"{out_stem}.mp4"
    gif_path = f"{out_stem}.gif"

    # 1. matplotlib → MP4 via ffmpeg writer.
    anim.save(
        mp4_path,
        writer="ffmpeg",
        fps=fps,
        dpi=100,
        bitrate=1200,
        extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"],
    )

    # 2. MP4 → GIF, two-pass for palette quality.
    with tempfile.TemporaryDirectory() as td:
        palette = os.path.join(td, "palette.png")
        filter_complex = (
            f"fps={fps},scale={width_px}:-1:flags=lanczos,palettegen=max_colors=128"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp4_path, "-vf", filter_complex, palette],
            check=True, capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", mp4_path, "-i", palette,
                "-lavfi", f"fps={fps},scale={width_px}:-1:flags=lanczos[x];[x][1:v]paletteuse",
                gif_path,
            ],
            check=True, capture_output=True,
        )

    size_kib = os.path.getsize(gif_path) / 1024
    print(f"  wrote {gif_path}  ({size_kib:.0f} KiB)")
    if size_kib > 2048:
        print(f"  WARNING: GIF >2 MiB — consider reducing frames or width")
    return mp4_path, gif_path


def style() -> None:
    """Consistent visual style across all animations."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.facecolor": "#f9fafb",
        "figure.facecolor": "white",
        "axes.edgecolor": "#6b7280",
        "axes.labelcolor": "#374151",
        "axes.titlecolor": "#111827",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "xtick.color": "#6b7280",
        "ytick.color": "#6b7280",
        "grid.color": "#e5e7eb",
        "axes.grid": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
