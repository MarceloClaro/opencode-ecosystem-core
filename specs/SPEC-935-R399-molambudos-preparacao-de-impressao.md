---
spec_id: SPEC-935-R399
title: Molambudos — preparação de impressão: miolo PT 160×230mm, capa derivada da paginação real e selo de integridade verificável
component: projetos/molambudos/Molambudos_VictoriaRegia, scripts/molambudos_selo.py
status: verified
test_file: tests/test_r399_molambudos_selo_e_capa.py
---

# SPEC-935-R399 — Preparação de Impressão

**Data:** 2026-08-04
**Motivação:** perguntado se a obra estava pronta para publicação, o
diagnóstico foi **não**, com três bloqueios concretos. Este ciclo resolve dois
deles e delimita o terceiro.

## 1. A capa não podia ser impressa com nenhum miolo existente

| | Capa entregue | Miolos existentes |
|---|---|---|
| Formato dos painéis | 157,4 × 234,6 mm | 160 × 230 mm |
| Lombada | 1,404 in ≈ **623 páginas** | 415 (PT digital) / 1115 (trilíngue) |

O template arquivado revela a origem:
`_archive/CASE_LAMINATE_6.000x9.000_471_PREMIUM_WHITE_en_US.png` — a capa foi
projetada para **capa dura 6×9 in com 471 páginas**. Três contagens
diferentes, nenhuma correspondendo ao miolo. A KDP recusa automaticamente capa
cuja lombada não corresponda à paginação.

### 1.1 A capa entregue nunca renderizou

`capa_completa.pdf` (6,4 MB, de 30/jul) renderiza **um retângulo escuro com uma
tira de conteúdo no topo**. A causa: `tikzpicture` com `overlay` cujas
coordenadas partem do ponto de texto corrente, não do canto da página — todo o
conteúdo é empurrado para fora. O arquivo tem as imagens embutidas (daí os 6,4
MB), apenas posicionadas fora da área impressa. O defeito estava lá desde
julho, sem nenhuma guarda que o detectasse.

### 1.2 Miolo PT de impressão

`main_kdp_print_160x230mm.tex` na raiz e `tri/main_kdp_print_160x230mm.tex`
produzem o **mesmo basename** e colidem na saída — o PDF na raiz era, na
prática, o build trilíngue (1115 páginas, com texto chinês). Criado
`main_kdp_pt_160x230mm.tex`, com jobname próprio:

- **433 páginas**, trim medido **160,0 × 230,0 mm**, conteúdo em português.

### 1.3 Capa nova, com geometria derivada

`capa_completa_pt_160x230mm.tex` — **brochura**, não capa dura: a KDP não
oferece 160×230 mm em capa dura (o trim mais próximo é 6,14×9,21 in ≈
156×234 mm, que é justamente o da capa antiga); em brochura o trim
personalizado é aceito.

Toda a geometria é derivada de cinco parâmetros no topo do arquivo
(`\TrimLargura`, `\TrimAltura`, `\Paginas`, `\EspessuraPapel`, `\Sangria`).
Nenhum número está fixo no corpo — mudar a paginação é uma linha.

Lombada calculada: **433 × 0,002347 = 1,0163 in = 25,81 mm**. A constante é a
da impressão **em cor** da KDP, e não é chute: verificou-se que todas as
páginas amostradas do miolo têm preenchimento sépia `#F2E8CF`, ou seja, o
miolo é colorido de ponta a ponta.

Capa final: **13,866 × 9,305 in (352,2 × 236,3 mm)**.

Confirmação de que 160×230 mm é o formato certo para esta arte: os PNGs de
capa e contracapa têm proporção **0,6955**; o painel de 160×230 mm tem
**0,6957**. O painel de capa dura antigo (0,6710) é que distorcia a arte.

### 1.4 Dois defeitos da arte, encontrados e sinalizados

