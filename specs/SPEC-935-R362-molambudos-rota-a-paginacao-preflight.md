---
spec_id: SPEC-935-R362
title: Rota histórica A, paginação editorial e preflight de margens de Molambudos
component: projetos/molambudos/Molambudos_VictoriaRegia
status: red
test_file: tests/test_r362_molambudos_route_a_pagination_preflight.py
external_validation: false
human_review_required: true
release_gate: blocked
quality_verdict_allowed: false
---

# SPEC-935-R362 — Rota A, paginação e preflight editorial

**Estado:** red após revisão adversarial; release bloqueado
**Data:** 2026-08-01
**Base:** SPEC-935-R358--R361
**Decisão autoral:** rota A aprovada explicitamente pelo usuário.

## 1. Objetivo

Implementar de modo trilíngue a rota histórica A — Joaquim parte de Senador
Pompeu em 1915 e é confinado no Campo do Alagadiço, nos arredores de Fortaleza
— e corrigir paginação, rotas e enquadramento de elementos editoriais nos cinco
PDFs: PT, EN, ZH, TRI e KDP TRI.

O estado `green` desta spec significará apenas conformidade interna SDD/TDD e
preflight técnico. Os nove bloqueios R361 não resolvidos continuam impedindo
publicação e validação externa.

## 2. Contrato histórico da rota A

1. **Origem:** Senador Pompeu, Ceará, em 1915.
2. **Deslocamento:** caminhada/retirada em direção a Fortaleza.
3. **Confinamento:** Campo do Alagadiço, próximo a Fortaleza, em 1915.
4. **Patu/Senador Pompeu:** não pode ser descrito como campo de 1915; quando
   mencionado historicamente, Patu pertence a 1932--1933.
5. **Cronologia de Joaquim:** transferência/internação em 1917 e morte em 1979
   permanecem como cronologia ficcional, sem afirmar que Alagadiço funcionou de
   1915 a 1917.
6. **Números:** remover ou rebaixar números exatos não sustentados (`8.240`,
   `7.912`, `80%`, `dois terços`) e usar somente formulações atribuídas e
   aproximadas sustentadas pela pesquisa R361.
7. **Pseudoarquivos afetados:** qualquer documento reescrito pela rota A deve
   ser marcado inequivocamente como reconstituição ficcional, não transcrição
   arquivística autêntica ou autorizada.
8. **Paridade:** o mesmo fato narrativo deve permanecer alinhado em PT-BR,
   EN-US e ZH-CN; diferenças estilísticas não podem reintroduzir Patu/1915.
9. Arquivos sob `_archive/` não integram o corpus ativo e não serão alterados.

## 3. Paginação

1. Pré-textuais usam numeração romana minúscula (`i`, `ii`, `iii`...).
2. Páginas deliberadamente cegas ou capas podem ocultar o fólio, mas pertencem
   à sequência romana e não reiniciam o contador.
3. O primeiro fragmento textual reinicia em página indo-arábica `1`.
4. Corpo, documentos, investigação, contaminação e pós-textuais continuam na
   sequência indo-arábica, sem reinício indevido.
5. PT, EN, ZH, TRI e KDP TRI devem empregar uma única transição formal de
   `frontmatter` para `mainmatter`.
6. Logs não podem conter destinos PDF duplicados de `page.*`.

## 4. Rotas

1. Recompilar antes da validação.
2. Conferir 540 rotas reais: 180 PT, 180 EN e 180 ZH.
3. Cada página impressa da rota deve coincidir com o label AUX correspondente.
4. Resultado final: zero labels ausentes e zero divergências.

## 5. Margens, tabelas, imagens e fontes

1. Derivar a caixa útil das opções `geometry` de cada edição.
2. Texto narrativo, tabelas, caixas, legendas e imagens não decorativas devem
   ficar dentro da caixa útil ou de sua zona editorial explicitamente permitida.
3. Cabeçalhos e fólios podem ocupar suas zonas próprias, mas nunca sair do
   `MediaBox`/`CropBox` nem invadir a área de corte segura.
4. Capas e artes de página inteira exigem allowlist explícita de full bleed.
5. Logs finais devem ter zero `Overfull \\hbox`, zero `Overfull \\vbox`, zero
   erro fatal, zero referência indefinida e zero caractere ausente.
