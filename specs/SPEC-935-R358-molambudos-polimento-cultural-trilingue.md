---
spec_id: SPEC-935-R358
title: Polimento cultural e tipográfico trilíngue de Molambudos
component: projetos/molambudos/Molambudos_VictoriaRegia
status: green
test_file: tests/test_r358_molambudos_polimento_cultural.py
---

# SPEC-935-R358 — Polimento cultural e tipográfico trilíngue de Molambudos

**Estado:** ativa
**Data:** 2026-08-01
**Orquestrador:** marceloclaro
**Base:** SPEC-935-R355 (EN), R356 (ZH) e R357 (edição trilíngue)

## 1. Objetivo

Polir as edições PT-BR, EN-US e ZH-CN de *Molambudos — O Diário do Paciente
1.260* para que pontuação, aspas, datas e marcas metalinguísticas sejam naturais
na cultura de leitura de cada língua, sem alterar a arquitetura fragmentária,
as vozes narrativas, os IDs, as rotas ou o sentido literário.

O trabalho é uma revisão editorial interna. Não constitui validação externa da
qualidade das traduções.

## 2. Escopo

1. Fragmentos em `fragmentos/`, `en/fragmentos/` e `zh/fragmentos/`.
2. Normalização tipográfica de aspas em PT-BR e EN-US.
3. Normalização de aspas chinesas “ ” e correção do falso trema `\"a\"` em ZH.
4. Correção cirúrgica de pares ausentes, invertidos ou semanticamente deslocados.
5. Datas documentais ajustadas à convenção cultural de cada edição, preservando
   a data histórica pretendida.
6. Verificação dos cinco artefatos: PT, EN, ZH, trilíngue e KDP trilíngue.

Ficam fora de escopo reescritas extensas, alteração de enredo, renomeação de
fragmentos, mudança de glossário fixado ou adaptação de números diegéticos.

## 3. Decisões editoriais

1. **PT-BR:** aspas curvas “ ”; datas numéricas em `dd/mm/aaaa`.
2. **EN-US:** aspas curvas “ ”; pontuação e datas conforme contexto editorial
   estadunidense, sem converter IDs ou o número diegético `1,260`.
3. **ZH-CN:** aspas chinesas “ ” em XeLaTeX; datas narrativas no padrão chinês
   quando já textualizadas, sem alterar IDs e números fixados em R356.
4. Aspas dentro de itálico permanecem dentro do escopo de `\textit{...}` quando
   isso preserva o desenho tipográfico do original.
5. Correções automáticas só são aceitas com revisão dos casos de aspas ímpares,
   grupos TeX aninhados e falas interrompidas por verbos dicendi.
6. Nenhuma correção pode reabrir o defeito de escopo TeX que deslocava labels e
   páginas das rotas.

## 4. Critérios de aceitação (gate SDD)

1. Teste R358 cobre, no mínimo:
   - ausência de aspas duplas retas não escapadas no corpus PT/EN;
   - pares tipográficos completos nos casos MEM-19, MEM-26 e DOC-12;
   - ausência de `\"a\"` em DOC-21 e presença de `“a”` na edição ZH;
   - fala de DOC-25 ZH semanticamente separada em `“奇怪。”` e
     `“我开一些检查。只是为了保险。”`;
   - balanço TeX dos 234 fragmentos;
   - datas PT documentais no padrão brasileiro.
2. Todos os testes R358 passam após ciclo RED → GREEN → REFACTOR.
3. `tri/main_tri.tex` compila com XeLaTeX em duas passadas: exit 0, sem erro
   fatal, referências indefinidas ou caracteres ausentes.
4. `main.tex` e `en/main_en.tex` compilam com pdfLaTeX; `zh/main_zh.tex` e
   `tri/main_kdp_print_160x230mm.tex` compilam com XeLaTeX.
5. Os cinco PDFs preservam suas contagens esperadas sem perda de seções ou
   fragmentos; variação de paginação decorrente apenas da tipografia é
   registrada, não ocultada.
6. As 462 referências de rota do volume trilíngue apresentam zero divergência
   entre label esperado e página resolvida.
7. Extração textual do PDF confirma os trechos:
   - `“Quem ler isto: você é o próximo.`;
   - `“Mas por que ela veio?”`;
   - `“Perguntei: ‘Como você sabe?’”` (ou glifo equivalente da fonte);
   - ZH sem `ä`/trema no trecho do `a` aberto;
   - DOC-25 ZH com duas falas corretamente delimitadas.
8. Nenhum comando, label, ID de fragmento, rota, número diegético ou decisão de
   glossário é alterado incidentalmente.
9. O ciclo R358 registra evidências, limitações e lições no EvolutionRegistry e
   no MetaBus, sem alegação de validação externa.

## 5. Estratégia TDD

1. **RED:** criar `tests/test_r358_molambudos_polimento_cultural.py` com casos
   conhecidos ainda quebrados no estado de trabalho.
2. **GREEN:** aplicar somente correções necessárias aos fragmentos.
3. **REFACTOR:** remover duplicações e padronizar comandos sem mudar o sentido.
4. Executar testes direcionados, compilação integral, auditoria de logs,
   extração textual e validação das rotas.

## 6. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Conversor inverter abertura/fechamento | Testes por caso + inspeção do PDF |
| Grupo TeX atravessar arquivos e deslocar labels | Balanço por fragmento + 462 rotas |
| “Correção” mudar a semântica da fala | Cotejo PT/EN/ZH nos casos ambíguos |
| Unicode CJK gerar caractere ausente | XeLaTeX + auditoria de missing chars |
| Alterações alheias no worktree | Escopo restrito aos arquivos R358 |

## 7. Evidências esperadas

- saída de `pytest` direcionado;
- logs das duas passadas dos cinco builds;
- relatório de balanço de chaves e aspas;
- relatório das 462 rotas;
- trechos extraídos dos PDFs;
- registro R358 no EvolutionRegistry e reflexão no MetaBus.
