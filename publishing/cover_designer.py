# -*- coding: utf-8 -*-
"""
Automated Cover Designer (SPEC-019)
Gera capas e contracapas de livros com estudo de paleta, tipografia e
prompts de ilustração baseados no tema e no estilo do leitor.
"""

import json
import logging
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

class CoverDesigner:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _determine_style(self, title: str, content_sample: str) -> str:
        """Determina o estilo base da paleta analisando o título e o conteúdo."""
        text = (title + " " + content_sample).lower()
        if any(w in text for w in ["código", "ia", "tecnologia", "dados", "algoritmo", "software"]):
            return "tecnologia"
        elif any(w in text for w in ["teorema", "análise", "estudo", "pesquisa", "qualis", "tese"]):
            return "academico"
        elif any(w in text for w in ["didático", "jovem", "aprenda", "guia", "prático", "fácil"]):
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

    def design_cover(self, title: str, author: str, content_sample: str,
                     subtitle: str = "", blurb: str = "") -> Dict[str, Any]:
        """
        Gera o estudo de design, os prompts de ilustração e os arquivos LaTeX
        para a capa e contracapa.
        """
        style_key = self._determine_style(title, content_sample)
        palette = PALETTES[style_key]

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
"""
        (self.output_dir / "DESIGN_STUDY.md").write_text(study_md, encoding="utf-8")

        # 2. Gerar capa.tex
        capa_tex = f"""\\begin{{titlepage}}
\\pagecolor[HTML]{{{palette['primary']}}}
\\color[HTML]{{{palette['bg']}}}
\\begin{{center}}
\\vspace*{{3cm}}
{{\\Huge \\textbf{{{title}}}}}\\\\[1cm]
{{\\Large {subtitle}}}\\\\[3cm]
% ESPAÇO PARA ILUSTRAÇÃO DA CAPA
% \\includegraphics[width=0.8\\textwidth]{{ilustracoes/capa_arte.png}}\\\\[3cm]
\\vfill
{{\\Large \\textbf{{{author}}}}}\\\\[1cm]
\\end{{center}}
\\end{{titlepage}}
\\nopagecolor
"""
        (self.output_dir / "capa.tex").write_text(capa_tex, encoding="utf-8")

        # 3. Gerar contracapa.tex
        contracapa_tex = f"""\\newpage
\\thispagestyle{{empty}}
\\pagecolor[HTML]{{{palette['bg']}}}
\\color[HTML]{{{palette['text']}}}
\\vspace*{{5cm}}
\\begin{{center}}
\\begin{{minipage}}{{0.8\\textwidth}}
{{\\Large \\textbf{{Sobre o Livro}}}}\\\\[1cm]
{blurb or "Uma obra essencial que transforma a complexidade em clareza, guiando o leitor por uma jornada de descoberta e inovação."}
\\end{{minipage}}
\\end{{center}}
\\vfill
\\begin{{center}}
% ESPAÇO PARA ILUSTRAÇÃO DA CONTRACAPA / CÓDIGO DE BARRAS
% \\includegraphics[width=0.4\\textwidth]{{ilustracoes/contracapa_arte.png}}
\\end{{center}}
\\nopagecolor
"""
        (self.output_dir / "contracapa.tex").write_text(contracapa_tex, encoding="utf-8")

        logger.info(f"[cover_designer] Estudo de design e capas gerados para '{title}' (Estilo: {style_key})")

        return {
            "style": style_key,
            "palette": palette,
            "study_file": str(self.output_dir / "DESIGN_STUDY.md"),
            "capa_file": str(self.output_dir / "capa.tex"),
            "contracapa_file": str(self.output_dir / "contracapa.tex")
        }
