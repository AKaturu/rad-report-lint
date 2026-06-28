"""Generate stable synthetic demo media for the GitHub README."""

from __future__ import annotations

from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs" / "assets"
WIDTH = 1280
HEIGHT = 720


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for name in candidates:
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    color: str,
    bold: bool = False,
) -> None:
    draw.text(xy, value, fill=color, font=font(size, bold))


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = "#ffffff") -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill)


def render_frame() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f7f8fb")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 92), fill="#133047")
    text(draw, (44, 28), "rad-report-lint", 34, "#ffffff", True)
    text(draw, (888, 34), "Deterministic report quality checks", 20, "#c8d8e8")

    card(draw, (44, 124, 594, 630))
    text(draw, (76, 154), "Input report", 24, "#2b405f", True)
    report = [
        "FINDINGS:",
        "Right lower-lobe pulmonary nodule measuring 8 mm.",
        "No pleural effusion.",
        "",
        "IMPRESSION:",
        "No pulmonary nodule.",
        "Recommend follow-up CT.",
    ]
    y = 210
    for line in report:
        fill = "#b42318" if "nodule" in line.lower() or "follow-up" in line.lower() else "#344054"
        text(draw, (82, y), line, 22, fill, line.endswith(":"))
        y += 42

    card(draw, (636, 124, 1236, 630))
    text(draw, (668, 154), "Lint results", 24, "#2b405f", True)
    issues = [
        (
            "ERROR",
            "findings-impression-contradiction",
            "Findings mention right lung nodule, but impression says none.",
        ),
        (
            "WARNING",
            "recommendation-without-interval",
            "Follow-up recommendation is missing an interval.",
        ),
        ("INFO", "unexpanded-abbreviations", "CT appears without first-use expansion."),
    ]
    y = 214
    colors = {"ERROR": "#b42318", "WARNING": "#b76e00", "INFO": "#175cd3"}
    for severity, rule, detail in issues:
        draw.rounded_rectangle((668, y - 10, 1204, y + 96), radius=14, fill="#f2f4f7")
        text(draw, (694, y + 4), severity, 18, colors[severity], True)
        text(draw, (814, y + 4), rule, 19, "#243b67", True)
        text(draw, (694, y + 43), detail, 17, "#475467")
        y += 126

    text(
        draw,
        (44, 676),
        "Synthetic scenario output - safe for demos, READMEs, and CI screenshots.",
        18,
        "#667085",
    )
    return image


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    frame = render_frame()
    frame.save(ASSET_DIR / "demo-poster.png")
    frames = [frame.copy() for _ in range(4)]
    frames[0].save(
        ASSET_DIR / "demo.gif", save_all=True, append_images=frames[1:], duration=650, loop=0
    )
    with imageio.get_writer(ASSET_DIR / "demo.mp4", fps=1, codec="libx264", quality=8) as writer:
        for still in frames:
            writer.append_data(np.asarray(still))


if __name__ == "__main__":
    main()
