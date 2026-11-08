"""Gera o audiolivro piloto da edição de curso (12 capítulos + abertura).

Voz sintética pt-BR Francisca, sem clonagem. O áudio é uma seleção de leitura,
não a narração integral das 600 laudas. O texto completo permanece no PDF/EPUB.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import edge_tts
from bs4 import BeautifulSoup

RAIZ = Path(__file__).resolve().parents[2]
LIVRO = RAIZ / "educacao_quantica_bohm" / "livro_pixel"
SECOES = LIVRO / "secoes"
OUT = LIVRO / "AUDIOLIVRO_CURSO"
VOICE = "pt-BR-FranciscaNeural"
TITULO = "Do Bit ao Todo — Audiolivro do Curso"

CAPITULOS = [
    ("Diferença e medida", "Do bit à medida: contar, tabular e comparar.", 1),
    ("Amplitude e probabilidade", "A conta que sustenta a previsão.", 3),
    ("Fase e interferência", "O sinal que muda o resultado.", 7),
    ("Emaranhamento e Bell", "Correlação que não é cópia.", 9),
    ("Portas e circuitos", "A receita do estado.", 21),
    ("GHZ e QASM", "Escala e linguagem.", 27),
    ("Ferramentas", "Python, Qiskit, PennyLane e GJQ.", 31),
    ("Bloch e amostragem", "Visualizar e estimar.", 38),
    ("Hardware e ruído", "O que o chip acrescenta.", 41),
    ("VQC e acurácia", "Aprender com poucos pontos.", 52),
    ("Ética e sociedade", "Quem ganha, quem perde.", 83),
    ("Projeto final", "Pergunta, evidência e limite.", 91),
]


def _slug(texto: str) -> str:
    """Converte o título em nome ASCII estável para o arquivo de áudio."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return "".join(c if c.isalnum() else "_" for c in texto.lower()).strip("_")


