#!/usr/bin/env python3
"""Compile Synthetic University paper LaTeX to PDF."""
import subprocess, os, sys

path = "academic/papers/paper_universidade_sintetica.tex"
with open(path, "r") as f:
    tex = f.read()

# Convert to standard article class
tex = tex.replace(
    "\\documentclass[\n    a4paper, 12pt, twoside, openright,\n    chapter=TITLE, section=TITLE,\n    english, brazilian\n]{abntex2}",
    "\\documentclass[a4paper,12pt]{article}"
)

tex = tex.replace(
    "\\usepackage[brazilian, hyperpageref]{backref}\n\\usepackage[alf]{abntex2cite}",
    "\\usepackage{cite}"
)

tex = tex.replace(
    "\\maketitle",
    "\\maketitle\n\\vspace{1cm}\n{\\large OpenCode Ecosystem Core --- SPEC-935}\n\\vspace{0.5cm}\n{\\small \\today}"
)

tex = tex.replace("\\begin{resumo}", "\\section*{Resumo}")
tex = tex.replace("\\end{resumo}", "")
tex = tex.replace("\\begin{abstract}", "\\section*{Abstract}")
tex = tex.replace("\\end{abstract}", "")
tex = tex.replace("\\bibliography{refs}", "")

tex = tex.replace(
    "\\usepackage{hyperref}",
    "\\usepackage{hyperref}\n\\hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue}"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(tex)

print("LaTeX atualizado. Compilando...")
result = subprocess.run(
    ["pdflatex", "-interaction=nonstopmode", "-output-directory=academic/papers", path],
    capture_output=True, text=True, timeout=120
)

pdf_path = path.replace(".tex", ".pdf")
if os.path.exists(pdf_path):
    print(f"PDF gerado: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
else:
    print("Erros de compilacao:")
    for line in result.stdout.split("\n"):
        if "!" in line and ("Error" in line or "error" in line):
            print(f"  {line[:150]}")
    # Try second pass
    result2 = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-output-directory=academic/papers", path],
        capture_output=True, text=True, timeout=120
    )
    if os.path.exists(pdf_path):
        print(f"PDF gerado na 2a passada: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    else:
        sys.exit(1)
