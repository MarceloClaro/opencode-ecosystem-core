---
spec_id: SPEC-935-R270
title: Aplicação dos scanners literários e de pesquisa ao texto completo de Molambudos
component: projetos/molambudos/Molambudos_VictoriaRegia + scanners/literary_scanners.py + scanners/literary_research_scanners.py
status: verified
test_file: tests/test_r270_molambudos_full_literary_scan.py
---

# SPEC-935-R270 — Molambudos: varredura literária integral

## Objetivo

Aplicar as suítes `run_literary_scanner_suite` e `run_literary_research_scanner_suite` ao texto completo de `Molambudos — O Diário do Paciente 1.260`, extraído dos arquivos LaTeX canônicos do projeto, gerando artefatos auditáveis em JSON e Markdown.

## Critérios de aceitação

1. O corpus analisado deve ser extraído do projeto `projetos/molambudos/Molambudos_VictoriaRegia` e conter o texto integral detectável dos fragmentos, paratextos relevantes e epílogo disponíveis em LaTeX.
2. A extração deve registrar contagem de arquivos, caracteres, palavras e classes de fragmento (`MEM`, `DOC`, `LUC`, `CONT`, `Epilogo` quando disponível).
3. A suíte literária deve retornar `scanner_count: 8`, domínio `literary` e `literary_excellence_score`.
4. A suíte de pesquisa literária deve retornar `scanner_count: 4`, domínio `literary_research` e `international_research_rigor_score`.
5. Os relatórios devem preservar `overclaim_guard` e declarar que os scores são heurísticos, não equivalem a validação crítica externa, peer review ou prova de originalidade internacional.
6. Devem ser gerados ao menos dois artefatos no projeto: um JSON bruto e um Markdown interpretativo.
7. O Markdown deve conter síntese executiva, tabela de scores, principais forças, lacunas, recomendações e limitações.
8. A validação deve confirmar que os artefatos existem, são não vazios, possuem campos esperados e que os scanners não quebraram com o corpus integral.
9. Doctor final não deve apresentar falhas críticas novas.

## Não escopo

- Não realizar busca web real, JSTOR/MLA/Scopus ou verificação bibliográfica externa neste ciclo.
- Não afirmar que a obra é “validada internacionalmente”, “Qualis A1” ou “superior” sem avaliação humana externa.
- Não alterar o texto literário, o miolo KDP ou a capa.

## Resultado — 2026-07-27

Artefatos gerados em `projetos/molambudos/Molambudos_VictoriaRegia/relatorios/`:

- `molambudos_full_corpus_R270.txt` — corpus textual limpo e auditável.
- `molambudos_full_literary_scan_R270.json` — saída bruta serializada das suítes.
- `molambudos_full_literary_scan_R270.md` — relatório interpretativo com guarda anti-overclaim.

Cobertura de corpus:

- 272.314 caracteres.
- 45.601 palavras.
- 73 unidades narrativas: `MEM` 26, `DOC` 27, `LUC` 14, `CONT` 5, `Epilogo` 1.
- 84 chamadas de `\input` expandidas; 84 arquivos únicos; 0 inputs ausentes.
- SHA-256 do corpus limpo: `2bee23728309fd08b07082f0fefcf644089da150681d21a28e6aea4122b52647`.

Resultados heurísticos:

- Suíte literária: `scanner_count: 8`, `literary_excellence_score: 97.67`, grau bruto `excelente`.
- Suíte de pesquisa literária: `scanner_count: 4`, `international_research_rigor_score: 63.72`, grau bruto `consistente`.

Validação:

- RED inicial: `pytest -q tests/test_r269_molambudos_full_literary_scan.py` falhou antes dos artefatos existirem.
- Conflito detectado: `R269` já constava no `evolution/cycles.json`; a execução foi migrada para `R270`.
- GREEN final: `pytest -q tests/test_r270_molambudos_full_literary_scan.py` → 4 passed.
- Regressão combinada: `pytest -q tests/test_r267_literary_scanners.py tests/test_r268_literary_agents_research_scanners.py tests/test_r270_molambudos_full_literary_scan.py` → 19 passed.
- Doctor final: sem falhas críticas novas; permanecem apenas avisos ambientais de loop spec ausente, `scihub-cli` ausente e LiteRT-LM sem readiness.

Guarda interpretativa:

- Os scores altos indicam aderência a marcadores heurísticos internos, não validação objetiva de qualidade literária.
- Resultados `100.00` indicam saturação de marcadores lexicais/formais, não perfeição estética.
- Sem crítica humana comparativa, corpus externo, recepção especializada e revisão acadêmica, a formulação segura é: a obra é candidata forte para leitura crítica aprofundada.
