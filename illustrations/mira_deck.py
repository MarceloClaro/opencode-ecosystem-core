"""
MIRA Deck Pipeline — a linha de montagem de apresentações do método MIRA.
========================================================================

Coração do método MIRA (livro "MIRA" + sandeco/mira-animator): transforma
um manuscrito científico (`manuscrito.md`) num deck HTML navegável de cards
de vidro animados. A esteira tem 6 postos com fronteiras limpas — cada um
é chamável isoladamente (consertar a peça, não a fábrica):

    extract → plan → copywrite → build → animate → validate

Regras portadas (SPEC-935-R123):
  1. Regra Zero: nenhum card é estático — entra com coreografia e segue em
     loop perpétuo (CSS `infinite`). Slide parado é defeito, não estilo.
  2. Título ≤ 6 palavras, sem ícone.
  3. Metáfora que preserva a estrutura ("alma") do conceito — cards de
     conceito reutilizam o catálogo do `MiraEngine`.
  4. Montagem atômica: cards de vidro translúcido (backdrop-filter/blur),
     consistentes por construção.
  5. Formato do card acompanha o formato da ideia (quote/code/grid/concept).
  6. Navegação card-a-card (teclado + botões).
  7. A esteira para nas juntas: API pública por estágio.
  8. Inspetor final: `validate` emite relatório de conformidade.
"""

from __future__ import annotations

import html as _html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .mira_engine import CATALOG, MAX_TITLE_WORDS, MiraEngine, Metaphor

_METAPHOR_MARK = "<!--MIRA-METAPHOR:{key}-->"


# ----------------------------------------------------------------------
# Estruturas de dados (entrada/saída de cada posto da esteira)
# ----------------------------------------------------------------------
@dataclass
class Section:
    """Uma seção `##` do manuscrito, com seus marcadores detectados."""
    title: str
    body: str
    key_points: List[str] = field(default_factory=list)
    quote: Optional[str] = None
    code: Optional[str] = None
    code_lang: Optional[str] = None


@dataclass
class Briefing:
    """Saída do estágio extract: título do documento + suas seções."""
    title: str
    sections: List[Section] = field(default_factory=list)


@dataclass
class SlideSpec:
    """Especificação de um slide (uma ideia por tela)."""
    kind: str                       # cover | concept | quote | code | grid | closing
    title: str
    subtitle: str = ""
    body: str = ""
    items: List[str] = field(default_factory=list)
    quote: Optional[str] = None
    code: Optional[str] = None
    code_lang: Optional[str] = None
    metaphor_key: Optional[str] = None


@dataclass
class SlidePlan:
    """Saída dos estágios plan/copywrite: a sequência de slides planejada."""
    title: str
    slides: List[SlideSpec] = field(default_factory=list)


@dataclass
class Deck:
    """Saída dos estágios build/animate: os slides + o HTML montado."""
    title: str
    slides: List[SlideSpec] = field(default_factory=list)
    html: str = ""


@dataclass
class ConformityReport:
    """Relatório do inspetor final (validate)."""
    passed: bool
    checks: List[tuple] = field(default_factory=list)     # (nome, ok, detalhe)
    violations: List[str] = field(default_factory=list)

    def to_markdown(self, deck_title: str = "") -> str:
        status = "✅ CONFORME" if self.passed else "❌ NÃO CONFORME"
        lines = [
            f"# Relatório de Conformidade MIRA — {deck_title}".rstrip(" —"),
            "",
            f"**Resultado: {status}**",
            "",
            "Inspetor final do método MIRA (Regra Zero, títulos, navegação,",
            "integridade de recursos). Consertar a peça, não a fábrica.",
            "",
            "## Verificações",
            "",
        ]
        for nome, ok, detalhe in self.checks:
            mark = "✅" if ok else "❌"
            lines.append(f"- {mark} **{nome}** — {detalhe}")
        if self.violations:
            lines += ["", "## Violações", ""]
            lines += [f"- ⚠️ {v}" for v in self.violations]
        lines.append("")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# A esteira
