#!/usr/bin/env python3
"""OCR the burned-in English subtitles for pilot P0006 source review."""
import json
import re
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'parts-extracted/parts/02XpQTA-_XE-P0006.mp4'
DIALOGUE = ROOT / 'pilot-P0006/dialogue-fit.json'
OUT = ROOT / 'pilot-P0006/ocr'
OUT.mkdir(parents=True, exist_ok=True)
BOX = (250, 560, 1030, 715)


def clean(text):
    text = re.sub(r'[^A-Za-z0-9\',.!?;:()\- ]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip(' -|')
    return text


def score(text):
    letters = sum(ch.isalpha() for ch in text)
    words = len(re.findall(r'[A-Za-z]{2,}', text))
    bad = sum(not (ch.isalnum() or ch in " .,!?;:'()-") for ch in text)
    return letters + 2 * words - 2 * bad


dialogue = json.loads(DIALOGUE.read_text())
results = []
for unit in dialogue['units']:
    midpoint = (unit['start_part'] + unit['end_part']) / 2
    frame = OUT / f'{unit["id"]}.png'
    if not frame.exists():
        subprocess.run([
            'ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{midpoint:.3f}',
            '-i', str(PART), '-frames:v', '1', '-y', str(frame),
        ], check=True, timeout=120)
    image = Image.open(frame).convert('RGB').crop(BOX)
    best = ''
    best_score = -10**9
    best_config = None
    for scale in (3, 4):
        gray = image.convert('L').resize((image.width * scale, image.height * scale))
        gray = ImageOps.autocontrast(gray)
        for threshold in (200, 210, 220, 230):
            binary = ImageOps.invert(gray.point(lambda value: 255 if value > threshold else 0))
            for psm in (6, 7):
                text = clean(pytesseract.image_to_string(
                    binary, lang='eng', config=f'--psm {psm}'))
                value = score(text)
                if value > best_score:
                    best, best_score, best_config = text, value, (scale, threshold, psm)
    results.append({
        'id': unit['id'], 'speaker': unit['speaker'],
        'start_part': unit['start_part'], 'end_part': unit['end_part'],
        'asr_tr': unit['source_text_tr'], 'english_ocr': best,
        'ocr_score': best_score, 'ocr_config': best_config,
    })
    print(unit['id'], repr(best), flush=True)
(OUT / 'english-ocr.json').write_text(json.dumps({
    'schema_version': 1, 'part_id': dialogue['part_id'],
    'method': 'tesseract 5.5 on burned-in bottom subtitles',
    'crop_box': BOX, 'results': results,
    'limitations': ['OCR can miss lines, merge frames or read background text',
                    'English subtitle is a translation, not the Turkish source',
                    'human review required'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'units': len(results), 'out': str(OUT / 'english-ocr.json')}))
