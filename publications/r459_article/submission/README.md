# Pacote de Submissão — Diversificação pós-ranqueamento no RAG científico

Manuscrito (R459/R460) em formato de **submissão a periódico** (2 colunas,
linhas numeradas), com o achado completo:
top-k vs MMR vs Recamán vs HABD.

## Arquivos
- `submission.tex` — fonte LaTeX da submissão (preâmbulo + resumo + input das 6 seções).
- `build.sh` — script reprodutível de compilação (gera `submission.pdf`).
- `submission.pdf` — **artefato gerado, gitignored** (regenerar com `bash build.sh`).
- As seções e a bibliografia são compartilhadas com o manuscrito de leitura
  (`../sections/*.tex`, `../referencias.bib`).

## Compilar
```bash
bash build.sh     # gera submission.pdf (requer pdflatex + bibtex)
```

## Sobre a classe
O ambiente não possui `IEEEtran.cls` nem `acmart.cls`; usamos a classe
`article` com `twocolumn` + `geometry`, que compila garantidamente e produz um
layout de periódico reconhecível. A conversão para a classe-alvo específica do
periódico (ex.: `IEEEtran`) é mecânica e pode ser feita após a definição do
veículo de submissão.

## Vereditos (reporte honesto, anti-overclaim)
- `refuta_H2`: Recamán empata com top-k em diversidade (Div 0.500), por operar
  sobre posições e não âncoras.
- `refuta_H3`: HABD supera em diversidade (Div 0.8333) e cobertura (1.0), mas a
  queda de relevância (10.4%) excede a tolerância de 5%.
- Valores 100% reais do `benchmarks/cohort_report.json`; escopo: corpus-piloto,
  não generaliza.
