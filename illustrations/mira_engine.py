"""
MIRA Engine — Metáforas Inteligentes Responsivas e Animadas.
============================================================

Inspirado no sandeco/mira-animator e no livro MIRA. Gera cards HTML
animados (SVG + CSS keyframes) que reexpressam conceitos científicos
como metáforas visuais concretas do cotidiano.

Regras portadas do mira-animator:
- Regra Zero (loop interno obrigatório): nenhuma animação é estática;
  entra com coreografia e segue em movimento perpétuo (CSS infinite).
- Canvas padrão: viewBox="0 0 1280 720", palco `.anim-stage`.
- Título sem ícone, com no máximo 6 palavras.
- Método da metáfora: destilar a dinâmica -> achar sistema do cotidiano
  com a MESMA dinâmica -> mapear 1-para-1 -> garantir loop -> obviedade.

O catálogo de metáforas mapeia dinâmicas conceituais para cenas animadas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

MAX_TITLE_WORDS = 6


def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")[:60] or "card"


# ----------------------------------------------------------------------
# Catálogo de metáforas (dinâmica -> cena SVG animada)
# ----------------------------------------------------------------------
@dataclass
class Metaphor:
    key: str
    dynamic: str          # a dinâmica que ela preserva (a "alma" do conceito)
    scene: str            # descrição da cena
    loop: str             # o loop perpétuo, em uma frase
    svg: str              # a cena SVG animada (CSS keyframes infinite)


def _svg_pipeline() -> str:
    return """
<svg viewBox="0 0 1280 720" class="anim-stage" xmlns="http://www.w3.org/2000/svg">
  <rect x="140" y="330" width="1000" height="26" rx="13" fill="#30363d"/>
  <g class="belt-item" style="animation-delay:0s"><circle r="26" fill="#58a6ff"/></g>
  <g class="belt-item" style="animation-delay:2s"><circle r="26" fill="#3fb950"/></g>
  <g class="belt-item" style="animation-delay:4s"><circle r="26" fill="#d29922"/></g>
  <g class="station" transform="translate(400,300)"><rect x="-34" y="-58" width="68" height="58" rx="8" fill="#8957e5"/></g>
  <g class="station" transform="translate(700,300)"><rect x="-34" y="-58" width="68" height="58" rx="8" fill="#f778ba"/></g>
  <g class="station" transform="translate(1000,300)"><rect x="-34" y="-58" width="68" height="58" rx="8" fill="#58a6ff"/></g>
  <style>
    .belt-item { animation: belt 6s linear infinite; }
    @keyframes belt {
      0%   { transform: translate(160px, 343px) scale(0.7); opacity: 0; }
      10%  { opacity: 1; }
      45%  { transform: translate(640px, 343px) scale(1); }
      90%  { opacity: 1; }
      100% { transform: translate(1120px, 343px) scale(1.2); opacity: 0; }
    }
    .station rect { animation: pulse 2s ease-in-out infinite; transform-origin: center bottom; }
    @keyframes pulse { 0%,100% { transform: scaleY(1);} 50% { transform: scaleY(1.12);} }
  </style>
</svg>"""


def _svg_orchestra() -> str:
    return """
<svg viewBox="0 0 1280 720" class="anim-stage" xmlns="http://www.w3.org/2000/svg">
  <g transform="translate(640,250)">
    <circle r="42" fill="#e6edf3"/>
    <rect class="baton" x="-4" y="-110" width="8" height="70" rx="4" fill="#d29922"/>
  </g>
  <g class="naipe" transform="translate(300,520)"><circle r="34" fill="#58a6ff"/></g>
  <g class="naipe" transform="translate(530,560)" style="animation-delay:.25s"><circle r="34" fill="#3fb950"/></g>
  <g class="naipe" transform="translate(760,560)" style="animation-delay:.5s"><circle r="34" fill="#f778ba"/></g>
  <g class="naipe" transform="translate(990,520)" style="animation-delay:.75s"><circle r="34" fill="#8957e5"/></g>
  <style>
    .baton { animation: conduct 2s ease-in-out infinite; transform-origin: 0 0; }
    @keyframes conduct { 0%,100% { transform: rotate(-30deg);} 50% { transform: rotate(30deg);} }
    .naipe { animation: play 2s ease-in-out infinite; }
    @keyframes play { 0%,100% { transform: translate(var(--tx,0),0) scale(1);} 50% { transform: scale(1.25);} }
  </style>
