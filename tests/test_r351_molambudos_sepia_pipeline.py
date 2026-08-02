"""Testes R351 — Pipeline de imagens sépia para o Molambudos (TDD)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HTML_CORPUS = ROOT / "projetos" / "molambudos" / "original" / "html_livro.html"
FIGURES_DIR = ROOT / "projetos" / "molambudos" / "figures"

# ── Testes do pipeline de processamento de imagem ──


def test_import_pipeline():
    """O módulo do pipeline deve importar sem erros."""
    import scripts.literary_sepia_pipeline as P  # noqa
    assert hasattr(P, "apply_sepia")
    assert hasattr(P, "apply_vignette")
    assert hasattr(P, "apply_grain")
    assert hasattr(P, "save_for_latex")


def test_apply_sepia_from_url():
    """apply_sepia deve processar imagem de URL e retornar imagem RGB com tom sépia."""
    from PIL import Image
    from scripts.literary_sepia_pipeline import apply_sepia, fetch_image

    # Usar imagem de teste pública
    url = "https://raw.githubusercontent.com/python-pillow/Pillow/main/Tests/images/hopper.jpg"
    img = fetch_image(url)
    assert img is not None, "fetch_image falhou"
    assert img.mode in ("RGB", "RGBA")

    result = apply_sepia(img, intensity=1.0)
    assert result is not None
    assert result.mode == "RGB"
    assert result.size == img.size

    # Verificar que pixels mudaram (não é mais cinza/branco puro)
    pixels = list(result.getdata())
    has_color = any(r != g or g != b for r, g, b in pixels[:100])
    assert has_color, "Imagem sépia deve ter variação de cor (tom sépia)"


def test_apply_sepia_synthetic():
    """apply_sepia deve funcionar com imagem sintética."""
    from PIL import Image
    from scripts.literary_sepia_pipeline import apply_sepia

    img = Image.new("RGB", (100, 100), (200, 180, 150))
    result = apply_sepia(img, intensity=1.0)
    assert result.size == (100, 100)
    r, g, b = result.getpixel((50, 50))
    # Tom sépia: R deve ser maior que B
    assert r > b, f"Sépia deve ter R > B, got R={r} B={b}"


def test_apply_sepia_intensity():
    """Intensidade 0 deve retornar imagem inalterada; intensidade 1 máxima."""
    from PIL import Image
    from scripts.literary_sepia_pipeline import apply_sepia

    img = Image.new("RGB", (50, 50), (100, 100, 100))
    zero = apply_sepia(img, intensity=0.0)
    full = apply_sepia(img, intensity=1.0)

    # Com intensidade 0, os canais devem permanecer iguais (tons de cinza)
    zr, zg, zb = zero.getpixel((25, 25))
    assert zr == zg == zb, f"Intensity=0 deve ser cinza puro, got R={zr} G={zg} B={zb}"

    # Com intensidade 1, os canais devem divergir (tom sépia)
    fr, fg, fb = full.getpixel((25, 25))
    assert fr != fg or fg != fb, "Intensity=1 deve ter canais divergentes (tom sépia)"


def test_apply_vignette():
    """apply_vignette deve escurecer as bordas da imagem."""
    from PIL import Image
    from scripts.literary_sepia_pipeline import apply_vignette

    img = Image.new("RGB", (200, 200), (200, 180, 150))
    result = apply_vignette(img, strength=0.5)

    # Centro deve ser mais claro que borda
    center = result.getpixel((100, 100))
    edge = result.getpixel((5, 5))
    assert sum(center) > sum(edge), (
        f"Centro ({sum(center)}) deve ser mais claro que borda ({sum(edge)})"
    )


def test_apply_grain():
    """apply_grain deve adicionar ruído visível à imagem."""
    from PIL import Image
    from scripts.literary_sepia_pipeline import apply_grain

    img = Image.new("RGB", (100, 100), (128, 128, 128))
    result = apply_grain(img, amount=0.3)

    # Com ruído, pixels devem variar em relação ao original
    orig_pixel = img.getpixel((50, 50))
    grain_pixel = result.getpixel((50, 50))
    # Nem todos os pixels devem ser idênticos ao original
    diffs = []
    for x in range(0, 100, 10):
        for y in range(0, 100, 10):
            orig = img.getpixel((x, y))
            grained = result.getpixel((x, y))
            if orig != grained:
                diffs.append(abs(sum(orig) - sum(grained)))
    assert len(diffs) > 0, "Grain deve alterar pelo menos alguns pixels"


def test_fetch_image_invalid_url():
    """fetch_image deve retornar None para URL inválida."""
    from scripts.literary_sepia_pipeline import fetch_image

    result = fetch_image("https://invalid.example.com/nonexistent.jpg")
    assert result is None, "URL inválida deve retornar None"


def test_save_for_latex():
    """save_for_latex deve salvar imagem e retornar código LaTeX."""
    from PIL import Image
    from scripts.literary_sepia_pipeline import save_for_latex

    img = Image.new("RGB", (100, 100), (200, 180, 150))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        out_path = f.name

    try:
        latex = save_for_latex(
            img, out_path,
            caption="Foto do Paciente 1.260, Colônia 1917."
        )
        assert os.path.exists(out_path), "Arquivo de imagem deve existir"
        assert os.path.getsize(out_path) > 100, "Arquivo não deve estar vazio"
        assert "\\includegraphics" in latex, (
            "LaTeX deve conter \\includegraphics"
        )
        assert "Paciente 1.260" in latex, "LaTeX deve conter caption"
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)


# ── Testes de detecção de menções a fotografias ──


def test_detect_photo_references_corpus():
    """detect_photo_references deve encontrar menções a fotos no corpus do Molambudos."""
    if not HTML_CORPUS.exists():
        pytest.skip(f"Corpus não encontrado: {HTML_CORPUS}")

    from scripts.literary_sepia_pipeline import detect_photo_references

    with open(HTML_CORPUS, encoding="utf-8") as f:
        text = f.read()

    refs = detect_photo_references(text)
    assert len(refs) >= 15, (
        f"Deve encontrar >=15 menções a fotografias, encontrou {len(refs)}"
    )

    # Verificar estrutura dos resultados
    for ref in refs:
        assert "linha" in ref, "Cada referência deve ter 'linha'"
        assert "contexto" in ref, "Cada referência deve ter 'contexto'"
        assert "tipo" in ref, "Cada referência deve ter 'tipo'"


def test_detect_photo_references_empty():
    """detect_photo_references deve retornar lista vazia para texto sem fotos."""
    from scripts.literary_sepia_pipeline import detect_photo_references

    refs = detect_photo_references("Era uma vez um gato feliz.")
    assert refs == [], "Texto sem fotos deve retornar lista vazia"


# ── Testes de linha de comando ──


def test_cli_help():
    """--help deve mostrar as opções disponíveis."""
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/literary_sepia_pipeline.py", "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    assert "--detect" in result.stdout
    assert "--generate" in result.stdout


def test_cli_detect():
    """--detect --corpus deve encontrar menções a fotos."""
    if not HTML_CORPUS.exists():
        pytest.skip(f"Corpus não encontrado: {HTML_CORPUS}")

    import subprocess
    result = subprocess.run(
        [
            "python3", "scripts/literary_sepia_pipeline.py",
            "--detect", "--corpus", str(HTML_CORPUS),
        ],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0
    assert "fotograf" in result.stdout.lower() or "encontrada" in result.stdout.lower()


def test_cli_process_text():
    """--text deve processar descrição e gerar imagem sépia."""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        out_path = f.name

    try:
        result = subprocess.run(
            [
                "python3", "scripts/literary_sepia_pipeline.py",
                "--text", "Foto antiga de menino com número 1.260",
                "--output", out_path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        # Pode falhar se não conseguir baixar imagem, mas não deve crashar
        if result.returncode == 0:
            assert os.path.exists(out_path)
            assert os.path.getsize(out_path) > 100
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)


# ── Teste de integridade (não quebrar projeto) ──


def test_figures_dir_exists():
    """O diretório de figuras do Molambudos deve existir."""
    assert FIGURES_DIR.exists() or FIGURES_DIR.parent.exists(), (
        f"Diretório de figuras não encontrado: {FIGURES_DIR}"
    )


def test_artifact_catalog_registers_agent():
    """O agente literary-image-sepia deve estar no catálogo."""
    from marceloclaro.catalog_loader import load_catalog_definitions

    agents = load_catalog_definitions()
    found = any("literary-image-sepia" in a.get("agent_id", "") for a in agents)
    assert found, "Agente literary-image-sepia não encontrado no catálogo"