# ----------------------------------------------------------------------
class MiraDeckPipeline:
    """Linha de montagem MIRA: manuscrito → deck HTML animado + conformidade."""

    def __init__(self, theme: str = "dark"):
        self.theme = theme
        self._mira = MiraEngine(theme=theme)

    # ---------- Posto 1: extract -------------------------------------
    def extract(self, markdown: str) -> Briefing:
        """Lê o manuscrito e produz um briefing (seções + marcadores)."""
        lines = markdown.splitlines()
        doc_title = ""
        for ln in lines:
            m = re.match(r"^#\s+(.*)", ln)
            if m:
                doc_title = m.group(1).strip()
                break

        sections: List[Section] = []
        cur_title: Optional[str] = None
        buf: List[str] = []

        def flush():
            if cur_title is None:
                return
            sections.append(self._section_from_block(cur_title, "\n".join(buf)))

        for ln in lines:
            h2 = re.match(r"^##\s+(.*)", ln)
            if h2:
                flush()
                cur_title = h2.group(1).strip()
                buf = []
            elif cur_title is not None:
                buf.append(ln)
        flush()
        return Briefing(title=doc_title or "Apresentação", sections=sections)

    def _section_from_block(self, title: str, block: str) -> Section:
        # bloco de código cercado por ```
        code = None
        code_lang = None
        cm = re.search(r"```(\w*)\n(.*?)```", block, re.DOTALL)
        if cm:
            code_lang = cm.group(1) or None
            code = cm.group(2).rstrip("\n")
        block_no_code = re.sub(r"```.*?```", "", block, flags=re.DOTALL)

        # citação em bloco (>)
        quote = None
        qlines = [re.sub(r"^\s*>\s?", "", l) for l in block_no_code.splitlines()
                  if l.lstrip().startswith(">")]
        if qlines:
            quote = " ".join(q.strip().strip('"“”') for q in qlines).strip()

        # itens paralelos (listas -, *, +)
        items = [re.sub(r"^\s*[-*+]\s+", "", l).strip()
                 for l in block_no_code.splitlines()
                 if re.match(r"^\s*[-*+]\s+", l)]

        # pontos-chave: itens da lista, ou frases do corpo
        key_points = list(items)
        if not key_points:
            prose = " ".join(l.strip() for l in block_no_code.splitlines()
                             if l.strip() and not l.lstrip().startswith(">"))
            key_points = [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()][:3]

        return Section(title=title, body=block.strip(), key_points=key_points,
                       quote=quote, code=code, code_lang=code_lang)

    # ---------- Posto 2: plan ----------------------------------------
    def plan(self, briefing: Briefing) -> SlidePlan:
        """Capa + 1 slide por seção (tipo inferido) + encerramento."""
        slides: List[SlideSpec] = [
            SlideSpec(kind="cover", title=briefing.title,
                      subtitle="Apresentação científica gerada pelo método MIRA")
        ]
        for sec in briefing.sections:
            slides.append(self._slide_from_section(sec))
        slides.append(SlideSpec(
            kind="closing", title="Obrigado",
            subtitle="Perguntas, discussão e próximos passos"))
        return SlidePlan(title=briefing.title, slides=slides)

    def _slide_from_section(self, sec: Section) -> SlideSpec:
        # O formato do card acompanha o formato da ideia.
        if sec.quote:
            return SlideSpec(kind="quote", title=sec.title, quote=sec.quote,
                             subtitle=self._lead(sec))
        if sec.code:
            return SlideSpec(kind="code", title=sec.title, code=sec.code,
                             code_lang=sec.code_lang, subtitle=self._lead(sec))
        if len(sec.key_points) >= 3 and not sec.body.count(". ") > len(sec.key_points):
            return SlideSpec(kind="grid", title=sec.title, items=sec.key_points,
                             subtitle="Aplicações em paralelo")
        # padrão: conceito com metáfora animada (a "alma" preservada)
        met = self._mira.pick_metaphor(f"{sec.title} {sec.body}")
        return SlideSpec(kind="concept", title=sec.title,
                         subtitle=self._lead(sec) or met.loop.capitalize(),
                         metaphor_key=met.key)

    @staticmethod
    def _lead(sec: Section) -> str:
        return sec.key_points[0] if sec.key_points else ""

    # ---------- Posto 3: copywrite -----------------------------------
    def copywrite(self, plan: SlidePlan) -> SlidePlan:
        """Refina textos: títulos clipados a ≤6 palavras, subtítulos enxutos."""
        for s in plan.slides:
            s.title = self._clip_title(s.title)
            if s.subtitle:
                s.subtitle = self._clip_sentence(s.subtitle, 14)
        return plan

    @staticmethod
    def _clip_title(title: str) -> str:
        words = title.replace("—", " ").split()
        return " ".join(words[:MAX_TITLE_WORDS]).strip(" ,;:")

    @staticmethod
    def _clip_sentence(text: str, max_words: int) -> str:
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]).rstrip(" ,;:") + "…"

    # ---------- Posto 4: build ---------------------------------------
    def build(self, plan: SlidePlan) -> Deck:
        """Monta UM HTML autocontido: cards de vidro + navegação card-a-card.

        Sem animação ainda (sem `@keyframes`/`infinite`) — isso é
        responsabilidade do posto `animate`, para que a fronteira entre
        os dois estágios seja verificável.
        """
        cards = "\n".join(self._card_html(i, s) for i, s in enumerate(plan.slides))
        title = _html.escape(plan.title)
        bg, fg, muted = self._palette()
        deck_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Apresentação MIRA</title>
