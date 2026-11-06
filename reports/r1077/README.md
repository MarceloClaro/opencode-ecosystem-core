# R1077 — Variante print-safe do Molambudos

**Data:** 2026-11-05  
**Status:** candidato de impressão gerado e medido. Não é publicação, não é nova
ISBN e não é validação externa.

## 1. Por que uma variante print-safe

A edição R1076 tem forte impacto sensorial na tela: fundo sépia em todas as
páginas, aberturas de parte em preto e ilustrações. Em impressão, porém, isso
significa:

- fundo sépia impresso em **421 páginas**;
- cinco aberturas de parte em preto (TAC de até **400%**);
- imagens de fragmento a **0,55 textwidth**, algumas abaixo de 300 DPI;
- página de rosto e colofão com arte de baixa resolução.

O R1077 mantém a identidade visual, mas troca **tinta por papel**: o calor vem
do papel cream do KDP, não de um fundo impresso. Na tela ele parece mais branco;
impresso, ganha a temperatura sépia sem pagar o custo de tinta.

## 2. O que mudou

| Item | R1076 (digital/sensorial) | R1077 (print-safe) |
|---|---|---|
| Páginas | 421 | **422** |
| Fundo | sépia impresso em todas as páginas | **papel cream, sem fundo impresso** |
| Aberturas de parte | página preta + dourado | **numeral romano + título + filete + ícone** |
| Rosto, colofão e “Cuidado” | arte/fundo | **tipográficos** |
| Imagens de fragmento | 0,55 textwidth (222–296 DPI) | **0,54 textwidth (paisagens) / 0,40 (retrato), ≥300 DPI** |
| Cores vetoriais | RGB | **CMYK com TAC ≤205%** |
| TAC médio | **304,4%** | **11,7%** |
| TAC máximo | **400%** | **173,4%** |
| PDF | `9ee4c467…` | `0bb22d292f9e7ed04820c0fcac093495a1951a734b308bf674e33afae1e381a5` |

## 3. Qualidade gráfica

| Verificação | Resultado |
|---|---|
| Páginas | 422 |
| Tamanho | 453,543 × 651,968 pt = 160 × 230 mm |
| Fontes | todas embutidas |
| Imagens | 20; **mínimo 300 DPI**; nenhuma abaixo de 300 |
| Cores | CMYK para elementos vetoriais; TAC máx. 205% nos textos |
| Cobertura média | 11,7% (C 0,70%; M 3,76%; Y 3,77%; K 3,44%) |
| Cobertura máxima | 173,4% |
| Preflight KDP | capa exterior ainda a ~163 DPI; lombada a recalcular para 422 pp |

A queda de TAC é o dado central: o miolo deixa de imprimir um fundo em todas as
páginas e passa a imprimir **texto, imagens e acentos**. Isso reduz risco de
show-through, consumo de tinta e variação de cor.

### Pranchas ampliadas

- Joaquim: **3,2 × 4,0 in** (~350 DPI).
- Paisagens do caderno: **2,3 in** (~348 DPI).
- Retrato do Dr. Oliveira: **2,0 in** (~300 DPI).
- Imagens de fragmento: paisagens **0,54 textwidth** (~301 DPI); retrato **0,40** (~305 DPI).

A ampliação para 3,2 in no retrato de Joaquim é o limite nativo seguro; acima
disso seria upscale, que não entra nesta edição print-safe.

## 4. O que permaneceu

- 84 fragmentos, 5 partes, capitular de família em cada abertura.
- Paleta de códigos: MEM cobre, DOC teal, LUC violeta, CONT carmim.
- Legenda dos Códigos.
- Caderno de Provas Iconográficas com 6 pranchas e aviso de ficção documental.
- Texto revisado R1075 (DOC −18,3%; CONT 7; LUC 23).

## 5. Trade-off editorial

O R1077 é a edição **de impressão**. A R1076 continua sendo a edição
**digital/sensorial**, com fundo sépia na tela e aberturas pretas. Não são a
mesma peça:

- para ler em tela, R1076 tem mais atmosfera;
- para imprimir em papel cream, R1077 é mais segura, mais barata e mais fiel ao
  material.

## 6. Limites

- A capa exterior continua a ~163 DPI; precisa de arte em 300 DPI.
- A lombada deve ser recalculada para **422 pp** (≈0,992 in na fórmula adotada).
- Sem nova ISBN; uma edição impressa substancialmente revista exige ISBN própria.
- Traduções EN/ZH/TRI não atualizadas.
- PDF tagged/PDF-UA bloqueado pelo toolchain.
- Nenhuma nota 10/10, validação profissional ou prova histórica é declarada.
