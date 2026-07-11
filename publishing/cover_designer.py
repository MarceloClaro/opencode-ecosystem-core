# -*- coding: utf-8 -*-
"""
Automated Cover Designer (SPEC-019)
Gera capas e contracapas de livros com estudo de paleta, tipografia e
prompts de ilustração baseados no tema e no estilo do leitor.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("publishing.cover")

# Paletas inspiradas em best-sellers e inovadores
PALETTES = {
    "tecnologia": {
        "primary": "002B5B",  # Deep Blue
        "secondary": "00A8CC", # Cyan
        "accent": "F3C623",    # Gold
        "bg": "F4F6F9",        # Off-white
        "text": "1A1A1A",      # Almost black
        "font_title": "Montserrat, sans-serif",
        "font_body": "Open Sans, sans-serif",
        "vibe": "Futurista, limpo, inovador (estilo O'Reilly / MIT Press)"
    },
    "academico": {
        "primary": "2C3E50",  # Dark Slate
        "secondary": "E74C3C", # Crimson
        "accent": "ECF0F1",    # Cloud
        "bg": "FFFFFF",        # White
        "text": "2C3E50",      # Dark Slate
        "font_title": "Merriweather, sans-serif",
        "font_body": "Lora, serif",
        "vibe": "Clássico, rigoroso, atemporal (estilo Oxford / Cambridge)"
    },
    "ficcao": {
        "primary": "2B2B2B",  # Charcoal
        "secondary": "D32F2F", # Blood Red
        "accent": "FFC107",    # Amber
        "bg": "121212",        # Dark
        "text": "E0E0E0",      # Light Grey
        "font_title": "Cinzel Decorative, serif",
        "font_body": "Crimson Text, serif",
        "vibe": "Misterioso, envolvente, dramático (estilo Penguin Random House)"
    },
    "didatico": {
        "primary": "4CAF50",  # Green
        "secondary": "FF9800", # Orange
        "accent": "03A9F4",    # Light Blue
        "bg": "FAFAFA",        # Very Light Grey
        "text": "212121",      # Dark Grey
        "font_title": "Nunito, sans-serif",
        "font_body": "Roboto, sans-serif",
        "vibe": "Vibrante, acessível, engajador (estilo 'Senku Ishigami' / didático jovem)"
    }
}

# Espessura estimada por página (mm) — papel offset 75g, impressão frente
# e verso. Estimativa editorial comum; a lombada real depende da gráfica.
MM_PER_PAGE = 0.0722


class CoverDesigner:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _determine_style(self, title: str, content_sample: str) -> str:
        """Determina o estilo base da paleta analisando o título e o conteúdo.

        Usa correspondência por *palavra inteira* (fronteira `\\b`) — sem
        isso, a palavra-chave curta "ia" casava como substring dentro de
        termos comuns (ex.: "colônia", "história") e classificava
        indevidamente romances como "tecnologia".
        """
        text = (title + " " + content_sample).lower()

        def has(words):
            return any(re.search(r"\b" + re.escape(w) + r"\b", text) for w in words)

        if has(["código", "ia", "tecnologia", "dados", "algoritmo", "software",
                "deep learning", "machine learning", "python"]):
            return "tecnologia"
        elif has(["teorema", "análise", "estudo", "pesquisa", "qualis", "tese"]):
            return "academico"
        elif has(["didático", "jovem", "aprenda", "guia", "prático", "fácil"]):
            return "didatico"
        return "ficcao"

    def _generate_internal_prompt(self, paragraph: str, palette: Dict[str, str]) -> str:
        """Gera um prompt de ilustração didática para um parágrafo complexo."""
        # Extrai palavras-chave simples (heurística básica)
        words = [w.strip(".,!?:;()") for w in paragraph.split() if len(w) > 5]
        keywords = ", ".join(words[:4])
        
        return (
            f"Didactic technical illustration explaining {keywords}. "
            f"Style: vibrant, engaging, 'Senku Ishigami' anime genius vibe, clear technical explanation. "
            f"Color palette: #{palette['primary']}, #{palette['secondary']}, #{palette['accent']}. "
            f"Clean vector art, masterpiece, 8k resolution --ar 16:9"
        )

    def illustrate_internals(self, markdown_content: str, style_key: str) -> str:
        """
        Analisa o Markdown e injeta blocos de ilustração didática (prompts)
        após parágrafos longos ou complexos.
        """
        palette = PALETTES.get(style_key, PALETTES["didatico"])
        lines = markdown_content.splitlines()
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            # Heurística: parágrafos longos (mais de 150 caracteres) ganham ilustração
            if len(line.strip()) > 150 and not line.startswith(("#", ">", "-", "*", " ")):
                prompt = self._generate_internal_prompt(line, palette)
                block = (
                    f"\n> **[ILUSTRAÇÃO DIDÁTICA SUGERIDA]**\n"
                    f"> *Prompt:* `{prompt}`\n"
                    f"> *(Insira aqui a imagem gerada para facilitar a compreensão do conceito acima)*\n"
                )
                new_lines.append(block)
                
        return "\n".join(new_lines)

    # ── Arte vetorial TikZ (R124): gradiente + formas por estilo ──
    def _tikz_art(self, style_key: str, palette: Dict[str, str]) -> str:
        """Corpo TikZ da arte de fundo da capa (full-bleed, por estilo).

        Cada estilo tem uma composição geométrica própria sobre um
        gradiente entre a primária e a secundária da paleta. Desenhado
        com `remember picture, overlay` para cobrir a página inteira. As
        formas ficam num `scope` ancorado a `current page.south west`, de
        modo que as coordenadas em cm caem sobre a página A4 (21x29,7 cm)
        — sem isso, com `overlay`, elas seriam posicionadas fora da folha.
        (Requer duas passadas de compilação, como todo `remember picture`.)
        """
        p, s, a = palette["primary"], palette["secondary"], palette["accent"]
        head = ("\\begin{tikzpicture}[remember picture, overlay]\n"
                f"  \\definecolor{{cPrim}}{{HTML}}{{{p}}}\n"
                f"  \\definecolor{{cSec}}{{HTML}}{{{s}}}\n"
                f"  \\definecolor{{cAcc}}{{HTML}}{{{a}}}\n"
                "  \\shade[top color=cPrim, bottom color=cSec]\n"
                "    (current page.north west) rectangle (current page.south east);\n"
                "  \\begin{scope}[shift={(current page.south west)}]\n")

        if style_key == "tecnologia":
            body = (
                "  % malha de nós conectados (orquestração/rede)\n"
                "  \\foreach \\x in {1.5,5,8.5,12,15.5,19} {\n"
                "    \\foreach \\y in {2,7,12,17,22,27} {\n"
                "      \\fill[cAcc, opacity=0.30] (\\x,\\y) circle (2.4pt);\n"
                "    }\n"
                "  }\n"
                "  \\draw[cAcc, opacity=0.22, line width=0.6pt]\n"
                "    (1.5,2) -- (8.5,12) -- (19,7) -- (5,22) -- (15.5,27) -- (12,2);\n")
        elif style_key == "academico":
            body = (
                "  % colunas clássicas + arco (rigor atemporal)\n"
                "  \\foreach \\x in {2,6,10,14,18} {\n"
                "    \\fill[cAcc, opacity=0.14] (\\x,2) rectangle (\\x+0.9,25);\n"
                "  }\n"
                "  \\draw[cAcc, opacity=0.28, line width=1.4pt]\n"
                "    (2,25) arc (180:0:8.5 and 2.4);\n")
        elif style_key == "didatico":
            body = (
                "  % formas orgânicas coloridas (acessível, vibrante)\n"
                "  \\fill[cAcc, opacity=0.28] (4.5,23) circle (3.2);\n"
                "  \\fill[cSec, opacity=0.32] (17,7) circle (4.0);\n"
                "  \\fill[cPrim, opacity=0.22, rounded corners=18pt]\n"
                "    (11,17) rectangle (20,26);\n"
                "  \\fill[cAcc, opacity=0.20] (3,5) circle (2.2);\n")
        else:  # ficcao
            body = (
                "  % silhueta dramática + raio de luz (misterioso)\n"
                "  \\fill[black, opacity=0.55]\n"
                "    (0,0) -- (5,0) -- (7,6) -- (9,2) -- (12,9) -- (16,4)\n"
                "    -- (21,3) -- (21,0) -- cycle;\n"
                "  \\draw[cAcc, opacity=0.4, line width=1.4pt]\n"
                "    (8,26) -- (8,9);\n")

        return head + body + "  \\end{scope}\n\\end{tikzpicture}"

    def _spine_mm(self, page_count: int) -> float:
        """Largura estimada da lombada (mm) a partir do número de páginas."""
        return round(max(3.0, page_count * MM_PER_PAGE), 1)

    @staticmethod
    def _ink_for(bg_hex: str) -> str:
        """Escolhe a tinta legível (branco/preto) sobre um fundo hex dado,
        pela luminância relativa — evita título escuro em capa escura."""
        r, g, b = (int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "white" if luminance < 0.55 else "black"

    def _cover_preamble(self, palette: Dict[str, str]) -> str:
        """Pacotes necessários para os fragmentos de capa compilarem."""
        return (
            "% cover_preamble.tex — inclua no preambulo do livro com\n"
            "% \\input{cover/cover_preamble} ANTES de \\begin{document}.\n"
            "\\usepackage[dvipsnames,table,HTML]{xcolor}\n"
            "\\usepackage{tikz}\n"
            "\\usetikzlibrary{fadings,shadings,calc}\n"
            "\\usepackage{eso-pic}   % util para arte full-bleed\n"
        )

    def _spine_tex(self, title: str, author: str, palette: Dict[str, str],
                   spine_mm: float) -> str:
        """Lombada vertical: título + autor rotacionados, largura por página."""
        return (
            f"% lombada.tex — largura estimada: {spine_mm} mm "
            f"(offset 75g, ver MM_PER_PAGE)\n"
            f"\\newlength{{\\spinewidth}}\\setlength{{\\spinewidth}}{{{spine_mm}mm}}\n"
            "\\begin{tikzpicture}\n"
            f"  \\definecolor{{cPrim}}{{HTML}}{{{palette['primary']}}}\n"
            f"  \\definecolor{{cBg}}{{HTML}}{{{palette['bg']}}}\n"
            f"  \\fill[cPrim] (0,0) rectangle ({spine_mm}mm,220mm);\n"
            f"  \\node[rotate=90, cBg, font=\\bfseries\\large]\n"
            f"    at ({spine_mm/2}mm,150mm) {{{title}}};\n"
            f"  \\node[rotate=90, cBg, font=\\small]\n"
            f"    at ({spine_mm/2}mm,60mm) {{{author}}};\n"
            "\\end{tikzpicture}\n"
        )

    def _ficha_catalografica(self, title: str, author: str, subtitle: str,
                             isbn: str, palette: Dict[str, str]) -> str:
        """Ficha catalográfica no modelo CIP brasileiro (bloco monoespaçado)."""
        isbn_line = f"ISBN {isbn}" if isbn else "ISBN 000-00-0000-000-0 (a atribuir)"
        sub = f" : {subtitle}" if subtitle else ""
        return (
            "\\begin{center}\\small\n"
            "\\fbox{\\begin{minipage}{0.82\\textwidth}\\ttfamily\\footnotesize\n"
            "\\begin{center}Dados Internacionais de Catalogação na Publicação (CIP)\\end{center}\n"
            "\\vspace{4pt}\\hrule\\vspace{4pt}\n"
            f"{author}.\\\\\n"
            f"\\hspace*{{1em}}{title}{sub} / {author}. --\\\\\n"
            "\\hspace*{1em}1. ed. -- [S.l.]: OpenCode Ecosystem, \\the\\year{}.\\\\\n"
            "\\vspace{4pt}\n"
            f"\\hspace*{{1em}}{isbn_line}\\\\\n"
            "\\vspace{4pt}\n"
            "\\hspace*{1em}1. Título. 2. Ciência. 3. Tecnologia.\\\\\n"
            "\\begin{flushright}CDD 001\\end{flushright}\n"
            "\\end{minipage}}\n"
            "\\end{center}\n"
        )

    def design_cover(self, title: str, author: str, content_sample: str,
                     subtitle: str = "", blurb: str = "",
                     page_count: int = 200, isbn: str = "") -> Dict[str, Any]:
        """
        Gera o estudo de design e os arquivos LaTeX da capa, lombada e
        contracapa com arte vetorial TikZ real (gradiente + formas por
        estilo), lombada dimensionada pela contagem de páginas e ficha
        catalográfica (CIP) — compiláveis direto no PDF do livro.
        """
        style_key = self._determine_style(title, content_sample)
        palette = PALETTES[style_key]
        spine_mm = self._spine_mm(page_count)

        # 1. Estudo de Design (DESIGN_STUDY.md)
        study_md = f"""# Estudo de Design Automatizado: {title}

