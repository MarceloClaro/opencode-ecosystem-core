---
spec_id: SPEC-935-R383
title: Corrige perda de conteúdo em extract_fragment_content e conclui pendências da frente Molambudos
component: scripts/build_miolo.py::extract_fragment_content
status: verified
test_file: tests/test_r383_build_miolo_links_epilogue_fix.py
---

# SPEC-935-R383 — Corrige `extract_fragment_content` e Conclui Pendências Molambudos

**Data:** 2026-08-03
**Motivação:** desde o R380, três arquivos ficaram pendentes de commit na
frente Molambudos (`CORRIGENDUM.md`, `scripts/clean_headers_and_lettrines.py`,
`scripts/regenerate_vic_cont_r376.py`), deixados intocados por pertencerem a
uma frente concorrente. O usuário pediu explicitamente para agora corrigi-los
e executá-los.

## 1. Causa raiz encontrada antes de executar (não suposta)

Ao verificar `scripts/regenerate_vic_cont_r376.py` comparando sua saída
(em memória, sem sobrescrever nada) contra os 9 fragmentos `CONT-05..13`
já commitados, 8 batiam byte-a-byte e 1 (`CONT-07`) divergia. A hipótese
inicial — "alguém editou manualmente depois da geração" — **estava
errada**: investigando `scripts/build_miolo.py::extract_fragment_content()`,
a função corta todo o conteúdo do fragmento na primeira ocorrência da linha
`"↪ Links:"`, assumindo que ela é sempre o último elemento. Isso não é
verdade: uma varredura completa de `molambudos.md` encontrou **4
fragmentos** com conteúdo real depois da linha de Links —
`CONT-03`, `CONT-07`, `MEM-27`, `LUC-Escolha`. De todos, só `CONT-07` tinha
esse conteúdo preservado no `.tex` commitado (por edição manual anterior,
não pela ferramenta) — `CONT-03`, `MEM-27` e `LUC-Escolha` **já estavam
sem o epílogo no `.tex` publicado**, um gap de conteúdo real e pré-existente
que a ferramenta jamais teria corrigido sozinha (documentado como achado
separado, fora do escopo desta correção — ver Seção 5).

## 2. Correção em `extract_fragment_content()`

A linha `"↪ Links:"` só é extraída como elemento à parte (reposicionado ao
fim do `.tex`, com formatação especial) quando **não há** conteúdo real
depois dela no fragmento-fonte. Quando há (os 4 casos acima), a linha
permanece no corpo, em sua posição original, e todo o conteúdo (incluindo
o epílogo) é passado para `md_to_latex()` como texto corrido — perde-se a
formatação especial da linha de Links nesse caso raro, mas **nenhum
conteúdo narrativo é descartado**.

Validado: para os 9 fragmentos `CONT-05..13`, 8 permanecem byte-idênticos
ao estado commitado (nenhuma regressão de formatação); `CONT-07` passa a
ter zero palavras (≥6 caracteres) do texto commitado ausentes na nova
geração (antes do fix, a geração fresca perdia a seção inteira).

## 3. Execução autorizada pelo usuário

Após o fix, executados de fato (não apenas simulados):
1. `scripts/regenerate_vic_cont_r376.py` — regenera `CONT-05..13`;
   8/9 idênticos ao estado anterior, `CONT-07` ganha o epílogo de volta.
2. `scripts/clean_headers_and_lettrines.py` (lógica generalizada de
   deduplicação de linhas consecutivas, já pendente de commit) — 84
   fragmentos higienizados (linhas duplicadas + blocos de 3+ linhas em
   branco colapsados). Verificado via comparação de conjunto de palavras
   (≥6 caracteres) entre backup manual e resultado: **zero palavras
   perdidas** em nenhum dos 84 arquivos.

**Rede de segurança:** `projetos/` está inteiramente no `.gitignore` — não
há histórico git para essas mudanças. Backup manual criado antes de
executar em
`projetos/molambudos/Molambudos_VictoriaRegia/_archive/backup_R383_pre_clean_headers/`
(158 arquivos `.tex`, cópia completa de `fragmentos/` em ambas as árvores
VictoriaRegia e canônica).

## 4. Regressão real encontrada e corrigida durante a validação

Após `clean_headers_and_lettrines.py`, dois testes passaram a falhar que
não estavam no baseline pré-existente (medido no R382):