1. **Resolução insuficiente.** `capa.png` e `contracapa.png` têm 1046×1504 px,
   o que dá **163 DPI** no painel impresso. A KDP pede 300 DPI. Seriam
   necessários ~1927×2792 px (ampliação de 1,84×). **Não corrigido** —
   ampliar por interpolação não cria detalhe; a arte precisa ser regerada na
   resolução final.
2. **Código de barras fictício embutido.** `contracapa.png` traz um código de
   barras impresso com ISBN **978-65-01-23456-7** — número de teste, diferente
   do ISBN real da obra (`9798189170492`). Está dentro do PNG, fora do alcance
   do LaTeX. A reserva branca do código de barras foi dimensionada e
   posicionada para **cobri-lo**, o que também atende à exigência da KDP de
   deixar a área livre. A solução definitiva é remover o elemento da arte de
   origem.

`capa_completa.tex` (capa dura) e `lombada.tex` foram **preservados intactos** —
são outro projeto, para outro formato. Nada foi perdido.

## 2. O selo de integridade não provava nada

`SELO_INTEGRIDADE_MERKLE.json` declarava **74 fragmentos** (o corpus tem 84),
**359 páginas**, e nenhum dos seus hashes conferia. Pior: `grep -rl
SELO_INTEGRIDADE_MERKLE tests/ scripts/ marceloclaro/ integrations/` não
retornava nada — **ninguém o gerava e ninguém o conferia**. Era um artefato de
aparência criptográfica sem função.

Novo `scripts/molambudos_selo.py`:

```
python3 -m scripts.molambudos_selo gerar      # recalcula e grava
python3 -m scripts.molambudos_selo verificar  # confere; sai != 0 se divergir
```

Mudanças de conteúdo em relação ao selo antigo:

- **Algoritmo documentado no próprio JSON** (`merkle-sha256-v1`): folha =
  `sha256(caminho_relativo + '\0' + bytes)`, fragmentos ordenados por caminho,
  nível interno = `sha256(esq + dir)`, nó ímpar promovido. O root anterior não
  era reproduzível porque o algoritmo nunca foi registrado — o novo root é
  **recalculado sob algoritmo declarado**, não uma tentativa de reproduzir o
  antigo.
- **Campo `escopo`** afirmando explicitamente o que o selo *não* atesta:
  não é validação externa, parecer editorial, revisão por pares nem atestado
  de qualidade.
- Passou a registrar a paginação dos dois miolos e o hash da capa de impressão.

Estado atual: 84 fragmentos, root
`7815a4234cb98ca821783b2d006f3aa9db3fd29f3df9a3b4e9d112dfe48ed53a`.

### 2.1 Defeito no próprio guarda, encontrado pela suíte

A primeira versão comparava também os hashes dos PDFs. Mas o `pdflatex` embute
`/CreationDate`, `/ModDate` e um `/ID` derivado deles: **dois builds da mesma
fonte produzem bytes diferentes**. O selo passaria a divergir a cada
recompilação, sem que nada de conteúdo tivesse mudado — ruído que treina
qualquer pessoa a ignorar o alarme, que é como um guarda morre.

Corrigido: os hashes de PDF continuam **registrados** (impressão digital do
build enviado à gráfica) mas ficam **fora da comparação**. A verificação cobre
o que vem da fonte: fragmentos, frontmatter, `main.tex` e contagens. O campo
`escopo` do JSON declara essa distinção.

### 2.2 O guarda foi provado, não apenas escrito

Três cenários verificados na prática:

| Cenário | Esperado | Resultado |
|---|---|---|
| Recompilar o PDF sem tocar na fonte | não acusa | não acusou |
| Anexar uma linha a `MEM-01.tex` | acusa, apontando o fragmento | acusou, com o merkle root novo e o nome do arquivo |
| Restaurar o arquivo | volta ao verde | voltou |

Um selo que não falha quando o corpus muda seria o mesmo teatro de antes com
mais linhas de código; um que falha a cada rebuild seria pior, porque ensina a
ignorá-lo.

## 3. O mapa de grafo das rotas estava defasado e ninguém o gerava