<style>
  :root {{ --bg:{bg}; --fg:{fg}; --muted:{muted}; --line:#30363d; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
         font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
         min-height:100vh; overflow:hidden; }}
  .deck {{ position:relative; width:100vw; height:100vh; }}
  .slide {{ position:absolute; inset:0; display:none; align-items:center;
           justify-content:center; padding:5vh 6vw; }}
  .slide.active {{ display:flex; }}
  .glass-card {{ width:min(1120px, 92vw); max-height:86vh; overflow:auto;
                background:rgba(255,255,255,0.05); border:1px solid var(--line);
                border-radius:22px; padding:38px 46px;
                backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
                box-shadow: 0 18px 60px rgba(0,0,0,0.45); }}
  .glass-card h1 {{ margin:0 0 10px; font-size:clamp(26px,4vw,44px); line-height:1.1; }}
  .glass-card .sub {{ margin:0 0 22px; color:var(--muted); font-size:clamp(15px,1.7vw,20px); }}
  .accent {{ height:6px; width:120px; border-radius:6px;
            background:linear-gradient(90deg,#58a6ff,#3fb950,#d29922); margin:0 0 20px; }}
  .anim-stage {{ width:100%; height:auto; max-height:52vh; border-radius:14px;
                background:rgba(0,0,0,0.25); }}
  blockquote {{ margin:0; font-size:clamp(22px,3vw,34px); line-height:1.35;
               border-left:5px solid #58a6ff; padding-left:22px; }}
  pre {{ background:rgba(0,0,0,0.4); border:1px solid var(--line); border-radius:12px;
        padding:20px 22px; overflow:auto; font-size:clamp(14px,1.6vw,18px);
        font-family: ui-monospace, "SF Mono", Menlo, monospace; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
          gap:16px; }}
  .grid .cell {{ background:rgba(255,255,255,0.04); border:1px solid var(--line);
                border-radius:14px; padding:18px 20px; font-size:clamp(15px,1.7vw,19px); }}
  .cover h1 {{ font-size:clamp(34px,6vw,68px); }}
  nav {{ position:fixed; bottom:22px; right:26px; display:flex; gap:10px; z-index:10; }}
  nav button {{ background:rgba(33,38,45,0.8); color:var(--fg); border:1px solid var(--line);
               border-radius:10px; padding:10px 16px; cursor:pointer; font-size:16px;
               backdrop-filter: blur(6px); }}
  nav button:hover {{ border-color:#58a6ff; }}
  .counter {{ position:fixed; bottom:30px; left:26px; color:var(--muted);
             font-size:14px; z-index:10; }}
</style>
</head>
<body>
<div class="deck" id="deck">
{cards}
</div>
<div class="counter" id="counter"></div>
<nav>
  <button type="button" onclick="miraGo(-1)" aria-label="Anterior">‹ Anterior</button>
  <button type="button" onclick="miraGo(1)" aria-label="Próximo">Próximo ›</button>
</nav>
<script>
  var miraIdx = 0;
  var miraSlides = document.querySelectorAll('.slide');
  function miraShow(n) {{
    miraIdx = Math.max(0, Math.min(miraSlides.length - 1, n));
    miraSlides.forEach(function(s, i) {{ s.classList.toggle('active', i === miraIdx); }});
    var c = document.getElementById('counter');
    if (c) c.textContent = (miraIdx + 1) + ' / ' + miraSlides.length;
  }}
  function miraGo(d) {{ miraShow(miraIdx + d); }}
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') miraGo(1);
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') miraGo(-1);
    else if (e.key === 'Home') miraShow(0);
    else if (e.key === 'End') miraShow(miraSlides.length - 1);
  }});
  miraShow(0);
</script>
</body>
</html>
"""
        return Deck(title=plan.title, slides=plan.slides, html=deck_html)

    def _card_html(self, index: int, s: SlideSpec) -> str:
        title = _html.escape(s.title)
        sub = f'<p class="sub">{_html.escape(s.subtitle)}</p>' if s.subtitle else ""
        klass = "cover" if s.kind == "cover" else ""
        inner = ""
        if s.kind == "quote":
            inner = f"<blockquote>{_html.escape(s.quote or '')}</blockquote>"
        elif s.kind == "code":
            inner = f"<pre><code>{_html.escape(s.code or '')}</code></pre>"
        elif s.kind == "grid":
            cells = "".join(f'<div class="cell">{_html.escape(it)}</div>' for it in s.items)
            inner = f'<div class="grid">{cells}</div>'
        elif s.kind == "concept":
            inner = _METAPHOR_MARK.format(key=s.metaphor_key or "pipeline")
        active = " active" if index == 0 else ""
        return (f'<section class="slide{active}" data-kind="{s.kind}" data-index="{index}">'
                f'<div class="glass-card {klass}">'
                f'<div class="accent"></div>'
                f'<h1>{title}</h1>{sub}{inner}'
                f'</div></section>')

    # ---------- Posto 5: animate (Regra Zero) ------------------------
    def animate(self, deck: Deck) -> Deck:
        """Aplica a Regra Zero: coreografia de entrada + loop perpétuo por card,
        e injeta a cena SVG da metáfora nos cards de conceito."""
        anim_css = """
<style id="mira-anim">
  .slide.active .glass-card { animation: cardEnter 0.7s cubic-bezier(.22,1,.36,1) both; }
  @keyframes cardEnter {
    from { opacity: 0; transform: translateY(34px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .accent { animation: accentFlow 4s ease-in-out infinite;
            background-size: 200% 100%; }
  @keyframes accentFlow {
    0%,100% { background-position: 0% 50%; transform: scaleX(1); }
    50%     { background-position: 100% 50%; transform: scaleX(1.25); }
  }
  .glass-card { animation: cardBreathe 7s ease-in-out infinite; }
  @keyframes cardBreathe {
    0%,100% { box-shadow: 0 18px 60px rgba(0,0,0,0.45); }
    50%     { box-shadow: 0 24px 80px rgba(88,166,255,0.22); }
  }
</style>
"""
        html = deck.html.replace("</head>", anim_css + "</head>", 1)
        # injeta a cena SVG animada da metáfora escolhida em cada card concept
        for met in CATALOG:
            html = html.replace(_METAPHOR_MARK.format(key=met.key), met.svg)
        # qualquer metáfora não resolvida cai no default (pipeline)
        html = re.sub(r"<!--MIRA-METAPHOR:[^>]*-->", CATALOG[0].svg, html)
        deck.html = html
        return deck

    # ---------- Posto 6: validate (inspetor final) -------------------
    def validate(self, deck: Deck) -> ConformityReport:
        """Confere a apresentação pronta e emite o relatório de conformidade."""
        html = deck.html or ""
        checks: List[tuple] = []
        violations: List[str] = []

        def check(nome: str, ok: bool, detalhe: str, violation: str = ""):
            checks.append((nome, ok, detalhe))
            if not ok:
                violations.append(violation or detalhe)

        has_entrance = "@keyframes cardEnter" in html
        check("Regra Zero: entrada", has_entrance,
              "coreografia de entrada presente" if has_entrance else "sem animação de entrada",
              "Regra Zero violada: nenhum card tem animação de entrada")

        has_loop = "infinite" in html
        check("Regra Zero: loop perpétuo", has_loop,
              "loop infinite presente" if has_loop else "nenhum loop 'infinite'",
              "Regra Zero violada: card sem loop perpétuo ('infinite' ausente)")

        for s in deck.slides:
            n = len(s.title.split())
            ok = n <= MAX_TITLE_WORDS
            check(f"Título ≤6 palavras: {s.title[:28]}", ok,
                  f"{n} palavra(s)",
                  f"Título com {n} palavras (>6): {s.title!r}")

        has_nav = "keydown" in html and "onclick" in html.lower()
        check("Navegação card-a-card", has_nav,
              "teclado + botões presentes" if has_nav else "navegação ausente",
              "Navegação card-a-card ausente (teclado/botões)")

        self_contained = ('src="http' not in html and 'href="http' not in html
                           and "<link" not in html)
        check("Autocontido (sem URLs externas)", self_contained,
              "nenhum recurso externo" if self_contained else "recurso externo detectado",
              "Recurso externo detectado — deck não é autocontido")

        glass = "backdrop-filter" in html
        check("Cards de vidro", glass,
              "glassmorphism presente" if glass else "sem backdrop-filter",
              "Cards não usam vidro translúcido (backdrop-filter ausente)")

        return ConformityReport(passed=not violations, checks=checks, violations=violations)

    # ---------- Linha completa: run ----------------------------------
    def run(self, markdown: str, output_dir: str) -> ConformityReport:
        """Executa a esteira inteira e grava `deck.html` + `CONFORMIDADE.md`."""
        deck = self.animate(self.build(self.copywrite(self.plan(self.extract(markdown)))))
        report = self.validate(deck)
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "deck.html").write_text(deck.html, encoding="utf-8")
        (out / "CONFORMIDADE.md").write_text(
            report.to_markdown(deck.title), encoding="utf-8")
        return report

    # ---------- utilidades -------------------------------------------
    def _palette(self):
        if self.theme == "dark":
            return "#0d1117", "#e6edf3", "#8b949e"
        return "#ffffff", "#111111", "#555555"