## 1. Análise de Público e Tema
- **Tema detectado:** {style_key.capitalize()}
- **Vibe:** {palette['vibe']}
- **Público-alvo:** Leitores exigentes que buscam clareza, rigor e inovação.

## 2. Paleta de Cores (Psicologia das Cores)
- **Primária:** #{palette['primary']} (Confiança, autoridade)
- **Secundária:** #{palette['secondary']} (Destaque, energia)
- **Acento:** #{palette['accent']} (Detalhes e call-to-action)
- **Fundo:** #{palette['bg']} (Leitura confortável)
- **Texto:** #{palette['text']} (Alto contraste)

## 3. Tipografia
- **Título:** {palette['font_title']} (Impacto visual)
- **Corpo:** {palette['font_body']} (Legibilidade prolongada)

## 4. Prompts de Ilustração (Midjourney / DALL-E / MIRA)
**Prompt Capa:**
> Minimalist book cover art for a book titled "{title}". Style: {palette['vibe']}. Color palette: #{palette['primary']}, #{palette['secondary']}, #{palette['accent']}. Clean composition, negative space, highly conceptual, vector art style, masterpiece, 8k resolution --ar 2:3

**Prompt Contracapa:**
> Minimalist back cover art, subtle continuation of the front cover theme. Abstract geometric shapes, plenty of negative space for text, color palette: #{palette['primary']}, #{palette['bg']}. Elegant, editorial design --ar 2:3