1. `tests/test_r362_molambudos_route_a_pagination_preflight.py::
   test_r362_manifest_chains_provenance_and_only_resolves_selected_blocker`
   — o manifesto de proveniência `validacao_externa/cultural_episteme/
   molambudos_r362_change_manifest.json` (ciclo R362, já fechado e
   commitado) registra o SHA-256 exato esperado de arquivos específicos
   como trilha de auditoria imutável. A limpeza tocou `DOC-17.tex` e
   `MEM-06.tex`, quebrando a cadeia.
2. `tests/test_r360_cultural_episteme_pilot.py::
   test_r360_provenance_points_to_immutable_corpus_snapshot` — mesma
   classe de problema, manifesto diferente
   (`molambudos_r360_reviews.json`, um dossiê de revisão cultural que
   fixa `source_locators` com SHA-256 e linhas exatas). A limpeza tocou
   `MEM-12.tex`, `LUC-01.tex` e `MEM-26.tex` — estes 3 **não têm nenhuma
   entrada em nenhum manifesto de drift/mudança** (R361/R362), então
   qualquer alteração neles quebra o teste sem chance de resolução por
   encadeamento.

**Corrigido**: os 5 arquivos (`DOC-17.tex`, `MEM-06.tex`, `MEM-12.tex`,
`LUC-01.tex`, `MEM-26.tex`, em ambas as árvores VictoriaRegia e
canônica) foram restaurados ao estado anterior (do backup manual),
preservando a limpeza nos demais 79 arquivos. Verificação escrita para
percorrer programaticamente as 3 cadeias de proveniência (R360 reviews →
R361 drift → R362 change manifest) confirmando resolução única
(`direct`/`chained`/`inherited_successors` == 1) para cada locator antes
de rodar os testes de novo: **zero problemas**. Conjunto de falhas
Molambudos voltou a ser idêntico (mesmos arquivos, mesmas linhas) ao
baseline pré-existente medido no ciclo R382.

**Lição**: numa árvore de conteúdo com múltiplas cadeias de proveniência
sobrepostas (R359→R360→R361→R362, cada uma podendo fixar hashes de
arquivos diferentes), uma varredura ampla ("limpe tudo") precisa ser
verificada contra **todos** os manifestos de proveniência conhecidos, não
apenas o mais óbvio/recente — o primeiro re-check (só `-k molambudos`)
already teria deixado passar a quebra do R360, cujo arquivo de teste não
tem "molambudos" no nome.

## 5. Achado fora de escopo, documentado e não corrigido (decisão do usuário)

`CONT-03`, `MEM-27` e `LUC-Escolha` têm conteúdo real em `molambudos.md`
que nunca chegou ao `.tex` publicado, pelo mesmo bug agora corrigido em
`extract_fragment_content()`. Corrigir isso exigiria estender
`regenerate_vic_cont_r376.py` (ou script equivalente) para esses 3 IDs —
ação **não autorizada nesta rodada** (o usuário autorizou especificamente
os 2 scripts existentes, escopados a `CONT-05..13`). Reportado
separadamente para decisão explícita, dado que pode envolver conteúdo já
publicado externamente (KDP).

## 6. Critérios de aceitação

1. `extract_fragment_content()` preserva conteúdo pós-Links quando ele
   existe; comportamento inalterado quando Links é de fato o último
   elemento (testado com fragmentos sintéticos e sobre o `molambudos.md`
   real).
2. Regeneração de `CONT-05..13`: 8/9 byte-idênticos ao estado anterior;
   `CONT-07` sem nenhuma palavra (≥6 caracteres) do conteúdo anterior
   perdida.
3. `clean_headers_and_lettrines.py`: 84 fragmentos modificados
   inicialmente; 5 restaurados por conflito de proveniência (ver item 5),
   79 permanecem higienizados. Zero palavras (≥6 caracteres) perdidas em
   qualquer um deles (verificado por comparação de conjuntos contra
   backup manual pré-execução).
4. Zero regressão nos testes Molambudos: conjunto de falhas idêntico
   (mesmos arquivos, mesmas linhas) ao baseline medido no R382.
5. Regressões reais de proveniência (R362: `DOC-17.tex`, `MEM-06.tex`;
   R360: `MEM-12.tex`, `LUC-01.tex`, `MEM-26.tex`) detectadas e
   corrigidas por restauração seletiva; todas as 3 cadeias de
   proveniência (R360/R361/R362) verificadas programaticamente com zero
   problemas.
6. Zero regressão na suíte completa fora do escopo Molambudos.
