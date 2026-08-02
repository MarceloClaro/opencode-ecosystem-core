---
spec_id: SPEC-935-R266
title: Ficha de estudo crítica de Molambudos com scanners e tipografia do livro
component: projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r265_r279_spec_deliverables.py
---

# SPEC-935-R266 — Ficha de estudo crítica de Molambudos

## Objetivo

Produzir uma ficha de estudo minuciosa sobre `Molambudos — O Diário do Paciente 1.260`, articulando leitura literária, técnica editorial, fundamentos teóricos, fundamentos do projeto literário, contribuição, fichamentos críticos, resenhas, limitações e impactos.

## Escopo

- Usar evidências dos fontes LaTeX, do PDF final 160 × 230 mm com folios e das auditorias/scanners R264–R265.
- Executar scanners aplicáveis do ecossistema e interpretar seus resultados sem overclaim.
- Gerar artefato em LaTeX/PDF com tipografia compatível com o livro: EB Garamond, fundo sépia, corpo amplo, espaçamento respirado, títulos em versalete/ornamento e atmosfera editorial coerente.

## Saídas esperadas

- `ficha_estudo_molambudos_scanners.tex`
- `ficha_estudo_molambudos_scanners.pdf`

## Critérios de aceitação

1. A ficha existe em `.tex` e `.pdf`.
2. A ficha compila sem erro fatal com `latexmk`.
3. O PDF abre e possui texto extraível.
4. As fontes principais estão incorporadas.
5. A tipografia preserva afinidade visual com o livro: EB Garamond, fundo sépia, títulos ornamentais e corpo legível.
6. O documento contém ficha técnica da obra.
7. O documento contém metodologia de leitura e uso dos scanners.
8. O documento descreve a arquitetura material do livro: formato, páginas, rotas, fragmentos, folios e KDP.
9. O documento descreve a arquitetura literária: fragmentação, arquivo clínico, navegação não linear, contaminação narrativa e pacto com o leitor.
10. O documento apresenta fundamentos teóricos sem afirmar validação externa inexistente.
11. O documento contém resenha descritiva e resenha crítica.
12. O documento contém fichamentos críticos organizados por eixos.
13. O documento contém limitações técnicas, editoriais, éticas e interpretativas.
14. O documento contém análise de impactos literários, pedagógicos, editoriais e sociais.
15. O documento distingue claramente miolo 10/10 local de pacote KDP completo pendente de capa/lombada 296p.
16. O documento inclui conclusão e roteiro de estudo.

## Não escopo

- Não é parecer acadêmico externo.
- Não substitui leitura humana integral linha a linha.
- Não transforma scanners científicos em prova de qualidade literária.

## Resultado — 2026-07-27

Artefatos gerados:

- `projetos/molambudos/Molambudos_VictoriaRegia/ficha_estudo_molambudos_scanners.tex`
- `projetos/molambudos/Molambudos_VictoriaRegia/ficha_estudo_molambudos_scanners.pdf`

Validações:

- Compilação `latexmk` concluída sem erro fatal.
- PDF com 34 páginas.
- Tamanho de página: 160 × 230 mm.
- PDF não criptografado.
- Texto extraível com 21.954 caracteres.
- Termos de aceitação presentes: `Ficha de Estudo`, `Molambudos`, `scanners`, `Resenha crítica`, `Fichamentos críticos`, `Limitações`, `Impactos potenciais`, `Bibliografia orientadora`.
- Fontes incorporadas: EB Garamond e monoespaçada Type 1 embutidas.

Observação: há avisos tipográficos menores de underfull/um overfull pequeno em tabelas, sem bloquear a geração nem a legibilidade geral do PDF.
