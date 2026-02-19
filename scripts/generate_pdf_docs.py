"""
Generate PDFs with image-based visuals from markdown docs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT_DIR / "reports" / "pdf_assets"
OUTPUT_DIR = ROOT_DIR / "reports" / "pdf"

PALETTE = {
    "navy": (20, 40, 80),
    "blue": (52, 120, 200),
    "teal": (44, 160, 155),
    "mint": (200, 238, 232),
    "light": (246, 249, 252),
    "grey": (120, 130, 140),
    "ink": (28, 32, 36),
    "accent": (242, 153, 74),
}


def _ensure_dirs() -> None:
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _draw_background(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for y in range(height):
        shade = 246 - int(8 * (y / height))
        draw.line([(0, y), (width, y)], fill=(shade, shade + 2, shade + 4))


def _draw_box(
    draw: ImageDraw.ImageDraw,
    box,
    text: str,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int],
    text_color: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    shadow = (x0 + 4, y0 + 4, x1 + 4, y1 + 4)
    draw.rectangle(shadow, outline=None, fill=(210, 218, 228))
    draw.rectangle(box, outline=outline, width=2, fill=fill)
    x0, y0, x1, y1 = box
    font = ImageFont.load_default()
    text_w = draw.textlength(text, font=font)
    text_h = 10
    draw.text(
        ((x0 + x1) / 2 - text_w / 2, (y0 + y1) / 2 - text_h / 2),
        text,
        font=font,
        fill=text_color,
    )


def _draw_arrow(draw: ImageDraw.ImageDraw, start, end) -> None:
    draw.line([start, end], fill=PALETTE["grey"], width=2)
    # Simple arrow head
    ex, ey = end
    draw.polygon(
        [(ex, ey), (ex - 6, ey - 4), (ex - 6, ey + 4)],
        fill=(60, 60, 60),
    )


def create_diagram_architecture(path: Path) -> None:
    img = PILImage.new("RGB", (900, 640), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    _draw_background(draw, 900, 640)

    boxes = [
        (120, 60, 780, 140, "User Interface Layer"),
        (120, 190, 780, 270, "Application Layer"),
        (120, 320, 780, 400, "Business Logic Layer"),
        (120, 450, 780, 530, "Data and Storage Layer"),
    ]

    fills = [PALETTE["mint"], (226, 236, 252), (233, 246, 241), (255, 242, 226)]
    for idx, (x0, y0, x1, y1, label) in enumerate(boxes):
        fill = fills[idx % len(fills)]
        _draw_box(draw, (x0, y0, x1, y1), label, fill, PALETTE["blue"], PALETTE["ink"])

    _draw_arrow(draw, (450, 140), (450, 190))
    _draw_arrow(draw, (450, 270), (450, 320))
    _draw_arrow(draw, (450, 400), (450, 450))

    img.save(path)


def create_diagram_data_flow(path: Path) -> None:
    img = PILImage.new("RGB", (900, 680), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    _draw_background(draw, 900, 680)

    steps = [
        (140, 40, 760, 110, "File Upload"),
        (140, 140, 760, 210, "Document Loading"),
        (140, 240, 760, 310, "Chunking and Embeddings"),
        (140, 340, 760, 410, "FAISS Index Creation"),
        (140, 440, 760, 510, "Persistence"),
        (140, 540, 760, 610, "RAG Query Execution"),
    ]

    for idx, (x0, y0, x1, y1, label) in enumerate(steps):
        fill = (230 + idx * 3, 242 - idx * 2, 252 - idx * 4)
        _draw_box(draw, (x0, y0, x1, y1), label, fill, PALETTE["teal"], PALETTE["ink"])

    for _, y0, _, y1, _ in steps[:-1]:
        _draw_arrow(draw, (450, y1), (450, y1 + 30))

    img.save(path)


def create_diagram_incident_flow(path: Path) -> None:
    img = PILImage.new("RGB", (900, 520), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    _draw_background(draw, 900, 520)

    steps = [
        (100, 60, 800, 130, "Incident Detected"),
        (100, 160, 800, 230, "Assess Severity"),
        (100, 260, 800, 330, "Investigate and Mitigate"),
        (100, 360, 800, 430, "Verify and Close"),
    ]

    fills = [(255, 238, 230), (255, 247, 219), (232, 244, 248), (226, 236, 252)]
    for idx, (x0, y0, x1, y1, label) in enumerate(steps):
        _draw_box(draw, (x0, y0, x1, y1), label, fills[idx % len(fills)], PALETTE["accent"], PALETTE["ink"])

    for _, y0, _, y1, _ in steps[:-1]:
        _draw_arrow(draw, (450, y1), (450, y1 + 30))

    img.save(path)


def create_diagram_backup_flow(path: Path) -> None:
    img = PILImage.new("RGB", (900, 520), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    _draw_background(draw, 900, 520)

    steps = [
        (120, 60, 780, 130, "Daily Backup"),
        (120, 180, 780, 250, "Weekly Rotation"),
        (120, 300, 780, 370, "Monthly Archive"),
        (120, 420, 780, 490, "Restore Validation"),
    ]

    fills = [(233, 246, 241), (226, 236, 252), (255, 242, 226), (232, 244, 248)]
    for idx, (x0, y0, x1, y1, label) in enumerate(steps):
        _draw_box(draw, (x0, y0, x1, y1), label, fills[idx % len(fills)], PALETTE["teal"], PALETTE["ink"])

    for _, y0, _, y1, _ in steps[:-1]:
        _draw_arrow(draw, (450, y1), (450, y1 + 30))

    img.save(path)


def create_diagram_module_integration(path: Path) -> None:
    width, height = 1100, 720
    img = PILImage.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    _draw_background(draw, width, height)

    left = (60, 80, 360, 150, "app/main.py")
    center = [
        (420, 60, 740, 120, "src/config.py"),
        (420, 140, 740, 200, "src/llm.py"),
        (420, 220, 740, 280, "src/loaders.py"),
        (420, 300, 740, 360, "src/database.py"),
        (420, 380, 740, 440, "src/summary_metrics.py"),
        (420, 460, 740, 520, "src/metrics_tool.py"),
        (420, 540, 740, 600, "src/utils.py"),
    ]
    right = [
        (800, 60, 1040, 120, "env/config.py"),
        (800, 140, 1040, 200, "env/secrets.py"),
        (800, 240, 1040, 300, "data/raw"),
        (800, 320, 1040, 380, "data/processed"),
        (800, 400, 1040, 460, "vector_db"),
        (800, 480, 1040, 540, "scripts/*.py"),
    ]

    _draw_box(draw, left[:4], left[4], (226, 236, 252), PALETTE["blue"], PALETTE["ink"])

    center_fill = (233, 246, 241)
    for box in center:
        _draw_box(draw, box[:4], box[4], center_fill, PALETTE["teal"], PALETTE["ink"])

    right_fills = [(255, 242, 226), (232, 244, 248), (255, 238, 230)]
    for idx, box in enumerate(right):
        _draw_box(
            draw,
            box[:4],
            box[4],
            right_fills[idx % len(right_fills)],
            PALETTE["accent"],
            PALETTE["ink"],
        )

    # App to core modules
    for box in center[:5]:
        _draw_arrow(draw, (360, 115), (420, (box[1] + box[3]) / 2))

    # Config to env
    _draw_arrow(draw, (740, 90), (800, 90))
    _draw_arrow(draw, (740, 170), (800, 170))

    # Loaders and summary metrics to data
    _draw_arrow(draw, (740, 250), (800, 270))
    _draw_arrow(draw, (740, 410), (800, 350))

    # Database to vector DB
    _draw_arrow(draw, (740, 330), (800, 430))

    # Metrics tool to processed data
    _draw_arrow(draw, (740, 490), (800, 350))

    # Scripts to modules
    _draw_arrow(draw, (800, 510), (740, 490))

    img.save(path)


def create_diagrams() -> Dict[str, Path]:
    _ensure_dirs()
    files = {
        "architecture": DIAGRAM_DIR / "architecture.png",
        "data_flow": DIAGRAM_DIR / "data_flow.png",
        "incident_flow": DIAGRAM_DIR / "incident_flow.png",
        "backup_flow": DIAGRAM_DIR / "backup_flow.png",
        "module_integration": DIAGRAM_DIR / "module_integration.png",
    }

    create_diagram_architecture(files["architecture"])
    create_diagram_data_flow(files["data_flow"])
    create_diagram_incident_flow(files["incident_flow"])
    create_diagram_backup_flow(files["backup_flow"])
    create_diagram_module_integration(files["module_integration"])

    return files


def _build_styles():
    styles = getSampleStyleSheet()
    styles["Heading1"].fontSize = 18
    styles["Heading1"].leading = 22
    styles["Heading1"].spaceAfter = 10
    styles["Heading1"].textColor = colors.HexColor("#14305A")

    styles["Heading2"].fontSize = 14
    styles["Heading2"].leading = 18
    styles["Heading2"].spaceAfter = 8
    styles["Heading2"].textColor = colors.HexColor("#2C6FAE")

    styles["Heading3"].fontSize = 12
    styles["Heading3"].leading = 16
    styles["Heading3"].spaceAfter = 6
    styles["Heading3"].textColor = colors.HexColor("#3C7C77")

    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=10.5,
            leading=14,
            spaceAfter=6,
            textColor=colors.HexColor("#1F2933"),
        )
    )
    styles["Code"].fontSize = 9
    styles["Code"].leading = 12
    styles["Code"].backColor = colors.whitesmoke
    styles["Code"].borderWidth = 0.5
    styles["Code"].borderColor = colors.lightgrey
    styles["Code"].borderPadding = 6
    return styles


def _add_image(story, image_path: Path) -> None:
    if not image_path.exists():
        return
    img = Image(str(image_path))
    max_width = A4[0] - 72  # 36pt margins on each side
    img.drawWidth = max_width
    img.drawHeight = img.imageHeight * (max_width / img.imageWidth)
    story.append(Spacer(1, 6))
    story.append(img)
    story.append(Spacer(1, 10))


def _match_image_for_heading(title: str, image_map: Dict[str, Path]) -> Path | None:
    title_lower = title.lower()
    for key, image_path in image_map.items():
        if key.lower() in title_lower:
            return image_path
    return None


def parse_markdown(md_text: str, image_map: Dict[str, Path]) -> List:
    styles = _build_styles()
    story: List = []

    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.startswith("# "):
            title = line[2:].strip()
            story.append(Paragraph(title, styles["Heading1"]))
            img_path = _match_image_for_heading(title, image_map)
            if img_path:
                _add_image(story, img_path)
            i += 1
            continue

        if line.startswith("## "):
            title = line[3:].strip()
            story.append(Paragraph(title, styles["Heading2"]))
            img_path = _match_image_for_heading(title, image_map)
            if img_path:
                _add_image(story, img_path)
            i += 1
            continue

        if line.startswith("### "):
            title = line[4:].strip()
            story.append(Paragraph(title, styles["Heading3"]))
            img_path = _match_image_for_heading(title, image_map)
            if img_path:
                _add_image(story, img_path)
            i += 1
            continue

        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code_text = "\n".join(code_lines)
            story.append(Preformatted(code_text, styles["Code"]))
            story.append(Spacer(1, 6))
            continue

        if line.strip().startswith("|") and "|" in line:
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            story.append(Preformatted("\n".join(table_lines), styles["Code"]))
            story.append(Spacer(1, 6))
            continue

        if line.strip().startswith("- ") or line.strip().startswith("* "):
            items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                item_text = lines[i].strip()[2:].strip()
                items.append(ListItem(Paragraph(item_text, styles["Body"])))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet"))
            story.append(Spacer(1, 6))
            continue

        if not line.strip():
            i += 1
            continue

        paragraph_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i].rstrip()
            if not next_line.strip():
                break
            if next_line.startswith("#") or next_line.startswith("-") or next_line.startswith("*"):
                break
            if next_line.startswith("```"):
                break
            paragraph_lines.append(next_line)
            i += 1

        paragraph_text = " ".join(part.strip() for part in paragraph_lines)
        story.append(Paragraph(paragraph_text, styles["Body"]))
        story.append(Spacer(1, 4))

    return story


def build_pdf(md_path: Path, pdf_path: Path, image_map: Dict[str, Path]) -> None:
    text = md_path.read_text(encoding="utf-8")
    story = parse_markdown(text, image_map)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=md_path.stem,
    )
    doc.build(story)


def main() -> None:
    _ensure_dirs()
    diagrams = create_diagrams()

    lld_md = ROOT_DIR / "LOW_LEVEL_DESIGN.md"
    support_md = ROOT_DIR / "PRODUCTION_SUPPORT_GUIDE.md"

    lld_pdf = OUTPUT_DIR / "LOW_LEVEL_DESIGN.pdf"
    support_pdf = OUTPUT_DIR / "PRODUCTION_SUPPORT_GUIDE.pdf"

    lld_images = {
        "Architecture Design": diagrams["architecture"],
        "Data Flow": diagrams["data_flow"],
        "Module Integration Data Flow": diagrams["module_integration"],
    }
    support_images = {
        "Incident Response": diagrams["incident_flow"],
        "Backup & Recovery": diagrams["backup_flow"],
    }

    build_pdf(lld_md, lld_pdf, lld_images)
    build_pdf(support_md, support_pdf, support_images)

    print(f"Created: {lld_pdf}")
    print(f"Created: {support_pdf}")


if __name__ == "__main__":
    main()
