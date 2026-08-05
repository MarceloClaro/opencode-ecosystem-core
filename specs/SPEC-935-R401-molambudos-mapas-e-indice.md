---
spec_id: SPEC-935-R401
title: Molambudos — Mapas 2 e 3 gerados do corpus, Índice de Fragmentos completado e contagens do livro alinhadas
component: scripts/molambudos_grafo_rotas.py, projetos/molambudos/Molambudos_VictoriaRegia
status: verified
test_file: tests/test_r397_molambudos_coerencia_diegetica.py
---

# SPEC-935-R401 — Mapas 2 e 3, Índice e Contagens

**Data:** 2026-08-05
**Motivação:** *"faça o mesmo com os mapas de grafos 2 e 3"* — dar aos Mapas 2
(Arquitetura em Três Atos) e 3 (Percurso Linear) o mesmo tratamento que o
R399/R400 deram ao Mapa 1: gerá-los do corpus real, em vez de mantê-los como
PNGs estáticos sem origem reproduzível.

## 1. Os mapas

`scripts/molambudos_grafo_rotas.py` ganhou `--mapa {rotas,enredo,linear,todos}`
e passou a derivar a estrutura de partes do próprio `main.tex`
(`\partopener` + `\fragdef`), em vez de qualquer lista mantida à mão — que foi
exatamente como as legendas acabaram afirmando "78 fragmentos" muito depois de
o corpus ter passado de 78.

**Mapa 2 — Arquitetura em Três Atos.** Os atos agrupam as cinco partes:

| Ato | Partes | Fragmentos |
|---|---|---|
| ATO 1 — O Trauma | Sertão | 9 |
| ATO 2 — Institucionalização | Colônia + Diário de Oliveira e Laudos | 41 |
| ATO 3 — O Ciclo | Investigação Lúcia + Contaminação | 35 |

Cada faixa tem **altura proporcional ao conteúdo**: faixas iguais dariam ao
Ato 1 (9 fragmentos) o mesmo peso visual do Ato 2 (41), sugerindo um
equilíbrio que a obra não tem. As rotas internas ficam esmaecidas; as **55 que
atravessam atos** aparecem em vermelho, porque são elas que carregam a
estrutura causal — o trauma alimentando a institucionalização, esta
alimentando o ciclo.

**Mapa 3 — Percurso Linear.** As 85 entradas em serpentina, coloridas por
parte, com as transições entre partes em vermelho e o Epílogo em preto ao fim.

## 2. O Índice de Fragmentos estava incompleto

Ao conferir as contagens declaradas contra o que o índice de fato lista:

| Parte | Declarava | Listava | Real |
|---|---|---|---|
| Sertão | 9 | 9 | 9 |
| Colônia | 16 | 16 | 16 |
| Diário de Oliveira e Laudos | 26 | **18** | 25 |
| Investigação Lúcia | 21 | **17** | 20 |
| Contaminação | 13 | 13 | 14 + Epílogo |

**Onze fragmentos não constavam do índice**: DOC-20 a DOC-27, LUC-13, LUC-14 e
MEM-27.

São quase exatamente os mesmos que o R400 encontrou **sem rota de entrada**.
A coincidência conta a história: esse conteúdo entrou na obra em algum ciclo e
**não foi ligado a nenhum dos dois sistemas de navegação** — não estava no
índice e não era alcançável por saltos. Existia só para quem folheasse página
a página. Um leitor procurando "O Homem do Pano Preto" no índice não o
encontrava.

Os onze foram inseridos com os títulos reais lidos dos próprios arquivos, nas
posições que respeitam a ordem do corpo, e as contagens declaradas corrigidas.
Índice: **84/84**.

Corrigida de passagem uma entrada que ainda dizia "Escala de Avaliação
**1.261**" — resquício da contradição do número do paciente resolvida no R397.

## 3. Contagens do livro sobre si mesmo

Três números diferentes conviviam, nenhum correto:

