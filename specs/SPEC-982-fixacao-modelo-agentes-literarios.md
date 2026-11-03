---
spec_id: SPEC-982
title: Fixação de modelo da cabeça não pode reintroduzir o retorno vazio dos agentes literários
version: 1.0.0
status: green
test_file: tests/test_r982_fixacao_modelo_agentes_literarios.py
---

# SPEC-982 — supressão auditável da fixação de modelo por categoria

## Problema

A governança de custo de tokens (SPEC-981) fixou o modelo da cabeça em todo
agente sem `model` declarado no cartão. Entre os afetados estão os agentes
literários, que o SPEC-935-R276 havia deliberadamente deixado **sem** modelo
explícito: com `model:` fixo, o runtime devolvia `task_result` vazio
(R271/R277). A cadeia de fallback foi mantida, mas a reintrodução da fixação
reabria o mesmo modo de falha silencioso — agora em 316 agentes, com 300
recebendo modelo de uma vez.

A fixação é útil para o resto do catálogo e é reversível por política; o
defeito é a ausência de uma exceção declarada, delimitada e auditável.

## Escopo

Fora de escopo: alterar o modelo global da sessão, remover a cadeia de
fallback, reavaliar a qualidade dos modelos, ou reclassificar outros agentes
por categoria. Nenhuma chamada de inferência foi executada; nenhuma
disponibilidade de executor foi verificada.

## Regras invioláveis

1. O `model` declarado no cartão permanece autoritativo.
2. A supressão remove **apenas** a fixação da cabeça; a cadeia declarada em
   `options.model_fallbacks` permanece em todos os agentes.
3. A supressão é declarada na política (`policy.no_fix_model_categories` e
   `policy.no_fix_model_prefixes`), versionada e referenciando o contrato que
   a motiva (R276). Não há lista escondida no código.
4. Metadado observado diverge do declarado, ou existe candidato alternativo
   do mesmo paciente/condição: bloqueio explícito, nunca exclusão silenciosa.

## Critérios de aceitação

1. Nenhum agente da categoria `literary` (nem com prefixo `literary-`)
   recebe `model` no `opencode.json` gerado.
2. Todo agente literário conserva `options.model_fallbacks` não vazio.
3. Agentes comuns (`coder`, `auditor`) continuam com modelo de cabeça fixado.
4. O cartão com `model` declarado (`kdp-orchestrator-phd`) mantém o valor
   declarado; o primário não recebe fixação; o modelo global não muda.
5. A política declara a exclusão e referencia R276 nas notas.
6. O manifesto publicado (`opencode.json`) é consistente com o construtor.

## Evidência de implementação

RED registrado em `tests/test_r982_fixacao_modelo_agentes_literarios.py`:
3 falhas (agentes literários com `model` no config e no artefato publicado;
política sem exclusão declarada). GREEN: 7/7.

Defeito corrigido: a função `cost_governance.head_model_for` substituiu a
condição inline de fixação em `integrations/opencode_cli.py`; a exclusão por
categoria/prefixo passou a ser lida do registro, com nota que referencia o
R276.

Pendência correlata resolvida no mesmo ciclo: `opencode.json` publicado estava
desatualizado (16 MCPs, 10 agentes com modelo) em relação ao construtor
(18 MCPs, 316 agentes). O artefato foi regenerado pelo gerador oficial.

Limites: a supressão é de política local; ela não altera o runtime do
OpenCode, e a validação real dos agentes literários em sessão nova continua
pendente (exige reinício do registry do OpenCode).

## Pendência R935 encerrada no mesmo ciclo

O inventário GDC metadata-only (SPEC-935-R935) estava pausado por
incompatibilidade de `workflow_version`/`data_release`. Passaram a ser
implementados: reconciliação de `/files/versions` para **todos** os arquivos
selecionados (não só os sem metadados), regra de compatibilidade por interseção
exata das listas `latest_release`, e a exclusão metadata-only autorizada do
arquivo `2b0106c5-7e32-423b-957f-06c9f2e7751b` com rationale de proveniência.
A autorização do operador está versionada em
`integrations/gdc_authorized_exclusions.json`. Consulta metadata-only real
reexecutada: 614 file ids únicos, 604 selecionados, release comum `46.0`,
nenhum download de conteúdo.