Os três PNGs em `misc/` (`grafo_narrativo`, `grafo_enredo`,
`grafo_leitura_linear`) datavam de 30/07/2026 e **nenhum script os produzia** —
`grep -rl grafo_narrativo --include=*.py` não retornava nada. Ficaram
defasados da expansão CONT, da conversão das linhas de navegação para
`\rota{}` (R389) e da deduplicação de DOC-24/25/27 (R398). Num livro que se
vende como hipertexto impresso, um mapa desatualizado engana o leitor
exatamente onde ele mais precisa de precisão.

Novo `scripts/molambudos_grafo_rotas.py`, que lê as chamadas `\rota{}` reais:

```
python3 -m scripts.molambudos_grafo_rotas          # regenera o PNG
python3 -m scripts.molambudos_grafo_rotas --stats  # só as métricas
```

`misc/grafo_narrativo.png` regerado (4400×3200 px), com fundo sépia do miolo,
cores por família de fragmento e tamanho de nó proporcional às rotas de
entrada.

### 3.1 O que o grafo revelou sobre a navegação

| Métrica | Valor |
|---|---|
| Fragmentos | 84 |
| Rotas | 192 |
| Componentes fracamente conexos | **1** (sem ilhas) |
| Rotas apontando para fragmento inexistente | **0** |
| Fragmentos sem rota de saída (beco) | **0** |
| Fragmentos sem rota de entrada | **14** |

Hub dominante: **DOC-01 com 20 rotas de entrada**, seguido de LUC-02 (12) e
CONT-07 (10).

Os 14 sem rota de entrada — DOC-17, DOC-20 a DOC-27, LUC-13, LUC-14, MEM-18,
MEM-21, MEM-27 — são **inalcançáveis pela "Rota Hipertextual (Navegação
Livre)"** que o protocolo oferece: o leitor que navega por saltos nunca chega
a eles, só os encontra na leitura linear. **Verificado que a condição é
anterior a esta sessão** (comparação com o backup pré-R397 dá exatamente os
mesmos 14): não foi introduzida pela deduplicação nem pelas correções de
rota. Fica registrada, não corrigida — decidir quais fragmentos devem
referenciá-los é decisão de arquitetura narrativa, não mecânica.

## 4. O bloqueio que permanece

**As três edições ainda não são o mesmo livro** — 10 fragmentos divergem
estruturalmente além do idioma (CONT-05: PT/EN 163 linhas, ZH 63; CONT-03:
PT 174, EN/ZH 102; CONT-12: ZH 101, EN 47; DOC-26: PT/EN 110, ZH 56). Na
edição trilíngue as três colunas ficam lado a lado e a divergência é visível
ao leitor. Escolher a versão canônica de cada caso é decisão autoral e de
tradução — fora do alcance mecânico deste ciclo, e o principal obstáculo
restante à alegação de obra de referência internacional.

## 5. Critérios de aceitação

1. Existe um miolo PT de impressão com trim medido de 160×230 mm. ✔
2. A lombada da capa é derivada da paginação real do miolo, e o teste falha se
   as duas divergirem. ✔
3. A capa renderiza conteúdo dentro da página (teste que rejeita a página
   uniforme do defeito anterior). ✔
4. O selo é gerado e conferido por script, e o teste falha quando um fragmento
   muda sem regeneração — **verificado na prática**. ✔
5. O selo declara seu próprio algoritmo e o que não atesta. ✔
6. Os projetos de capa dura preexistentes seguem intactos. ✔
7. Os defeitos da arte que exigem regeneração externa (163 DPI; ISBN fictício
   embutido) ficam documentados, não apresentados como resolvidos. ✔
8. A divergência trilíngue permanece registrada como bloqueio autoral. ✔
9. O mapa de grafo das rotas é gerado por script a partir dos fragmentos
   reais, e não mais um PNG estático sem origem reproduzível. ✔
10. Os 14 fragmentos inalcançáveis por navegação livre ficam medidos e
    atribuídos à condição anterior a esta sessão, não corrigidos em silêncio. ✔