6. Tabelas largas devem quebrar, ajustar colunas ou usar redução local.
7. Imagens devem preservar proporção e ter `width`/`height` limitados à caixa.
8. Redução de fonte, quando necessária, deve ser local e documentada; proíbe-se
   reduzir globalmente a narrativa. Tabelas/legendas não podem ficar abaixo de
   `\footnotesize` sem decisão adicional.
9. Um auditor PDF deve registrar por página caixas de texto, imagens e desenhos,
   violações, exceções full bleed e tolerância numérica.

## 6. Entregáveis

1. Correções históricas PT/EN/ZH e paratextos ativos.
2. Paginação corrigida nos cinco documentos mestres.
3. Correções locais de tabelas, imagens, caixas e tipografia.
4. `scripts/audit_r362_pdf_layout.py`.
5. `validacao_externa/cultural_episteme/molambudos_r362_change_manifest.json`.
6. `validacao_externa/cultural_episteme/molambudos_r362_preflight.json`.
7. `validacao_externa/cultural_episteme/molambudos_r362_control_gates.json`.
8. Testes R362, logs, cinco PDFs e relatório de rotas.

## 7. Critérios de aceitação

1. Nenhum arquivo ativo associa campo de Senador Pompeu/Patu a 1915--1917.
2. Todas as ocorrências narrativas afetadas implementam origem Senador Pompeu,
   deslocamento para Fortaleza e confinamento no Alagadiço em 1915.
3. Números históricos não sustentados e falsa autoridade arquivística afetada
   pela rota A são removidos/rebaixados nos três idiomas.
4. Paginação romana pré-textual e indo-arábica textual é demonstrada nos cinco
   PDFs e nos fontes TeX; não há destinos de página duplicados.
5. Cinco builds em duas passadas concluem conforme §5.5.
6. Auditor PDF não encontra conteúdo não permitido fora das caixas editoriais.
7. Toda exceção full bleed é identificada por arquivo/página e justificada.
8. Rotas concluem 540/540, sem labels ausentes ou divergências.
9. Correções tipográficas são locais; tamanho narrativo global é preservado.
10. Regressão R358--R362 passa e snapshots anteriores recebem manifesto de
    deriva em vez de hashes retroativamente reescritos.
11. O bloqueio `patu_1915_chronology` fica `implemented_pending_external_review`;
    os nove demais bloqueios R361 continuam `blocked_author_decision`.
12. Todos os artefatos mantêm `external_validation: false`,
    `human_review_required: true`, `release_gate: blocked` e
    `quality_verdict_allowed: false`.

## 8. TDD

1. **RED:** testes históricos, paginação, rotas e preflight antes das edições.
2. **GREEN:** alterações mínimas que satisfaçam o contrato.
3. **REFACTOR:** reduzir duplicação e substituir ajustes globais por locais.
4. **VERIFY:** builds, inspeção de logs, auditor PDF, rotas e revisão adversarial.

## 9. Não escopo

- liberar publicação;
- resolver automaticamente os outros nove bloqueios R361;
- declarar equivalência cultural EN-US/ZH-CN;
- alterar arquivos de `_archive/`;
- reduzir globalmente fontes para mascarar problemas de composição.

## 10. Verificação interna provisória

- regressão R358--R362: `61 passed`;
- cinco edições compiladas em duas passadas, com recibos SHA-256;
- cinco logs sem overfull, infinite glue, destinos duplicados, referências
  indefinidas, caracteres ausentes, pedido de nova passada ou erro fatal;
- paginação PDF: romano desde a primeira página e arábico `1` no primeiro
  fragmento das cinco edições;
- auditoria por página: zero violações e oito exceções full bleed justificadas
  por edição;
- rotas: 540/540, distribuídas em 180 PT, 180 EN e 180 ZH, sem ausência ou
  divergência;
- SpecVerifier: 12/12 critérios internos.

Os resultados acima foram rebaixados a provisórios após a revisão adversarial
identificar lacunas de frescor dos recibos, vinculação integral de fontes/AUX,
eficácia das zonas editoriais, ancoragem de proveniência e publicação atômica
do gate. Nove bloqueios R361 permanecem e o KDP TRI possui 1.095 páginas, 267
acima do limite de 828 assumido no preflight.