</svg>"""


def _svg_desk() -> str:
    return """
<svg viewBox="0 0 1280 720" class="anim-stage" xmlns="http://www.w3.org/2000/svg">
  <rect x="240" y="480" width="800" height="30" rx="8" fill="#30363d"/>
  <g class="paper p1"><rect width="150" height="100" rx="6" fill="#58a6ff"/></g>
  <g class="paper p2"><rect width="150" height="100" rx="6" fill="#3fb950"/></g>
  <g class="paper p3"><rect width="150" height="100" rx="6" fill="#d29922"/></g>
  <style>
    .paper { animation: slidein 6s linear infinite; }
    .p2 { animation-delay: 2s; } .p3 { animation-delay: 4s; }
    @keyframes slidein {
      0%   { transform: translate(1160px, 370px); opacity: 0; }
      15%  { transform: translate(880px, 370px); opacity: 1; }
      60%  { transform: translate(520px, 370px); opacity: 1; }
      85%  { transform: translate(240px, 370px); opacity: .6; }
      100% { transform: translate(120px, 370px); opacity: 0; }
    }
  </style>
</svg>"""


def _svg_tower() -> str:
    return """
<svg viewBox="0 0 1280 720" class="anim-stage" xmlns="http://www.w3.org/2000/svg">
  <rect x="500" y="600" width="280" height="24" rx="6" fill="#30363d"/>
  <g class="blk b1"><rect x="540" y="520" width="200" height="70" rx="8" fill="#58a6ff"/></g>
  <g class="blk b2"><rect x="550" y="440" width="180" height="70" rx="8" fill="#d29922"/></g>
  <g class="blk b3"><rect x="560" y="360" width="160" height="70" rx="8" fill="#f85149"/></g>
  <style>
    .blk { animation: grow 6s ease-in-out infinite; opacity: 0; transform-origin: 640px 600px; }
    .b1 { animation-delay: 0s; } .b2 { animation-delay: 1.5s; } .b3 { animation-delay: 3s; }
    @keyframes grow {
      0% { opacity: 0; transform: translateY(-60px);}
      15% { opacity: 1; transform: translateY(0);}
      70% { opacity: 1; transform: translateY(0) rotate(1.5deg);}
      90% { opacity: 0; transform: translateY(30px);}
      100% { opacity: 0; }
    }
  </style>
