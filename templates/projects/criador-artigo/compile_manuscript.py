#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASWOS PDF Compiler v1.0
========================
Compila o manuscrito markdown para PDF utilizando pandoc e o template LaTeX.
"""

import subprocess
import shutil
import sys
from pathlib import Path

CRIADOR_DIR = Path(__file__).resolve().parent
MD_FILE = CRIADOR_DIR / "tese_mestrado_cnpq.md"
PDF_FILE = CRIADOR_DIR / "tese_mestrado_cnpq.pdf"
TEX_FILE = CRIADOR_DIR / "tese_mestrado_cnpq.tex"
TEMPLATE_FILE = CRIADOR_DIR / "template-report.latex"

def check_dependencies():
    """Verifica se os executáveis necessários estão no PATH."""
    pandoc_path = shutil.which("pandoc")
    if not pandoc_path:
        print("[ERRO] 'pandoc' não foi encontrado no sistema. Por favor, instale o Pandoc.")
        return False
        
    pdflatex_path = shutil.which("pdflatex")
    if not pdflatex_path:
        print("[AVISO] 'pdflatex' não foi encontrado no PATH. Tentando usar motores alternativos.")
        
    return True

def compile_pdf():
    """Executa o comando de compilação do Pandoc."""
    if not MD_FILE.exists():
        print(f"[ERRO] O arquivo markdown original não foi encontrado em: {MD_FILE}")
        return False

    print(f"Lendo manuscrito: {MD_FILE.name}")
    print(f"Utilizando template: {TEMPLATE_FILE.name}")

    # Comando para gerar o PDF diretamente via pdflatex usando o template
    cmd = [
        "pandoc",
        str(MD_FILE),
        "-o", str(PDF_FILE),
        f"--template={TEMPLATE_FILE}",
        "--pdf-engine=pdflatex",
        "--top-level-division=chapter",
        "-V", "fontsize=12pt",
        "-V", "lang=pt-BR"
    ]

    print(f"Executando compilação do PDF...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[SUCESSO] PDF gerado com sucesso em: {PDF_FILE}")
        return True
    except subprocess.CalledProcessError as e:
        print("[ERRO] Falha ao compilar o PDF via Pandoc/LaTeX:")
        print(e.stderr)
        
        # Fallback: tentar compilar para .tex primeiro para depuração
        print("\nTentando gerar arquivo LaTeX (.tex) intermediário para depuração...")
        try:
            cmd_tex = [
                "pandoc",
                str(MD_FILE),
                "-o", str(TEX_FILE),
                f"--template={TEMPLATE_FILE}",
                "--top-level-division=chapter",
                "-V", "fontsize=12pt",
                "-V", "lang=pt-BR"
            ]
            subprocess.run(cmd_tex, check=True)
            print(f"[SUCESSO] LaTeX gerado em: {TEX_FILE}")
            print("Você pode compilar o arquivo .tex manualmente usando seu editor LaTeX (TeXworks, TeXstudio, etc.).")
        except Exception as tex_err:
            print(f"[ERRO] Falha ao gerar arquivo LaTeX: {tex_err}")
            
        return False
    except FileNotFoundError:
        print("[ERRO] Erro crítico ao invocar pandoc. Verifique as variáveis de ambiente do sistema.")
        return False

def main():
    print("=" * 60)
    print(" MASWOS Academic PDF Compiler ")
    print("=" * 60)
    
    if not check_dependencies():
        sys.exit(1)
        
    success = compile_pdf()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
