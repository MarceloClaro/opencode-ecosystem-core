# SPEC-935-R544 — Passe editorial final R522 pós-consenso RH1×RH2-IA (n=21)

**Status:** SDD executável — finalização editorial e auditoria de submissão  
**Data:** 2026-09-19  
**Escopo:** Manuscrito `manuscrito_porescrito799_R522` para Educação Por Escrito — Chamada 799  
**Dependência:** SPEC-935-R522, log de execução real R522, formulário `RH1xRH2_FORMULARIO_COMPLETO_2026-09-18.md`

## 1. Objetivo

Consolidar o manuscrito R522 após a decisão de consenso do autor na triagem RH1×RH2-IA, reduzindo o corpus final de 25 para **21 estudos incluídos**, incorporando a busca complementar 2026 como atualização contextual sem alterar denominadores, regenerando a Figura 1 PRISMA-ScR, e produzindo versões `v30_observado` e `v30_leitura_revisor` auditáveis para leitura editorial.

## 2. Entradas formais

- Matriz `matriz_extracao_R522.xlsx`, com exclusões pós-consenso em A01, B02, N03 e N12.
- Formulário completo `execucao_real/RH1xRH2_FORMULARIO_COMPLETO_2026-09-18.md`.
- Log `execucao_real/LOG_EXECUCAO_REAL_R522.md`, seção §2.31.
- Manuscrito `manuscrito_porescrito799_brasil_comparado_R522_v30_observado.docx`.
- Busca 2026 `execucao_real/openalex_2026_update.json`.

## 3. Decisões editoriais obrigatórias

1. Corpus final: **n=21**.
2. Excluídos por consenso: A01 (E2), B02 (E4), N03 (E4), N12 (E4).
3. Manter: B04, B09, N04, N07.
4. Busca 2026: Lorteau & Sarro e Schrepel citados na discussão como atualização contextual; fora dos denominadores por acesso fechado (E6). Fruehwald fora por tipo documental (preprint).
5. κ RH1×RH2-IA reportado apenas como estatística descritiva, sem alegar dois avaliadores humanos.
6. N11: declínio aproximado de 20 pontos atribuído a Choi & Schwarcz apud Alimardani, não como achado primário do quase-experimento de Alimardani.

## 4. Critérios de aceitação

- **CA1 — Corpus e frequências:** texto, tabelas e fluxograma devem usar n=21 e frequências finais D1=20/95,2%, D2=11/52,4%, D3=11/52,4%, D4=16/76,2%, D5=7/33,3%, D6=8/38,1%, E1=20/95,2%, E2=15/71,4%, E3=12/57,1%, E4=18/85,7%.
- **CA2 — PRISMA-ScR:** Figura 1 deve ser regenerada com n=21 e menção à busca 2026 sem contagem indevida no corpus.
- **CA3 — Duplo-cego:** versão `v30_leitura_revisor` não deve conter metadados autorais indevidos nem nota interna de auditoria editorial. Resíduos de `PUCRS`, `PPGEDU`, `Porto Alegre`, `R522`, `Marcelo Claro Laranjeira`, `ORCID`, `Lattes` devem ser explicitamente auditados; quando ocorrerem em rodapé/template interno, devem ser reportados e não enviados como versão final cega.
- **CA4 — Limite editorial:** PDF de leitura deve ter no máximo 20 páginas.
- **CA5 — Referências:** referências dos 21 estudos incluídos + Lorteau & Sarro + Schrepel devem estar presentes, sem placeholder PAULA e sem nota de uso interno no bloco de referências.
- **CA6 — Rastreabilidade:** SHAs finais dos artefatos devem ser recalculados e registrados em README/log final.
- **CA7 — Integridade acadêmica:** sem Sci-Hub; ausência de OSF/Turnitin marcada como pendência externa, não como concluída.

## 5. Verificações TDD/QA

- Converter `v30_leitura_revisor.docx` para PDF via LibreOffice.
- Validar páginas via `pdfinfo`.
- Extrair texto via `pdftotext` para checar resíduos e presença/ausência de termos críticos.
- Inspecionar `docx` via `python-docx` para verificar tabelas, parágrafos e remoção de nota interna.
- Recalcular SHA-256 dos arquivos finais.

## 6. Entregáveis

- `manuscrito_porescrito799_brasil_comparado_R522_v30_observado.docx` atualizado.
- `manuscrito_porescrito799_brasil_comparado_R522_v30_leitura_revisor.docx` sem nota interna.
- `manuscrito_porescrito799_brasil_comparado_R522_v30_leitura_revisor.pdf` reconvertido.
- Figura 1 substituída no DOCX.
- Registro R544 em `evolution/cycles.json`.
- `README_R522.md` atualizado com status e SHAs.
