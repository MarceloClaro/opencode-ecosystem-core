---
spec_id: SPEC-935-R387
title: Segunda leva de aprimoramento cirúrgico de prosa (CONT-10, CONT-11, CONT-13)
component: projetos/molambudos (fragmentos CONT-10/CONT-11/CONT-13)
status: verified
test_file: tests/test_r385_psychological_immersion_scanners.py
---

# SPEC-935-R387 — Segunda Leva de Aprimoramento de Prosa

**Data:** 2026-08-03
**Motivação:** continuação do R386 a pedido do usuário ("prossiga").
Estende as mesmas 3 técnicas (cruzamento sensorial, interocepção
corporal, comando direto de 2ª pessoa) para mais 3 fragmentos `CONT-*`
ainda não tocados, escolhidos por serem curtos e terem baixa densidade
sensorial/interoceptiva na varredura R385 — maior retorno por edição.

## 1. Verificação prévia (mesma disciplina do R386)

Confirmado programaticamente antes de editar: nenhum dos 3 fragmentos
alvo (`CONT-10`, `CONT-11`, `CONT-13`) está travado por hash em
`molambudos_r360_reviews.json`, `molambudos_r361_provenance_drift.json`
ou `molambudos_r362_change_manifest.json`. Backup manual adicionado a
`Molambudos_VictoriaRegia/_archive/backup_R386_prosa_edits/` (mesmo
diretório do R386, já que é a mesma frente de trabalho).

## 2. Edições aplicadas

- **CONT-10** ("A Ferida"): "Sinta: seu coração bate mais forte bem
  naquele ponto da pele, como se a mancha tivesse pulso próprio."
  (cruzamento tátil+interoceptivo) e "Olhe de novo." (comando direto,
  antes do clímax do fragmento).
- **CONT-11** ("O Número"): "E, no mesmo instante, seu coração vai pular
  uma batida." + "Sinta agora. Já pulou." (interocepção + comando
  direto, no ponto de maior repetição obsessiva do fragmento).
- **CONT-13** ("A Fila"): "Sinta o peso dela na palma da mão. Frio
  primeiro. Depois quente --- quente demais, como se já tivesse sido
  segurada por muitas mãos antes da sua." (cruzamento tátil+térmico+
  interoceptivo, ancorado na metáfora já existente da "chave").

## 3. Medido, não estimado

| Fragmento | sensory_immersion | hypnotic_induction | psychological_manipulation | Agregado |
|---|---|---|---|---|
| CONT-10 | 35.9 → 67.38 | 31.25 → 56.25 | 0.0 → 25.0 | 24.86 → 45.12 |
| CONT-11 | 7.96 → 50.22 | 31.25 → 56.25 | 0.0 → 25.0 | 21.43 → 47.36 |
| CONT-13 | 9.39 → 18.62 | 50.0 → 74.09 | 25.0 → 25.0 | 33.67 → 43.31 |

`frenetic_pacing` não caiu desta vez (ao contrário do CONT-01 no R386) —
as adições foram mais curtas/pontuais, sem diluir a fragmentação
visceral do fragmento.

## 4. Nota metodológica descoberta durante a medição (transparente)

Ao tentar medir o efeito agregado no "livro inteiro", descobri que
`molambudos.md` (fonte markdown) e o corpus `.tex` real de
`Molambudos_VictoriaRegia/fragmentos/` **divergem** — minhas edições
foram aplicadas diretamente aos `.tex` (seguindo o precedente já
existente de notas editoriais e do parágrafo da "quarta opção",
achados no R384, que só existem no `.tex`), não ao `.md`. Rodar os
scanners sobre `molambudos.md` não reflete essas edições. Rodando sobre
o corpus `.tex` real (452.187 caracteres, 84 arquivos — mais fragmentos
que os 73 do R270 porque inclui `frontmatter/` e outros): imersão
psicológica agregada **51.93/100** (vs. 60.28 medido sobre o `.md` antes
das edições desta leva — os dois números não são diretamente
comparáveis por serem corpora diferentes, com ruído de marcação LaTeX
diluindo densidade de palavras-chave no `.tex`). **Não fabrico um
número único "antes/depois do livro inteiro"** porque isso exigiria
escolher um corpus consistente primeiro — o sinal confiável desta spec
é o comparativo por fragmento (Seção 3), medido sobre o mesmo tipo de
arquivo antes e depois.

## 5. Critérios de aceitação

1. 3 fragmentos editados, cada um com melhoria mensurável em pelo menos
   2 das 4 dimensões da suíte de imersão psicológica.
2. Zero palavra removida do texto original (só adições).
3. Nenhuma cadeia de proveniência (R360/R361/R362) quebrada — verificado
   programaticamente após as edições.
4. Zero regressão em `tests/test_r385_psychological_immersion_scanners.py`
   (18/18) e no conjunto de testes Molambudos (as 2 falhas do
   `test_r358` são pré-existentes, sobre contagem de fragmentos, não
   relacionadas).