def _lauda_texto(codigo: int) -> str:
    caminho = next(SECOES.glob(f"{codigo:04d}_*.md"))
    soup = BeautifulSoup(caminho.read_text(encoding="utf-8"), "html.parser")
    for seletor in (
        ".ponte", ".resultado", ".mini-barras", ".topo", ".xp", ".rodape",
        ".fn", ".prof", ".rotulo", ".rotulo-mini", "script", "style",
        "pre", "table", "figure", "img",
    ):
        for tag in soup.select(seletor):
            tag.decompose()
    texto = soup.get_text("\n")
    texto = re.sub(r"LEIA EM 3 PASSOS|RIGOR CIENTÍFICO|CHECKPOINT", "", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def _capitulo_texto(indice: int, titulo: str, descricao: str, conceito: int) -> str:
    base = (conceito - 1) * 10 + 1
    ideia = _lauda_texto(base)
    pratica = _lauda_texto(base + 2)
    return (
        f"Capítulo {indice}. {titulo}. {descricao}\n\n"
        f"{ideia}\n\n{pratica}\n\nFim do capítulo {indice}."
    )


async def _gerar(texto: str, destino: Path) -> None:
    for tentativa in range(3):
        try:
            await edge_tts.Communicate(texto, VOICE, rate="+0%", volume="+0%").save(str(destino))
            if destino.is_file() and destino.stat().st_size > 1000:
                return
        except Exception:
            if tentativa == 2:
                raise
            await asyncio.sleep(3)
    raise RuntimeError(f"áudio vazio: {destino}")


def _duracao(caminho: Path) -> float:
    saida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(caminho)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(saida)


def _fmt(segundos: float) -> str:
    total = int(round(segundos))
    return f"{total // 60:02d}:{total % 60:02d}"


async def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    abertura = (
        f"{TITULO}. Marcelo Claro Laranjeira. "
        "Esta é uma seleção de doze módulos da edição de curso. "
        "A narração usa voz sintética em português do Brasil, sem clonagem de voz humana. "
        "O texto completo, as figuras e as referências estão no PDF e no EPUB. "
        "Cada capítulo apresenta uma ideia, uma prática e um limite."
    )
    arquivos = [("00_abertura.mp3", "Abertura", abertura, [])]
    for indice, (titulo, descricao, conceito) in enumerate(CAPITULOS, 1):
        base = (conceito - 1) * 10 + 1
        nome = f"{indice:02d}_{_slug(titulo)}.mp3"
        texto = _capitulo_texto(indice, titulo, descricao, conceito)
        arquivos.append((nome, titulo, texto, [f"L{base:04d}", f"L{base+2:04d}"]))

    manifest = {
        "title": TITULO,
        "author": "Marcelo Claro Laranjeira",
        "voice": VOICE,
        "synthetic_voice": True,
        "voice_cloning": False,
        "language": "pt-BR",
        "source": "EDICAO_CURSO_600.pdf",
        "source_commit": "cc30a434",
        "generated_at": "2026-11-08",
        "chapters": [],
        "total_seconds": 0.0,
        "license_text": "CC BY-NC-SA 4.0",
        "license_code": "MIT",
        "note": "Seleção de 12 módulos; não é a narração integral das 600 laudas.",
    }
    duracoes = []
    for nome, titulo, texto, laudas in arquivos:
        destino = OUT / nome
        print("gerando", nome, flush=True)
        await _gerar(texto, destino)
        duracao = _duracao(destino)
        duracoes.append(duracao)
        manifest["chapters"].append({
            "file": nome,
            "title": titulo,
            "duration_seconds": round(duracao, 2),
            "duration": _fmt(duracao),
            "source_laudas": laudas,
            "sha256": hashlib.sha256(destino.read_bytes()).hexdigest(),
        })
    manifest["total_seconds"] = round(sum(duracoes), 2)
    manifest["total_duration"] = _fmt(sum(duracoes))

    lista = OUT / "lista.txt"
    lista.write_text(
        "\n".join(f"file '{nome}'" for nome, *_ in arquivos) + "\n",
        encoding="utf-8",
    )
    completo = OUT / "AUDIOLIVRO_CURSO.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
         "-c:a", "libmp3lame", "-b:a", "96k",
         "-metadata", f"title={TITULO}", "-metadata", "artist=Marcelo Claro Laranjeira",
         "-metadata", "album=Do Bit ao Todo", str(completo)],
        check=True, capture_output=True,
    )
    manifest["full_file"] = completo.name
    manifest["full_sha256"] = hashlib.sha256(completo.read_bytes()).hexdigest()
    manifest["full_bytes"] = completo.stat().st_size
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    guia = ["# Guia do audiolivro", "", f"Voz sintética: `{VOICE}` · sem clonagem.", "",
            "| Faixa | Título | Duração |", "|---:|---|---:|"]
    for cap in manifest["chapters"]:
        guia.append(f"| {cap['file'][:2]} | {cap['title']} | {cap['duration']} |")
    guia += ["", f"**Total:** {manifest['total_duration']}.", "",
             "O áudio é uma seleção de 12 módulos, não a narração integral das 600 laudas.", ""]
    (OUT / "GUIA.md").write_text("\n".join(guia), encoding="utf-8")

    (OUT / "README.md").write_text(
        "# Audiolivro do Curso\n\n"
        f"Voz sintética `{VOICE}` (Edge TTS), sem clonagem. "
        f"Total: {manifest['total_duration']} em 12 capítulos + abertura.\n\n"
        "Arquivos: `00_abertura.mp3`, `01_...mp3` a `12_...mp3`, "
        "`AUDIOLIVRO_CURSO.mp3` (concatenação) e `manifest.json`.\n\n"
        "Esta é uma seleção de leitura da edição de curso. O texto completo, "
        "as figuras e as referências estão em `EDICAO_CURSO_600.pdf` e `.epub`.\n\n"
        "A voz é sintética e não representa uma pessoa real. Verifique os termos "
        "do serviço de voz antes de redistribuir o áudio em outro contexto.\n",
        encoding="utf-8",
    )
    print(json.dumps({"total": manifest["total_duration"], "bytes": manifest["full_bytes"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
