# Artigo — Educação em computação quântica e a armadilha da renda média

Esta pasta contém o artigo, as referências verificadas e os artefatos de conversão.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `ARTIGO.md` | Manuscrito em Markdown, fonte única. |
| `ARTIGO.docx` | Conversão para DOCX (pandoc). |
| `ARTIGO.html` | Conversão HTML com CSS ABNT-like. |
| `ARTIGO.pdf` | PDF A4 gerado por WeasyPrint (21 páginas). |
| `REFERENCIAS.json` | Metadados das referências, verificados na API do Crossref. |
| `estilo_artigo.css` | Estilo A4, Times 12 pt, margens 3/2/2/3 cm. |
| `VERIFICACAO.md` | Checagens, contagens e limites. |

## Como regenerar

```bash
pandoc ARTIGO.md -f markdown+pipe_tables -t docx -o ARTIGO.docx
pandoc ARTIGO.md -f markdown+pipe_tables -t html5 -s \
  --css estilo_artigo.css \
  --metadata pagetitle="Educação em computação quântica desde a educação básica" \
  -o ARTIGO.html
../../.venv-pdf/bin/python -m weasyprint ARTIGO.html ARTIGO.pdf
```

## Escopo

- Revisão narrativa estruturada, não revisão sistemática PRISMA.
- 29 referências, 27 com DOI verificado no Crossref em 2026-11-09.
- Quatro tabelas de síntese, comparação internacional, mecanismos da armadilha da renda média e cenários para o Brasil.
- Nenhuma previsão numérica de PIB, emprego ou retorno econômico.
- Nenhuma alegação de Qualis A1, aceite editorial ou eficácia pedagógica comprovada.