## 5. Arte vetorial embutida (TikZ) — R124
A capa, a lombada e a contracapa já saem com arte vetorial **compilável
no PDF** (gradiente + formas geométricas do estilo *{style_key}*), sem
depender de gerador de imagem externo. Para compilar, inclua o preâmbulo
gerado **antes** de `\\begin{{document}}`:

```latex
\\input{{cover/cover_preamble}}   % carrega tikz + xcolor(HTML)
```

- **Capa:** `cover/capa.tex` (arte full-bleed + título/autor por cima)
- **Lombada:** `cover/lombada.tex` (largura ≈ {spine_mm} mm para {page_count} páginas)
- **Contracapa:** `cover/contracapa.tex` (blurb + ficha catalográfica CIP)
"""
        (self.output_dir / "DESIGN_STUDY.md").write_text(study_md, encoding="utf-8")

        # 2. Preâmbulo com os pacotes necessários (tikz + xcolor HTML)
        preamble_tex = self._cover_preamble(palette)
        (self.output_dir / "cover_preamble.tex").write_text(preamble_tex, encoding="utf-8")

        # 3. Gerar capa.tex — arte vetorial TikZ + título/autor por cima
        art = self._tikz_art(style_key, palette)
        ink = self._ink_for(palette['primary'])
        capa_tex = f"""\\begin{{titlepage}}
