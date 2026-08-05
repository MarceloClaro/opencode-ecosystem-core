---
spec_id: SPEC-935-R400
title: Molambudos — todas as rotas levam ao Epílogo, nenhum ciclo aprisiona, nenhum fragmento fica fora da rede
component: projetos/molambudos/Molambudos_VictoriaRegia, scripts/molambudos_grafo_rotas.py
status: verified
test_file: tests/test_r397_molambudos_coerencia_diegetica.py
---

# SPEC-935-R400 — Convergência da Rede de Rotas

**Data:** 2026-08-04
**Motivação:** o autor declarou a regra de arquitetura narrativa — *"todas as
rotas levam para o epílogo"*, *"sem loop e sem loops infinitos"* — e, em
seguida, *"não quero nenhum aberto, corrija todos, devem estar contidos na rota
com coesão e coerência e sequência lógica da narração"*.

## 1. O Epílogo era inalcançável

`\fragdef{Epilogo}` existia como âncora, última entrada da ordem linear, mas
**nenhuma rota apontava para ele em nenhum dos três idiomas**. O grafo de
leitura tinha um sorvedouro de 48 fragmentos: quem seguia as setas circulava
ali indefinidamente e nunca chegava ao fim da obra.

### 1.1 A escolha que foi ao autor, não decidida sozinho

Havia dois caminhos, com resultados muito diferentes:

| | Grafo acíclico estrito | Garantir saída sempre |
|---|---|---|
| Rotas | 192 → 107 (**−85, −44%**) | 192 mantidas + novas |
| Ciclos | zero | preservados |
| Custo | perde as remissões documento→memória que dão à obra o caráter de arquivo | nenhum |

As 85 rotas que apontam para trás na ordem linear são justamente as remissões
cruzadas do arquivo. Além disso, a obra afirma *"O ciclo recomeça"* como tese —
um grafo sem ciclos contradiria o próprio texto. **Decisão do autor: garantir
saída sempre.**

### 1.2 Implementação

O Epílogo recebeu o ID **`EPI-01`**, que casa com
`FRAGMENT_ID_PATTERN` de `scripts/validate_molambudos_routes.py` — assim o
preflight passa a validá-lo como qualquer outro destino, em vez de ele ficar
invisível ao auditor.

Dez fragmentos terminais ganharam `\rota{EPI-01}`: os oito sorvedouros da
ordem-frente (DOC-10, DOC-19, LUC-13, LUC-14, CONT-07, CONT-09, CONT-13,
MEM-27) mais os fechos temáticos **LUC-12** (Lúcia encerra seu ciclo) e
**DOC-27** (fecha o dossiê documental).

### 1.3 A armadilha da edição trilíngue

Renomear `\fragdef{Epilogo}` → `\fragdef{EPI-01}` nos três `main*.tex` de
idioma **não bastou**: `tri/main_tri.tex` ficou para trás. A edição trilíngue
ancora cada fragmento sob três prefixos (`frag:`, `fragen:`, `fragzh:`) via
`\tribody`, e o Epílogo tinha apenas `\fragdef{Epilogo}`. Resultado: as rotas
`\rota{EPI-01}` das versões EN e ZH não resolviam — o preflight acusou
**618/648**, exatamente 30 faltantes (10 por idioma). Corrigido ancorando o
Epílogo nas três variantes. Foi o preflight que pegou, não a revisão manual.

## 2. Nenhum fragmento fora da rede

Catorze fragmentos não tinham **nenhuma rota de entrada** — DOC-17, DOC-20 a
DOC-27, LUC-13, LUC-14, MEM-18, MEM-21 e MEM-27. O bloco DOC-20→DOC-26 (sete
documentos do dossiê de 2026) estava órfão **inteiro**. Num livro que oferece
três modos de leitura, um deles — a navegação livre — simplesmente não
entregava esse conteúdo. (Verificado contra o backup pré-R397: condição
anterior a esta sessão, não introduzida por ela.)

Os enlaces foram escolhidos pela **motivação narrativa**, não para fechar o
grafo:

| Enlace | Justificativa |
|---|---|
| MEM-07 → DOC-17 | a memória do curral → o mesmo curral visto de dentro, na voz do soldado |
| LUC-02 → DOC-20 | Lúcia recebe o diário no arquivo → a cadeia de custódia com lacunas |
| DOC-16 → DOC-21 | Oliveira se identifica como 1.261 → sua carta nunca enviada |
| DOC-21 → DOC-22 | a carta → o memorando institucional de 2026 |
| DOC-22 → DOC-23 | o memorando → a ocorrência registrada no arquivo |
| DOC-23 → DOC-24 | a ocorrência → o parecer de conservação do objeto |
| DOC-24 → DOC-25 | o parecer → a identificação do homem do pano preto |
| DOC-25 → DOC-26 | identificado Oliveira → as anotações dele sobre o mecanismo |
| DOC-26 → DOC-27 | *"o que o diário faz com o tempo"* → a origem, 1853 |
| LUC-12 → LUC-13 | o desaparecimento → a gravação da noite do diagnóstico |
| LUC-13 → LUC-14 | a noite → a autoavaliação clínica que a encerra |
| MEM-17 → MEM-18 | o cárcere → a tentativa de fuga de 1943 |
| MEM-18 → MEM-21 | a fuga fracassada de 1943 → o jornal que mentia, 1948: falhada a fuga, o jornal é a única janela para fora |
| CONT-13 → MEM-27 | *A Fila* → *A Última Página* |

**Enlace realocado por proveniência:** a primeira escolha para MEM-21 era
`MEM-12 → MEM-21`, mas `MEM-12` está sob cadeia de proveniência de tradução
do R360 (review `r360-rasga_mortalha`, EN e ZH). Alterar sua linha de
navegação quebrou os testes `test_r360_provenance_points_to_immutable_corpus_snapshot`
e `test_cadeias_r360_r361_r362_resolvem_sem_problema`. A correção **não** foi
reescrever o registro de proveniência — foi mover a origem do enlace para
`MEM-18`, que é livre e produz um encadeamento narrativo melhor. Mesma
disciplina do R398 §4: registro selado de outro ciclo não se reescreve para
acomodar mudança nova.

A cadeia DOC-21→DOC-27 reproduz a sequência lógica do dossiê forense de 2026,
que já era a ordem linear do autor — o hipertexto passa a oferecê-la também
como percurso navegável.

## 3. Estado final da rede

| Propriedade | Antes | Depois |
|---|---|---|
| Fragmentos sem rota de entrada | 14 | **0** |
| Fragmentos que alcançam o Epílogo | 0 | **84 / 84** |
| Rotas que chegam ao Epílogo | 0 | 10 |
| Rotas que saem do Epílogo | — | **0** (sorvedouro) |
| Ciclos | 6 | 6 (maior: 58 fragmentos) |
| Ciclos sem saída (aprisionam o leitor) | — | **0** |
| Rotas quebradas | 0 | 0 |
| Rotas totais | 192 | **216** |
| Destinos distintos | 70 | **85** (84 fragmentos + Epílogo) |

O protocolo passou a declarar 216 rotas nos três idiomas e a registrar a
promessa: *"Nenhum caminho é um beco: de qualquer fragmento existe percurso
até o Epílogo."*

## 4. Guardas

Quatro testes novos em `tests/test_r397_molambudos_coerencia_diegetica.py`,
parametrizados nos três idiomas:

1. `test_o_epilogo_e_alcancavel_de_todos_os_fragmentos`
2. `test_o_epilogo_recebe_rotas_e_nao_emite_nenhuma`
3. `test_nenhum_ciclo_aprisiona_o_leitor` — componentes fortemente conexos sem
   aresta de saída
4. `test_nenhum_fragmento_fica_fora_da_rede_de_rotas`

`scripts/molambudos_grafo_rotas.py` passou a conhecer o Epílogo como nó
legítimo (ele não tem arquivo — é capítulo inline) e a medir convergência,
ciclos aprisionantes e órfãos, além de desenhar o grafo.

## 5. Critérios de aceitação

1. O Epílogo é alcançável a partir dos 84 fragmentos, nos três idiomas. ✔
2. O Epílogo recebe rotas e não emite nenhuma. ✔
3. Nenhum ciclo existe sem aresta de saída — o leitor nunca fica preso. ✔
4. Nenhum fragmento fica sem rota de entrada. ✔
5. Os ciclos temáticos foram preservados (decisão do autor). ✔
6. Preflight R362 com `--build`: `overall_internal_spec_passed=True`,
   **648/648 rotas**, `source_multiset_match=True` nas cinco edições, zero
   violações de layout. ✔
7. Cada enlace novo tem justificativa narrativa registrada, não é fiação
   arbitrária para fechar o grafo. ✔
