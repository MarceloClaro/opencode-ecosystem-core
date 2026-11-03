---
spec_id: SPEC-983
title: Migração preservadora e explícita dos ciclos legados do EvolutionRegistry
version: 1.0.0
status: green
test_file: tests/test_r983_evolution_legacy_migration.py
---

# SPEC-983 — migração preservadora do histórico EvolutionRegistry

## Problema e intenção autorizada

O diagnóstico do Core relata 78 entradas do `evolution/cycles.json` que são
preservadas, mas não modeladas pelo `EvolutionRegistry`. O operador autorizou
explicitamente a migração e pediu melhoria. A advertência não deve ser removida
por tolerância global nem por coerção silenciosa: algumas entradas são legados
reconhecíveis, outras podem ser malformadas ou não ser registros de ciclo.

Esta spec estabelece migração **opt-in**, auditável, idempotente e com cópia
byte-a-byte da fonte. O carregamento normal permanece conservador; uma execução
sem `migrate_legacy_entries()` não altera arquivos nem interpreta registros
antigos.

## Escopo

1. Inspecionar e classificar cada entrada não modelada por índice, identidade
   disponível, motivo estrutural e hash canônico do payload — sem expor o
   conteúdo inteiro no relatório.
2. Migrar entradas objeto JSON reconhecíveis para os campos tipados atuais,
   usando projeções documentadas. Manter cada ciclo migrado no formato
   canônico; o backup byte-a-byte é a cópia autoritativa integral dos objetos
   originais. O ledger de topo `legacy_migrations[]` aponta para o backup por
   caminho relativo, hash global, índice de origem, hash SHA-256 canônico do
   objeto e códigos de normalização.
3. Criar, antes da publicação, backup byte-a-byte do `cycles.json` de origem.
   Um backup preexistente diferente bloqueia; um backup idêntico pode ser
   reutilizado. A publicação continua usando lock, comparação dos bytes de
   origem e substituição atômica já existentes.
4. Manter entradas não objeto ou não migráveis intactas; não descartá-las,
   não sobrescrever identificadores duplicados e não classificá-las como
   validadas. O doctor permanece `warn` se restar qualquer entrada não modelada.
5. Preservar ciclos já válidos, campos superiores desconhecidos, campos
   desconhecidos por ciclo, estatísticas e a semântica dos gravadores atuais.

## Regras invioláveis

- Sem migração automática no construtor ou no `doctor`.
- Não remover, filtrar ou reordenar ciclos.
- Não converter score inválido em número plausível; pontuação sem tipo válido
  vira `None`, mantendo o original completo no payload de origem.
- Timestamp ISO-8601 com fuso pode ser normalizado para epoch; sem timestamp
  utilizável, usar sentinel `0.0` e registrar `timestamp_missing`/
  `timestamp_invalid` (não usar o horário da migração como data histórica).
- `changes`, `lessons` e `evidence_trail` que não sejam listas são projetados
  para representações de texto determinísticas; nenhum dado original é perdido,
  pois o objeto completo permanece em `legacy_original` e no backup.
- Identidade sintética deve ser determinística (`legacy-entry-<índice>-<hash>`),
  marcada no relatório e nunca pode substituir uma identidade existente válida.
- Migração de objeto desconhecido só cria campos mínimos com razão explícita;
  entradas JSON que não são objetos permanecem intactas e não são promovidas.
- Erro de backup, concorrência, serialização ou publicação não pode alterar a
  fonte nem a memória do registro; backup incompleto nunca é tratado como prova.
- `legacy_original` é proveniência, não valida o conteúdo histórico nem atesta
  execução, revisão externa ou integridade das alegações antigas.

## Critérios de aceitação

1. `preview_legacy_migration()` é somente leitura, determinístico e informa
   contagem modelada/não modelada, entradas migráveis/não migráveis, índice,
   hash e códigos de razão.
2. `migrate_legacy_entries()` migra somente entradas não modeladas objeto;
   mantém a contagem/ordem do array; não duplica `round_id`; preserva campos
   superiores desconhecidos; o backup contém os objetos originais, e os
   registros em `legacy_migrations` apontam para índices/hash do backup, sem
   adicionar chaves não canônicas aos objetos em `cycles`.
3. Backup é byte-idêntico à fonte pré-migração; hash informado coincide;
   backup conflitante causa falha antes da alteração.
4. Publicação é idempotente: segunda execução retorna `already_migrated`, não
   cria backup diferente nem adiciona camadas `legacy_original` duplicadas.
5. Recarregar após migração modela todos os registros migrados; mudanças futuras
   em ciclos novos preservam os envelopes legados e extensões desconhecidas.
6. Registros não objeto/inválidos que não podem ser reconhecidos permanecem
   preservados e mantêm o aviso do doctor; nunca são descartados para obter
   `pass` artificial.
7. RED→GREEN: testes sintéticos de projeção e contraexemplos; teste real em
   `EVOLUTION_STATE_PATH` isolado. A migração de produção só ocorre após
   preview revisado, backup e comparação de hashes; depois, executar doctor e
   testes de regressão do EvolutionRegistry.

## Evidência e resultado

RED registrado: `tests/test_r983_evolution_legacy_migration.py` (7 falhas antes
da API de migração). GREEN: suíte dedicada + regressões R581/R929/R110/R414/
R488/R611: 123 passed.

Prévia real (somente leitura): 704 ciclos modelados, 78 objetos migráveis,
zero entradas não-objeto/não-migráveis; 24 identidades foram sintetizadas de
forma determinística por ausência/conflito de ID; 72 timestamps ISO-8601 foram
normalizados para epoch; os payloads originais permaneceram disponíveis. A
migração foi aplicada com backup byte-a-byte:
`evolution/migrations/R983/cycles.json.before`, SHA-256
`bc61356b488edeb93c8fa35ce924840fe6ed400421f891a9efb1b6c9fe703360`.
O backup byte-a-byte contém os 78 payloads originais; o ledger de topo
`legacy_migrations` registra índice, hash do backup e hash canônico por entrada.
Os objetos `cycles[]` permanecem no formato canônico.

Resultado antes de registrar o ciclo R983: 782/782 ciclos modelados; prévia
posterior 0 não modelados. Após registrar R983, o doctor reporta 783/783.
Suite completa local: 8380 passed, 66 skipped, 0 failed; `doctor` healthy
(22 pass, 0 warn, 0 fail). O ciclo R983 foi registrado no EvolutionRegistry
com hashes do backup, spec, testes, script e implementação. Isso fecha apenas
o alerta estrutural; não valida o conteúdo histórico.

## Limites

A migração modela a estrutura, não valida os fatos, scores, provas, fontes ou
execuções dos ciclos históricos. Ausência de aviso estrutural não significa
validade histórica nem auditoria externa. A revisão de conteúdo permanece fora
do escopo; somente a proveniência da transformação é atestada.
