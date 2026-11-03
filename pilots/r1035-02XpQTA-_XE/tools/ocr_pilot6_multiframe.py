#!/usr/bin/env python3
"""Multi-frame OCR of burned-in English subtitles for source review."""
import json
import re
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'parts-extracted/parts/02XpQTA-_XE-P0006.mp4'
DIALOGUE = ROOT / 'pilot-P0006/dialogue-fit.json'
OUT = ROOT / 'pilot-P0006/ocr-multiframe'
OUT.mkdir(parents=True, exist_ok=True)
BOX = (250, 560, 1030, 715)


def clean(text):
    text = re.sub(r'[^A-Za-z0-9\',.!?;:()\- ]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip(' -|')


def score(text):
    letters = sum(ch.isalpha() for ch in text)
    words = len(re.findall(r'[A-Za-z]{2,}', text))
    bad = sum(not (ch.isalnum() or ch in " .,!?;:'()-") for ch in text)
    return letters + 2 * words - 2 * bad


def ocr_frame(frame):
    image = Image.open(frame).convert('RGB').crop(BOX)
    gray = image.convert('L').resize((image.width * 3, image.height * 3))
    binary = ImageOps.invert(ImageOps.autocontrast(gray).point(
        lambda value: 255 if value > 220 else 0))
    result = []
    for psm in (6, 7):
        text = clean(pytesseract.image_to_string(binary, lang='eng', config=f'--psm {psm}'))
        result.append({'text': text, 'score': score(text), 'psm': psm})
    return sorted(result, key=lambda item: item['score'], reverse=True)


dialogue = json.loads(DIALOGUE.read_text())
results = []
for unit in dialogue['units']:
    start, end = float(unit['start_part']), float(unit['end_part'])
    times = [start + (end - start) * fraction for fraction in (0.2, 0.5, 0.8)]
    variants = []
    for index, moment in enumerate(times):
        frame = OUT / f'{unit["id"]}-{index}.png'
        if not frame.exists():
            subprocess.run([
                'ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{moment:.3f}',
                '-i', str(PART), '-frames:v', '1', '-y', str(frame),
            ], check=True, timeout=120)
        for item in ocr_frame(frame):
            variants.append({'at_seconds': round(moment, 3), **item})
    variants.sort(key=lambda item: item['score'], reverse=True)
    unique = []
    seen = set()
    for item in variants:
        key = re.sub(r'[^a-z]', '', item['text'].lower())
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    results.append({
        'id': unit['id'], 'speaker': unit['speaker'],
        'start_part': unit['start_part'], 'end_part': unit['end_part'],
        'asr_tr': unit['source_text_tr'],
        'best_english': unique[0]['text'] if unique else '',
        'best_score': unique[0]['score'] if unique else -999,
        'variants': unique[:5],
    })
    print(unit['id'], repr(unique[0]['text'] if unique else ''), flush=True)
(OUT / 'english-ocr-multiframe.json').write_text(json.dumps({
    'schema_version': 1, 'part_id': dialogue['part_id'],
    'method': 'tesseract 5.5, 3 frames per ASR unit, threshold 220, psm 6/7',
    'crop_box': BOX, 'results': results,
    'limitations': ['OCR can still miss or mix consecutive subtitle lines',
                    'English is a translation, not the Turkish source',
                    'human review required'],
}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'units': len(results), 'out': str(OUT / 'english-ocr-multiframe.json')}))
