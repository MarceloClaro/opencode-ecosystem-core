"""Render the final manuscript PDF for page-by-page visual quality review."""

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "Journal_of_Dentistry_Example_OdontoCA.pdf"
OUT = ROOT / "manuscript_assets" / "review_pages"
OUT.mkdir(exist_ok=True)

pdf = pdfium.PdfDocument(str(PDF))
thumbs = []
for number, page in enumerate(pdf, 1):
    rendered = page.render(scale=1.5).to_pil().convert("RGB")
    rendered.save(OUT / f"page-{number}.png")
    thumb = ImageOps.contain(rendered, (400, 540))
    canvas = Image.new("RGB", (420, 575), "#eeeeee")
    canvas.paste(thumb, ((420 - thumb.width) // 2, 8))
    ImageDraw.Draw(canvas).text((12, 548), f"Page {number}", fill="#333333")
    thumbs.append(canvas)

columns = 3
rows = (len(thumbs) + columns - 1) // columns
sheet = Image.new("RGB", (columns * 420, rows * 575), "#dddddd")
for i, thumb in enumerate(thumbs):
    sheet.paste(thumb, ((i % columns) * 420, (i // columns) * 575))
sheet.save(OUT / "contact-sheet.png")
print(f"Rendered {len(pdf)} pages to {OUT}")
