# Dissertação de Mestrado — PPGTE/UFC

## Metodologias Ativas: ABP e ABPr na Educação Brasileira

**Autor:** Fernando Ramos Passoni  
**Orientador:** Prof. Dr. [Nome do Orientador]  
**Programa:** Pós-Graduação em Tecnologia e Educação (PPGTE)  
**Instituição:** Universidade Federal do Ceará (UFC)  
**Defesa:** Junho de 2026 — Fortaleza/CE

---

## Estrutura de Arquivos

```
dissertacao-latex/
├── dissertacao.tex              # Arquivo principal (compilar este)
├── referencias.bib              # Banco de referências BibTeX (46 entradas)
│
├── # CAPÍTULOS (5)
├── 01_introducao.tex            # Cap. 1 — Introdução
├── 02_aspectos_estrategicos.tex # Cap. 2 — Aspectos Estratégicos
├── 03_organizacao_trabalho.tex  # Cap. 3 — Organização do Trabalho
├── 04_resultados.tex            # Cap. 4 — Apresentação e Análise dos Resultados
├── 05_conclusao.tex             # Cap. 5 — Considerações Finais
│
├── # DOCUMENTAÇÃO
├── README.md                    # Este arquivo
├── ECOSYSTEM_TASKS.md           # Documentação completa de tarefas
├── RELATORIO_NOOLOGICO_GAPS.md  # Relatório do Scanner Noológico
│
└── # SAÍDA
    └── dissertacao.pdf          # PDF compilado (94 páginas, 656 KB)
```

## Como Compilar

### Requisitos
- TeX Live ou MiKTeX instalado

### Compilação
```bash
cd "C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"

# Compilar 4 vezes para resolver todas as referências
pdflatex -interaction=nonstopmode dissertacao.tex
bibtex dissertacao
pdflatex -interaction=nonstopmode dissertacao.tex
pdflatex -interaction=nonstopmode dissertacao.tex
```

## Estatísticas

| Métrica | Quantidade |
|---------|-----------|
| Total de capítulos | **5** |
| Total de páginas | **94** |
| Tamanho do PDF | **656 KB** |
| Total de citações | **228** |
| Referências BibTeX | **46** |
| Tabelas | **12** |
| Figuras (TikZ) | **1** |
| Erros de compilação | **0** |

## Formato

- Codificação: UTF-8
- Idioma: Português Brasileiro (babel)
- Tamanho da fonte: 12pt
- Espaçamento: 1.5
- Margens: 3cm esquerda, 2cm direita, 3cm superior/inferior
- Citações: Numéricas (natbib, apalike)

## Notas

- Os capítulos são incluídos via `\input{}`
- As citações usam `\cite{}` com BibTeX
- Cross-references usam `\ref{}`

---

*Última atualização: 23 de junho de 2026*
