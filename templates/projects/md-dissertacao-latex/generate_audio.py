#!/usr/bin/env python3
"""Dissertation to Audio MP3 - Resume-capable version."""

import asyncio
import os
import re
import sys
from pathlib import Path
import edge_tts

# === CONFIG ===
AUDIO_DIR = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\audio")
CHUNKS_DIR = AUDIO_DIR / "chunks"
TEXT_FILE = AUDIO_DIR / "dissertacao_texto_limpo.txt"
OUTPUT_FILE = AUDIO_DIR / "dissertacao_completa.mp3"
VOICE = "pt-BR-FranciscaNeural"
RATE = "-5%"
CHUNK_SIZE = 3500


def split_text_into_chunks(text: str, max_chars: int = CHUNK_SIZE) -> list:
    """Split text into chunks for TTS."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > max_chars:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 1 > max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
        else:
            if len(current_chunk) + len(para) + 2 > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return chunks


async def generate_chunk(chunk: str, index: int, output_path: Path):
    """Generate a single audio chunk."""
    communicate = edge_tts.Communicate(chunk, VOICE, rate=RATE)
    await communicate.save(str(output_path))


async def main():
    AUDIO_DIR.mkdir(exist_ok=True)
    CHUNKS_DIR.mkdir(exist_ok=True)

    # Load text
    text = TEXT_FILE.read_text(encoding='utf-8')
    chunks = split_text_into_chunks(text)
    total = len(chunks)
    print(f"Total blocos: {total}")

    # Check which chunks already exist
    existing = set()
    for f in CHUNKS_DIR.glob("chunk_*.mp3"):
        idx = int(f.stem.split("_")[1])
        existing.add(idx)

    print(f"Ja gerados: {len(existing)}")
    print(f"Restantes: {total - len(existing)}")

    # Generate missing chunks
    for i, chunk in enumerate(chunks):
        if i in existing:
            continue
        out = CHUNKS_DIR / f"chunk_{i:04d}.mp3"
        try:
            await generate_chunk(chunk, i, out)
            if (i + 1) % 5 == 0 or i == 0:
                print(f"  [{i+1}/{total}] OK ({len(chunk):,} chars)")
        except Exception as e:
            print(f"  [{i+1}/{total}] ERRO: {e}")
            # Retry once after 2 seconds
            await asyncio.sleep(2)
            try:
                await generate_chunk(chunk, i, out)
                print(f"  [{i+1}/{total}] Retry OK")
            except Exception as e2:
                print(f"  [{i+1}/{total}] Retry FAILED: {e2}")

    # Concatenate all chunks
    print("\nConcatenando...")
    chunk_files = sorted(CHUNKS_DIR.glob("chunk_*.mp3"), key=lambda f: int(f.stem.split("_")[1]))
    with open(OUTPUT_FILE, 'wb') as outfile:
        for cf in chunk_files:
            with open(cf, 'rb') as infile:
                outfile.write(infile.read())

    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    est_min = sum(len(c) for c in chunks) / 15
    print(f"\nFINAL: {OUTPUT_FILE}")
    print(f"Tamanho: {size_mb:.1f} MB")
    print(f"Duracao estimada: {est_min:.0f} min ({est_min/60:.1f} h)")


if __name__ == "__main__":
    asyncio.run(main())
