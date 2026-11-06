# Projeto LaTeX: Main Dark

> Gerado automaticamente por **pdf2latex** — OpenCode Ecosystem Core
> Fonte: `main-dark.pdf`
> SPEC-962

## Estrutura do Projeto

```
.
├── main.tex              # Arquivo principal
├── Makefile              # Comandos de compilação
├── referencias.bib       # Referências extraídas
├── README.md             # Este arquivo
├── capitulos/            # Capítulos em arquivos separados
│   ├── 00_*.tex
│   ├── capitulo_01_*.tex
│   └── ...
└── figures/              # Figuras extraídas
    ├── fig_*.png
    └── ...
```

## Compilar

```bash
make          # Compilar completo
make quick    # Apenas pdflatex
make clean    # Limpar arquivos auxiliares
make view     # Abrir PDF gerado
```

## Estatísticas

- Total de capítulos: 11
- Total de figuras: 76
- Total de tabelas: 5
- Total de equações: 8
- Total de referências: 11

## Template

Para aplicar um template LaTeX do ecossistema:
```bash
python3 -m pdf2latex.template_integrator --project . --template abntex2
```

Templates disponíveis: `abntex2`, `abnt2025`, `acm`, `ieee`, `nature`, etc.
Veja `templates/README.md` para o catálogo completo.
