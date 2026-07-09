#!/usr/bin/env python3
"""
Dissertation to Audio MP3 Converter
Uses edge-tts (Microsoft Edge TTS) for high-quality Brazilian Portuguese speech.
"""

import asyncio
import os
import re
import sys
import tempfile
import shutil
from pathlib import Path

import pdfplumber
import edge_tts

# === CONFIGURATION ===
PDF_PATH = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\dissertacao.pdf")
OUTPUT_DIR = Path(r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\audio")
OUTPUT_FILE = OUTPUT_DIR / "dissertacao_completa.mp3"

# Voice: pt-BR-FranciscaNeural (female, natural) or pt-BR-AntonioNeural (male)
VOICE = "pt-BR-FranciscaNeural"
# Rate adjustment: "+0%" normal, "-10%" slower, "+10%" faster
RATE = "-5%"
# Chunk size for TTS (edge-tts limit ~4000 chars)
CHUNK_SIZE = 3500


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract full text from PDF, page by page."""
    print(f"[1/5] Extraindo texto de {pdf_path.name}...")
    with pdfplumber.open(pdf_path) as pdf:
        pages_text = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages_text.append(text)
            if (i + 1) % 20 == 0:
                print(f"  ... {i+1}/{len(pdf.pages)} paginas extraidas")
    full_text = "\n\n".join(pages_text)
    print(f"  Total: {len(full_text):,} caracteres, {len(full_text.split()):,} palavras")
    return full_text


def clean_text_for_tts(text: str) -> str:
    """Clean text for natural TTS reading."""
    print("[2/5] Limpando texto para leitura...")

    # Remove page numbers (standalone numbers)
    text = re.sub(r'\n\d{1,3}\n', '\n', text)

    # Remove headers/footers patterns
    text = re.sub(r'Metodologias Ativas.*?Educação Brasileira', '', text)
    text = re.sub(r'Fernando Ramos Passoni', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'doi\.org/\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)

    # Remove figure/table references that are just numbers
    text = re.sub(r'Fonte:\s*.*?\n', '\n', text)

    # Clean up multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    print(f"  Texto limpo: {len(text):,} caracteres")
    return text


def split_text_into_chunks(text: str, max_chars: int = CHUNK_SIZE) -> list:
    """Split text into chunks suitable for TTS, respecting sentence boundaries."""
    print(f"[3/5] Dividindo texto em blocos de ~{max_chars} caracteres...")

    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If single paragraph exceeds max_chars, split by sentences
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

    print(f"  {len(chunks)} blocos criados")
    return chunks


async def generate_audio_chunk(chunk: str, chunk_index: int, total_chunks: int,
                                temp_dir: Path, voice: str, rate: str) -> Path:
    """Generate audio for a single text chunk."""
    output_path = temp_dir / f"chunk_{chunk_index:04d}.mp3"

    communicate = edge_tts.Communicate(chunk, voice, rate=rate)
    await communicate.save(str(output_path))

    if (chunk_index + 1) % 10 == 0 or chunk_index == 0:
        print(f"  Bloco {chunk_index+1}/{total_chunks} gerado ({len(chunk):,} chars)")

    return output_path


async def generate_all_audio(chunks: list, temp_dir: Path, voice: str, rate: str) -> list:
    """Generate audio for all chunks sequentially."""
    print(f"[4/5] Gerando audio para {len(chunks)} blocos (voz: {voice})...")
    audio_files = []

    for i, chunk in enumerate(chunks):
        audio_file = await generate_audio_chunk(chunk, i, len(chunks), temp_dir, voice, rate)
        audio_files.append(audio_file)

    print(f"  Todos os {len(audio_files)} blocos gerados")
    return audio_files


def concatenate_mp3_files(audio_files: list, output_path: Path) -> Path:
    """Concatenate MP3 files by binary append (works for MP3 format)."""
    print(f"[5/5] Combinando {len(audio_files)} arquivos MP3...")

    with open(output_path, 'wb') as outfile:
        for audio_file in audio_files:
            with open(audio_file, 'rb') as infile:
                outfile.write(infile.read())

    file_size = output_path.stat().st_size
    print(f"  Arquivo final: {output_path}")
    print(f"  Tamanho: {file_size / (1024*1024):.1f} MB")
    return output_path


async def main():
    """Main pipeline."""
    print("=" * 60)
    print("  DISSERTACAO -> AUDIO MP3")
    print("  Voz: pt-BR-FranciscaNeural (Microsoft Edge TTS)")
    print("=" * 60)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Create temp directory for chunks
    temp_dir = Path(tempfile.mkdtemp(prefix="dissertacao_audio_"))

    try:
        # Step 1: Extract text
        raw_text = extract_text_from_pdf(PDF_PATH)

        # Step 2: Clean text
        clean_text = clean_text_for_tts(raw_text)

        # Save cleaned text for reference
        text_file = OUTPUT_DIR / "dissertacao_texto_limpo.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        print(f"  Texto limpo salvo em: {text_file}")

        # Step 3: Split into chunks
        chunks = split_text_into_chunks(clean_text)

        # Step 4: Generate audio
        audio_files = await generate_all_audio(chunks, temp_dir, VOICE, RATE)

        # Step 5: Concatenate
        final_file = concatenate_mp3_files(audio_files, OUTPUT_DIR / "dissertacao_completa.mp3")

        # Calculate duration estimate
        total_chars = sum(len(c) for c in chunks)
        estimated_minutes = total_chars / 15  # ~15 chars per second for Portuguese

        print()
        print("=" * 60)
        print("  CONCLUIDO!")
        print(f"  Arquivo: {final_file}")
        print(f"  Duracao estimada: {estimated_minutes:.0f} min ({estimated_minutes/60:.1f} h)")
        print("=" * 60)

    finally:
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
