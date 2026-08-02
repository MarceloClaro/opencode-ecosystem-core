#!/usr/bin/env python3
"""
Pipeline de imagens sépia para o Molambudos — O Diário do Paciente 1.260.

Uso:
  python3 scripts/literary_sepia_pipeline.py --detect --corpus projetos/molambudos/original/html_livro.html
  python3 scripts/literary_sepia_pipeline.py --text "Foto antiga de menino" --output /tmp/foto.png
  python3 scripts/literary_sepia_pipeline.py --generate "descrição" --output /tmp/gerada.png

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import argparse
import io
import math
import os
import random
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Dependências opcionais ──
try:
    from PIL import Image, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Constantes ──
ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "projetos" / "molambudos" / "figures"
HTML_CORPUS = ROOT / "projetos" / "molambudos" / "original" / "html_livro.html"

# Palavras-chave para detectar menções a fotografias
PHOTO_KEYWORDS = [
    "fotograf", "foto", "fotografia", "fotográfic", "imagem",
    "retrato", "polaroid", "instantâneo", "kodak", "câmera",
    "camera", "selfie", "autorretrato", "chapas", "negativo",
    "album", "álbum",
]


# ═══════════════════════════════════════════════════════════════════════════
# 1. DETECÇÃO DE MENÇÕES A FOTOGRAFIAS
# ═══════════════════════════════════════════════════════════════════════════

def detect_photo_references(text: str) -> List[Dict[str, Any]]:
    """Encontra menções a fotografias no texto.

    Args:
        text: Texto completo do corpus (HTML, LaTeX ou markdown)

    Returns:
        Lista de dicts com 'linha', 'contexto' (trecho ao redor), 'tipo'
    """
    references: List[Dict[str, Any]] = []
    seen_contexts: set = set()

    lines = text.split("\n")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for keyword in PHOTO_KEYWORDS:
            if keyword in line_lower:
                # Extrai contexto: linha atual +-2 linhas
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end]).strip()

                # Deduplica por contexto similar
                context_key = context[:100]
                if context_key not in seen_contexts:
                    seen_contexts.add(context_key)
                    # Determina tipo
                    tipo = _classify_photo_reference(line_lower)
                    references.append({
                        "linha": i + 1,
                        "contexto": context[:300],
                        "tipo": tipo,
                        "keyword": keyword,
                    })
                break  # só a primeira keyword por linha

    return references


def _classify_photo_reference(line: str) -> str:
    """Classifica o tipo de referência fotográfica."""
    if any(w in line for w in ["antiga", "amarelada", "191", "192", "século"]):
        return "fotografia_historica"
    elif any(w in line for w in ["câmera", "camera", "segurança", "filmagem"]):
        return "camera_seguranca"
    elif any(w in line for w in ["polaroid", "instantâneo", "selfie"]):
        return "fotografia_moderna"
    elif any(w in line for w in ["retrato", "autorretrato"]):
        return "retrato"
    else:
        return "fotografia"


# ═══════════════════════════════════════════════════════════════════════════
# 2. BUSCA DE IMAGEM
# ═══════════════════════════════════════════════════════════════════════════

def fetch_image(url: str, timeout: int = 15) -> Optional[Any]:
    """Baixa uma imagem de URL.

    Args:
        url: URL da imagem
        timeout: Timeout em segundos

    Returns:
        PIL.Image ou None se falhar
    """
    if not HAS_PIL:
        return None

    try:
        if HAS_REQUESTS:
            resp = requests.get(url, timeout=timeout, headers={
                "User-Agent": "Mozilla/5.0 (OpenCode-Ecosystem/1.0)"
            })
            resp.raise_for_status()
            img_data = resp.content
        else:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0"
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                img_data = resp.read()

        img = Image.open(io.BytesIO(img_data))
        return img.convert("RGB") if img.mode != "RGB" else img
    except Exception:
        return None


def generate_image(description: str) -> Optional[Any]:
    """Gera uma imagem synthetic via Antigravity.

    Nota: Esta função delega ao Antigravity via MCP.
    O resultado é recebido assincronamente. Se não houver retorno,
    retorna uma imagem sintética de placeholder.

    Args:
        description: Descrição textual da imagem

    Returns:
        PIL.Image ou None
    """
    # Tenta delegar ao Antigravity...
    # (implementação real usaria o MCP antigravity-bridge)
    # Por ora, retorna placeholder sintético
    return generate_placeholder(description)


def generate_placeholder(description: str, size: Tuple[int, int] = (800, 600)) -> Any:
    """Gera uma imagem sintética como placeholder.

    Cria uma imagem simples com fundo texturizado e texto descritivo
    para servir como fallback quando não há imagem real disponível.

    Args:
        description: Descrição textual (usada no texto da imagem)
        size: Dimensões da imagem

    Returns:
        PIL.Image
    """
    if not HAS_PIL:
        return None

    img = Image.new("RGB", size, color=(200, 190, 180))
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)

    # Fundo com variação sutil
    for y in range(0, size[1], 20):
        for x in range(0, size[0], 20):
            c = 160 + (x * y) % 40
            draw.rectangle([x, y, x + 18, y + 18], fill=(c, c - 8, c - 15))

    # Texto central
    # (usando fonte padrão, sem depender de fontes externas)
    lines = description.split(". ")
    y_pos = size[1] // 2 - len(lines) * 15
    for line in lines:
        # Centraliza texto aproximado
        x_pos = size[0] // 2 - len(line) * 4
        draw.text((x_pos, y_pos), line[:60], fill=(80, 70, 60))
        y_pos += 30

    draw.text((size[0] // 2 - 100, size[1] - 40),
              "[placeholder — substituir por imagem real]",
              fill=(120, 110, 100))

    return img.convert("RGB")


# ═══════════════════════════════════════════════════════════════════════════
# 3. PIPELINE DE PROCESSAMENTO
# ═══════════════════════════════════════════════════════════════════════════

def apply_sepia(img: Any, intensity: float = 1.0) -> Any:
    """Aplica filtro sépia com intensidade controlada.

    Matriz 3×3 clássica (baseada em fotografia P&B):
      R_out = 0.393*R + 0.769*G + 0.189*B
      G_out = 0.349*R + 0.686*G + 0.168*B
      B_out = 0.272*R + 0.534*G + 0.131*B

    Args:
        img: PIL.Image em modo RGB
        intensity: 0.0 (sem efeito) a 1.0 (sépia máximo)

    Returns:
        PIL.Image em modo RGB
    """
    if not HAS_PIL:
        return img

    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]

            # Matriz sépia
            sr = 0.393 * r + 0.769 * g + 0.189 * b
            sg = 0.349 * r + 0.686 * g + 0.168 * b
            sb = 0.272 * r + 0.534 * g + 0.131 * b

            # Interpola entre original e sépia conforme intensity
            tr = int(r + (sr - r) * intensity)
            tg = int(g + (sg - g) * intensity)
            tb = int(b + (sb - b) * intensity)

            pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))

    return img


def apply_vignette(img: Any, strength: float = 0.4) -> Any:
    """Aplica vinheta radial (bordas escuras).

    Args:
        img: PIL.Image em modo RGB
        strength: 0.0 (sem vinheta) a 1.0 (vinheta máxima)

    Returns:
        PIL.Image em modo RGB
    """
    if not HAS_PIL:
        return img

    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    cx, cy = w / 2, h / 2
    max_dist = math.sqrt(cx**2 + cy**2)

    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            factor = 1.0 - strength * (dist / max_dist)
            factor = max(0.3, factor)
            r, g, b = pixels[x, y]
            pixels[x, y] = (
                int(r * factor),
                int(g * factor),
                int(b * factor),
            )

    return img


def apply_grain(img: Any, amount: float = 0.05) -> Any:
    """Adiciona grão/textura de papel envelhecido.

    Args:
        img: PIL.Image em modo RGB
        amount: 0.0 (sem grão) a 1.0 (grão máximo)

    Returns:
        PIL.Image em modo RGB
    """
    if not HAS_PIL:
        return img

    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    max_delta = int(amount * 60)

    random.seed(42)  # Determinístico para reprodutibilidade

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            delta = random.randint(-max_delta, max_delta)
            pixels[x, y] = (
                max(0, min(255, r + delta)),
                max(0, min(255, g + delta)),
                max(0, min(255, b + delta)),
            )

    return img


def full_pipeline(img: Any, sepia_intensity: float = 1.0,
                  vignette_strength: float = 0.4,
                  grain_amount: float = 0.05) -> Any:
    """Executa o pipeline completo de envelhecimento.

    1. Sépia → 2. Vinheta → 3. Grão

    Args:
        img: PIL.Image
        sepia_intensity: Intensidade do sépia
        vignette_strength: Força da vinheta
        grain_amount: Quantidade de grão

    Returns:
        PIL.Image processada
    """
    if not HAS_PIL:
        return img

    result = apply_sepia(img, intensity=sepia_intensity)
    result = apply_vignette(result, strength=vignette_strength)
    result = apply_grain(result, amount=grain_amount)
    return result


# ═══════════════════════════════════════════════════════════════════════════
# 4. INTEGRAÇÃO LaTeX
# ═══════════════════════════════════════════════════════════════════════════

def save_for_latex(img: Any, output_path: str,
                   caption: str = "",
                   width: str = "0.6\\textwidth") -> str:
    """Salva imagem e retorna código LaTeX.

    Args:
        img: PIL.Image
        output_path: Caminho para salvar
        caption: Legenda da figura (opcional)
        width: Largura LaTeX (ex: '0.6\\textwidth')

    Returns:
        Código LaTeX gerado
    """
    if not HAS_PIL:
        return "% PIL não disponível"

    # Garante que diretório existe
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Salva como PNG (qualidade máxima)
    img.save(output_path, "PNG")

    # Gera código LaTeX
    rel_path = os.path.relpath(output_path, ROOT)
    latex = []
    latex.append(r"\begin{figure}[htbp]")
    latex.append(r"  \centering")
    latex.append(rf"  \includegraphics[width={width}]{{{rel_path}}}")
    if caption:
        latex.append(rf"  \caption{{{caption}}}")
    latex.append(r"  \label{fig:" + os.path.splitext(os.path.basename(output_path))[0] + "}")
    latex.append(r"\end{figure}")

    return "\n".join(latex)


# ═══════════════════════════════════════════════════════════════════════════
# 5. CLI
# ═══════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        description="Pipeline de imagens sépia para o Molambudos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --detect --corpus projetos/molambudos/original/html_livro.html
  %(prog)s --text "Foto antiga de menino com número 1.260" --output /tmp/foto.png
  %(prog)s --generate "Paciente 1.260 no Colônia, 1917" --output /tmp/gerada.png
        """,
    )
    parser.add_argument(
        "--detect", action="store_true",
        help="Detecta menções a fotografias no corpus"
    )
    parser.add_argument(
        "--corpus", type=str, default=None,
        help="Caminho do corpus HTML/LaTeX para detectar fotos"
    )
    parser.add_argument(
        "--text", type=str, default=None,
        help="Descrição textual da foto para processar"
    )
    parser.add_argument(
        "--generate", type=str, default=None,
        help="Gera imagem a partir de descrição textual"
    )
    parser.add_argument(
        "--url", type=str, default=None,
        help="URL de imagem para baixar e processar"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Caminho de saída para a imagem processada"
    )
    parser.add_argument(
        "--sepia", type=float, default=1.0,
        help="Intensidade do sépia (0.0-1.0)"
    )
    parser.add_argument(
        "--vignette", type=float, default=0.4,
        help="Força da vinheta (0.0-1.0)"
    )
    parser.add_argument(
        "--grain", type=float, default=0.05,
        help="Quantidade de grão (0.0-1.0)"
    )
    parser.add_argument(
        "--caption", type=str, default="",
        help="Legenda para inclusão no LaTeX"
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Função principal da CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # ── Modo detect ──
    if args.detect:
        corpus_path = args.corpus or str(HTML_CORPUS)
        if not os.path.exists(corpus_path):
            print(f"Erro: corpus não encontrado: {corpus_path}", file=sys.stderr)
            return 1

        with open(corpus_path, encoding="utf-8") as f:
            text = f.read()

        refs = detect_photo_references(text)
        print(f"Menções a fotografias encontradas: {len(refs)}")
        for ref in refs:
            print(f"\n  Linha {ref['linha']} [{ref['tipo']}]:")
            print(f"  Contexto: {ref['contexto'][:150]}...")
        return 0

    # ── Modo generate ──
    if args.generate:
        if not args.output:
            print("Erro: --output é obrigatório com --generate", file=sys.stderr)
            return 1

        img = generate_image(args.generate)
        if img is None:
            img = generate_placeholder(args.generate)

        result = full_pipeline(
            img,
            sepia_intensity=args.sepia,
            vignette_strength=args.vignette,
            grain_amount=args.grain,
        )

        latex = save_for_latex(result, args.output, caption=args.caption)
        result.save(args.output, "PNG")
        print(f"Imagem gerada e processada: {args.output}")
        print(f"\nCódigo LaTeX:\n{latex}")
        return 0

    # ── Modo url ──
    if args.url:
        if not args.output:
            print("Erro: --output é obrigatório com --url", file=sys.stderr)
            return 1

        img = fetch_image(args.url)
        if img is None:
            print("Erro: não foi possível baixar a imagem", file=sys.stderr)
            return 1

        result = full_pipeline(
            img,
            sepia_intensity=args.sepia,
            vignette_strength=args.vignette,
            grain_amount=args.grain,
        )

        latex = save_for_latex(result, args.output, caption=args.caption)
        result.save(args.output, "PNG")
        print(f"Imagem processada e salva: {args.output}")
        print(f"\nCódigo LaTeX:\n{latex}")
        return 0

    # ── Modo text (descrição + placeholder) ──
    if args.text:
        if not args.output:
            print("Erro: --output é obrigatório com --text", file=sys.stderr)
            return 1

        img = generate_placeholder(args.text)
        result = full_pipeline(
            img,
            sepia_intensity=args.sepia,
            vignette_strength=args.vignette,
            grain_amount=args.grain,
        )

        latex = save_for_latex(result, args.output, caption=args.caption)
        print(f"Imagem placeholder processada: {args.output}")
        print(f"\nCódigo LaTeX:\n{latex}")
        return 0

    # ── Sem modo ──
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