\\pagecolor[HTML]{{{palette['primary']}}}
\\color{{{ink}}}
% arte vetorial de fundo (full-bleed), gerada pelo CoverDesigner (R124)
{art}
\\begin{{center}}
\\vspace*{{3cm}}
{{\\Huge \\textbf{{{title}}}}}\\\\[1cm]
{{\\Large {subtitle}}}\\\\[3cm]
\\vfill
{{\\Large \\textbf{{{author}}}}}\\\\[1cm]
\\end{{center}}
\\end{{titlepage}}
\\nopagecolor
"""
        (self.output_dir / "capa.tex").write_text(capa_tex, encoding="utf-8")

        # 4. Gerar lombada.tex (spine dimensionada pela contagem de páginas)
        lombada_tex = self._spine_tex(title, author, palette, spine_mm)
        (self.output_dir / "lombada.tex").write_text(lombada_tex, encoding="utf-8")

        # 5. Gerar contracapa.tex — blurb + ficha catalográfica CIP
        ficha = self._ficha_catalografica(title, author, subtitle, isbn, palette)
        contracapa_tex = f"""\\newpage
\\thispagestyle{{empty}}
\\pagecolor[HTML]{{{palette['bg']}}}
\\color[HTML]{{{palette['text']}}}
\\vspace*{{4cm}}
\\begin{{center}}
\\begin{{minipage}}{{0.8\\textwidth}}
{{\\Large \\textbf{{Sobre o Livro}}}}\\\\[1cm]
{blurb or "Uma obra essencial que transforma a complexidade em clareza, guiando o leitor por uma jornada de descoberta e inovação."}
\\end{{minipage}}
\\end{{center}}
\\vfill
{ficha}
\\nopagecolor
"""
        (self.output_dir / "contracapa.tex").write_text(contracapa_tex, encoding="utf-8")

        logger.info(f"[cover_designer] Capa/lombada/contracapa TikZ gerados para '{title}' "
                    f"(Estilo: {style_key}, lombada {spine_mm}mm)")

        return {
            "style": style_key,
            "palette": palette,
            "spine_mm": spine_mm,
            "study_file": str(self.output_dir / "DESIGN_STUDY.md"),
            "preamble_file": str(self.output_dir / "cover_preamble.tex"),
            "capa_file": str(self.output_dir / "capa.tex"),
            "lombada_file": str(self.output_dir / "lombada.tex"),
            "contracapa_file": str(self.output_dir / "contracapa.tex"),
        }