| Onde | Dizia | Real |
|---|---|---|
| Cabeçalho dos 4 `main*.tex` | 78 fragmentos · 180 rotas | 84 · 216 |
| `\textit{Este arquivo contém…}` | 78 fragmentos | 84 |
| Legenda do Mapa 1 | 78 fragmentos · 180 conexões | 84 · 216 |
| Legenda do Mapa 2 | "sustenta os 78 fragmentos" | 84 |
| Legenda do Mapa 3 | 78 fragmentos | 84 |
| Comentário de código | "LEITURA LINEAR — 71 FRAGMENTOS" | 84 |
| Colofão | "Este livro contém 78 fragmentos" | 84 |

Também a lista de partes do Mapa 3 (`Diário de Oliveira (18)`,
`Investigação Lúcia (21)`) foi alinhada ao real (25, 20).

Quinze ocorrências corrigidas em `main.tex`, `en/main_en.tex`,
`zh/main_zh.tex` e `tri/main_tri.tex`.

## 4. Defeito de inclusão de imagem, encontrado pelo preflight

O Mapa 2 regerado ficou em formato paisagem (2:1). As inclusões usavam
`\includegraphics[height=0.85\textheight,keepaspectratio]` — **sem restrição
de largura**. Com apenas `height=`, `keepaspectratio` escala pela altura e
deixa a largura crescer livremente: a imagem estourou a página xxvii, gerando
4 violações de layout por edição (1 `image` fora da área de corte segura e 3
`drawing` fora do MediaBox — a moldura `\fbox`).

`tri/main_tri.tex` já usava o padrão correto (`width=0.96\textwidth` + `height`
+ `keepaspectratio`) no Mapa 1; as outras onze inclusões não. Todas as doze
foram alinhadas.

Foi o preflight que pegou, não a revisão visual — o PDF "parecia" bem numa
inspeção rápida.

## 5. Posição dos Mapas 2 e 3 igualada

O autor observou que *"a posição do mapa 2 deveria ser igual a posição do mapa
3, pois fica melhor para visualizar"*. O Mapa 2 era, de fato, o único dos três
sem `angle=90`.

Rotacioná-lo **não bastou**: sua proporção gerada era 2:1 contra 1,69:1 do
Mapa 3, de modo que, rotacionado, ficava *mais estreito* que ele — 214 pt
contra 253 pt de largura. Medido, não estimado.

Corrigido nos dois eixos: o Mapa 2 passou a ser gerado em 4400×2600 (mesma
proporção do Mapa 3), e a caixa de inclusão dos três subiu de
`0.96\textwidth × 0.85\textheight` para `0.98 × 0.90` — são grafos densos com
85 nós rotulados, e a 22% da área da página os rótulos ficavam ilegíveis.

| Mapa | Antes | Depois |
|---|---|---|
| 1 — Rotas | 312 × 428 pt (32%) | 330 × 454 pt (36%) |
| 2 — Três Atos | 214 × 428 pt (22%) | **268 × 454 pt (29%)** |
| 3 — Linear | 253 × 428 pt (26%) | **268 × 454 pt (29%)** |

Mapas 2 e 3 ficam com dimensões idênticas. O Mapa 1 permanece um pouco maior
por ter proporção própria: seu layout *force-directed* precisa de mais largura
para não empilhar os nós.

## 6. Critérios de aceitação

1. Os três mapas são gerados por script a partir do corpus real. ✔
2. A estrutura de partes é derivada de `main.tex`, não de lista mantida à mão. ✔
3. O Índice de Fragmentos lista 84 de 84. ✔
4. As contagens declaradas de cada parte batem com o que o índice lista e com
   o corpo. ✔
5. Nenhuma ocorrência de "78 fragmentos", "180 rotas" ou "71 FRAGMENTOS"
   sobrevive em nenhuma das quatro edições. ✔
6. Preflight R362 com `--build`: `overall_internal_spec_passed=True`,
   648/648 rotas, **zero violações de layout** nas cinco edições. ✔
7. Mapas 2 e 3 ocupam área e posição idênticas na página. ✔
