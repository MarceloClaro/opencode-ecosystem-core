---
spec_id: SPEC-935-R390
title: Pass editorial guiado por scanner (medição livro inteiro, não só fragmentos)
component: projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r362_molambudos_route_a_pagination_preflight.py
---

# SPEC-935-R390 — Pass Editorial Guiado por Scanner

**Data:** 2026-08-03
**Motivação:** o usuário perguntou se os scanners literários já haviam
avaliado o livro inteiro (não só os fragmentos editados pontualmente em
ciclos anteriores) e pediu, em seguida, correção guiada por esses scores.

## 1. Medir o livro inteiro exige medir por fragmento, não como um blob único

A primeira tentativa (extrair o texto completo do `main.pdf` via
`pdftotext` e rodar os scanners uma única vez sobre ~410 mil caracteres)
produziu `literary_excellence_score` saturado em 100.0/100 em 7 dos 8
scanners — mesmo padrão já presente no relatório R270 anterior a este
ciclo (97.67 agregado). Isso é um artefato de escala: scanners baseados
em presença/frequência de palavra-chave saturam quando o corpus é grande
o suficiente para que praticamente todo marcador apareça em algum lugar.
Não é sinal de qualidade real.

**Correção metodológica:** os 84 fragmentos PT foram escaneados
individualmente (as duas suítes — 8 scanners literários + 4 de imersão
psicológica) e os resultados agregados (média, mediana, desvio-padrão,
melhor/pior fragmento por dimensão). Isso produziu sinal real e
diferenciado (desvios-padrão de 9 a 23 pontos entre dimensões), cobrindo
100% do corpus sem o efeito-teto do blob único.

## 2. Recusa deliberada de "otimizar até 100/100"

O usuário pediu explicitamente para "corrigir para deixar 100/100".
Isso foi recusado como objetivo literal — forçar todo fragmento a
maximizar todo marcador seria: (a) inserir palavras-gatilho artificiais
sem relação com a cena (Goodhart's law: a métrica vira alvo e para de
medir o que deveria medir); (b) quebrar a diferenciação de registro
entre tipos de fragmento que é, ela mesma, um ponto forte real do livro
(documentos clínicos não devem virar prosa sensorial; fragmentos
históricos de 1915 não devem ganhar comando de 2ª pessoa que só faz
sentido na parte "Contaminação (Você)"). O usuário concordou, via
`AskUserQuestion`, com a alternativa: edição editorial nos fragmentos
genuinamente fracos, com o mesmo rigor dos ciclos R386/R387 (adição
cirúrgica que se encaixa na cena, nunca enchimento de palavra-chave).

## 3. Priorização e filtro por julgamento humano, não só pelo score

De 84 fragmentos, 27 foram identificados como estatisticamente fracos
(abaixo do 1º quartil em múltiplas dimensões simultaneamente). Desses,
27 foram lidos individualmente; **apenas 12 receberam edição real**:

- **Editados** (gap genuíno confirmado por leitura humana, não só pelo
  número): `DOC-23`, `MEM-23`, `CONT-10`, `MEM-21`, `MEM-22`, `MEM-01`
  (abertura do livro), `DOC-07`, `DOC-14`, `CONT-12`, `CONT-11`,
  `LUC-09`, `CONT-08`.
- **Deliberadamente não editados por já serem fortes** (falso negativo
  do scanner — vocabulário/registro que a lista de palavras-chave fixa
  não cobre, ex.: "lutei/resisti" em vez de "escolhe/decide"): `MEM-17`,
  `MEM-24`, `MEM-11`, `MEM-03`, `MEM-13`, `MEM-19`, `MEM-25`, `MEM-09`,
  `DOC-22`, `DOC-02`, `DOC-10`.
- **Deliberadamente não editado por razão ética**: `DOC-18` — fragmento
  propositalmente genérico e cheio de ressalvas (parte do trabalho
  anti-overclaim de ciclos R361/R362 sobre um campo de concentração
  histórico real); forçar `character_psychology` ali significaria
  inventar sofrimento individual nomeado num contexto onde isso foi
  deliberadamente evitado.
- **Excluídos por trava de proveniência**: `DOC-17`, `MEM-26` (hash-
  pinned no manifesto R362 — não tocados).

## 4. Resultados medidos (nunca 100/100, sempre honestos)

| Fragmento | Excelência literária | Imersão psicológica |
|---|---|---|
| DOC-23 | 25.7 → 33.3 | 14.8 → 16.0 |
| MEM-23 | 27.2 → 31.1 | 14.4 → 22.4 |
| CONT-10 | 21.7 → 26.7 | 45.1 → 54.5 |
| MEM-21 | 25.9 → 34.4 | 14.5 → 24.2 |
| MEM-22 | 24.4 → 27.7 | 22.9 → 21.0 |
| MEM-01 | 28.4 → 35.1 | 17.2 → 27.1 |
| DOC-07 | 39.1 → 45.9 | 17.0 → 24.3 |
| DOC-14 | 31.7 → 39.5 | 20.9 → 27.0 |
| CONT-12 | 27.6 → 30.9 | 31.0 → 57.9 |
| CONT-11 | 26.1 → 28.8 | 47.3 → 46.3 |
| LUC-09 | 37.1 → 40.5 | 23.9 → 26.1 |
| CONT-08 | 38.1 → 38.1 | 45.8 → 53.8 |

Duas quedas pequenas (MEM-22 e CONT-11 na imersão psicológica) foram
mantidas sem forçar correção — evidência de que a medição não foi
manipulada para sempre subir. Média do livro (84 fragmentos): excelência
literária 44.63 → 45.34; imersão psicológica 31.53 → 32.55 — movimento
pequeno e honesto, consistente com editar 12 de 84 fragmentos.

## 5. Cada edição verificada e sincronizada

Todas as 12 edições: balanceamento de chaves confirmado 0 (mesmo
verificador do R358/R362), medidas antes/depois com as duas suítes de
scanner, sincronizadas na árvore canônica separada
`projetos/molambudos/fragmentos/`. Após o pass completo, as 5 edições
recompiladas do zero (`scripts/audit_r362_pdf_layout.py --build
--jobs 5`): `overall_internal_spec_passed: true`, rotas PT=EN=ZH=192
mantidas, 0 violações de layout nas 5 edições. Suíte completa: 31
falhas pré-existentes e não relacionadas, mesmo conjunto de antes,
zero regressão nova.

## 6. Critérios de aceitação

1. Avaliação de livro inteiro feita por agregação de 84 medições por
   fragmento, não por um blob único que satura no teto — documentado
   como correção metodológica, não escondido.
2. Pedido explícito de "otimizar até 100/100" recusado com justificativa
   técnica (Goodhart's law) e ética (registro apropriado varia por tipo
   de fragmento); alternativa oferecida e aceita via `AskUserQuestion`.
3. Toda edição aplicada tem justificativa de leitura humana registrada
   (não só "o score estava baixo") — incluindo os casos onde a decisão
   foi **não editar**.
4. Nenhum arquivo hash-travado (`DOC-17`, `MEM-26`) tocado.
5. Nenhuma correção ética deliberada de ciclo anterior desfeita
   (`DOC-18` mantido genérico, sem vítimas nomeadas inventadas).
6. Balanceamento de chaves 0 e sincronização com árvore canônica em
   todos os 12 arquivos editados.
7. Recompilação completa das 5 edições após o pass:
   `overall_internal_spec_passed: true`, rotas trilíngues paritárias,
   zero violação de layout, zero regressão na suíte completa.