</svg>"""


CATALOG: List[Metaphor] = [
    Metaphor("pipeline", "fluxo sequencial com estações que transformam",
             "esteira de linha de montagem", 
             "uma peça crua entra numa ponta, passa pelas estações e sai montada na outra, repetindo",
             _svg_pipeline()),
    Metaphor("orquestracao", "coordenação central que sincroniza executores heterogêneos",
             "maestro regendo os naipes da orquestra",
             "a batuta marca o tempo no centro e as seções pulsam em uníssono a cada compasso",
             _svg_orchestra()),
    Metaphor("contexto", "capacidade finita onde o novo empurra o antigo para fora",
             "mesa de trabalho lotada",
             "um papel novo entra de um lado e empurra o mais antigo para fora do outro, sem parar",
             _svg_desk()),
    Metaphor("debito", "custo que cresce sozinho com o tempo se não for pago",
             "torre de juros compostos",
             "a cada ciclo a torre ganha um bloco sozinha e inclina mais, até ruir e recomeçar",
             _svg_tower()),
]

KEYWORD_MAP = {
    "pipeline": "pipeline", "fluxo": "pipeline", "etapas": "pipeline", "workflow": "pipeline",
    "orquestra": "orquestracao", "orquestr": "orquestracao", "coorden": "orquestracao",
    "agentes": "orquestracao", "multiagente": "orquestracao",
    "contexto": "contexto", "memoria": "contexto", "janela": "contexto", "cache": "contexto",
    "debito": "debito", "divida": "debito", "custo": "debito", "juros": "debito",
}


@dataclass
class MiraCard:
    """Um card MIRA: conceito + metáfora + animação em loop perpétuo."""
    title: str
    subtitle: str
    metaphor: Metaphor
    html_path: Optional[str] = None

    @property
    def slug(self) -> str:
        return _slugify(self.title)


class MiraEngine:
    """Gera cards HTML animados com metáforas visuais (Regra Zero: loop perpétuo)."""

    def __init__(self, output_dir: str = "ilustracoes/mira", theme: str = "dark"):
        self.output_dir = Path(output_dir)
        self.theme = theme

    # ------------------------------------------------------------------
    def pick_metaphor(self, concept_text: str) -> Metaphor:
        """Escolhe a metáfora cuja dinâmica melhor preserva a 'alma' do conceito."""
        low = concept_text.lower()
        scores: Dict[str, int] = {}
        for kw, key in KEYWORD_MAP.items():
            if kw in low:
                scores[key] = scores.get(key, 0) + 1
        if scores:
            best = max(scores, key=scores.get)
            return next(m for m in CATALOG if m.key == best)
        return CATALOG[0]  # pipeline é a metáfora default para processos

    def _clip_title(self, title: str) -> str:
        words = title.split()
        return " ".join(words[:MAX_TITLE_WORDS])

    # ------------------------------------------------------------------
    def card(self, title: str, concept_text: str, subtitle: str = "") -> MiraCard:
        """Cria um card animado para o conceito (sem renderizar ainda)."""
        met = self.pick_metaphor(f"{title} {concept_text}")
        return MiraCard(title=self._clip_title(title),
                        subtitle=subtitle or met.loop.capitalize(),
                        metaphor=met)

    def render(self, card: MiraCard) -> MiraCard:
        """Renderiza o card em HTML self-contained com loop CSS infinito."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        bg, fg, muted = ("#0d1117", "#e6edf3", "#8b949e") if self.theme == "dark" else ("#ffffff", "#111", "#555")
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{card.title} — MIRA Card</title>
<style>
  body {{ margin:0; background:{bg}; color:{fg}; font-family: system-ui, sans-serif;
         display:flex; align-items:center; justify-content:center; min-height:100vh; }}
  .card {{ width: 960px; max-width: 94vw; background: rgba(255,255,255,0.04);
          border: 1px solid #30363d; border-radius: 18px; padding: 28px 34px;
          backdrop-filter: blur(6px); }}
  h1 {{ margin: 0 0 6px; font-size: 34px; }}
  p.sub {{ margin: 0 0 18px; color: {muted}; font-size: 17px; }}
  .anim-stage {{ width: 100%; height: auto; border-radius: 12px; background: rgba(0,0,0,0.25); }}
  footer {{ margin-top: 12px; color: {muted}; font-size: 13px; }}
  button {{ background:#21262d; color:{fg}; border:1px solid #30363d; border-radius:8px;
           padding:6px 14px; cursor:pointer; }}
</style>
</head>
<body>
<div class="card">
  <h1>{card.title}</h1>
  <p class="sub">{card.subtitle}</p>
  {card.metaphor.svg}
  <footer>
    Metáfora: <strong>{card.metaphor.scene}</strong> · Loop: {card.metaphor.loop}
    <button onclick="document.querySelectorAll('.anim-stage').forEach(s=>{{const c=s.cloneNode(true);s.replaceWith(c);}})">Replay</button>
  </footer>
</div>
</body>
</html>
"""
        path = self.output_dir / f"{card.slug}.html"
        path.write_text(html, encoding="utf-8")
        card.html_path = str(path)
        return card

    def illustrate_sections(self, sections: Dict[str, str]) -> List[MiraCard]:
        """Gera um card por seção do manuscrito {título: texto}."""
        cards = []
        for title, text in sections.items():
            cards.append(self.render(self.card(title, text)))
        return cards
