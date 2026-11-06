# R1076 — Direção visual e tipográfica do Molambudos

**Data:** 2026-11-05  
**Status:** design aplicado à edição revista; PDF de 421 pp e EPUB de 13
imagens gerados. Não é validação profissional independente, publicação ou nova
ISBN.

## 1. O diagnóstico

A edição anterior tinha uma paleta definida, mas **não a usava**:

- `mem`, `doc`, `luc` e `cont` apareciam **zero vezes** nos cabeçalhos dos
  fragmentos;
- os 84 fragmentos abriam com `\section*` centralizado em preto;
- não havia legenda dos códigos;
- a capitular existia apenas no prefácio, fora do corpo do livro;
- não havia caderno iconográfico.

O resultado era um texto bem composto, mas visualmente indiferenciado: MEM, DOC,
LUC e CONT pareciam a mesma família.

## 2. Paleta

Todas as cores de leitura foram medidas contra o papel sépia `#F8F0D7`.

| Família | Cor | Hex | Contraste | Uso |
|---|---|---:|---:|---|
| MEM | cobre queimado | `#8A3B1F` | **6,76:1** | inicial, filete e código |
| DOC | teal profundo | `#1F5C57` | **6,76:1** | inicial, filete e código |
| LUC | violeta | `#552A7A` | **9,23:1** | inicial, filete e código |
| CONT | carmim | `#9B1B1B` | **7,18:1** | inicial, filete e código |
| EPI | âmbar escuro | `#6E4E10` | **6,68:1** | filete do caderno |
| Tinta | sépia escuro | `#2B2117` | **13,83:1** | corpo do texto |
| Papel | sépia claro | `#F8F0D7` | — | fundo |
| Dourado | `customgold` | `#CBA135` | — | **apenas** fundo escuro |
| Olho | amarelo | `#FFD700` | — | **apenas** fundo escuro |

Regra: nenhuma cor de leitura abaixo de **4,5:1**. O dourado e o amarelo do olho
não são usados como texto sobre papel; eles pertencem à capa e às páginas
escuras de abertura de parte.

A distinção não depende só da cor: cada família tem **letra e nome** próprios
(M/D/L/C + Memória/Documento/Lucidez/Contaminação). Isso protege leitores com
daltonismo e dá redundância semântica ao código.

## 3. Tipografia e capitular

| Elemento | Especificação |
|---|---|
| Corpo | EB Garamond 14/17,5 pt |
| Título do fragmento | EB Garamond bold 18/22 pt |
| Rótulo de família | CM Sans bold 8/9 pt, small caps |
| Capitular | 40 pt, cor da família |
| Filete | 1,2 pt, 28% da largura do texto |

Cada fragmento abre com a **capitular da família**:

- **M** de Memória;
- **D** de Documento;
- **L** de Lucidez;
- **C** de Contaminação.

A capitular é seguida do rótulo “Memória 01”, “Documento 03” etc., do título e
de um filete na cor da família. Não foi acrescentada uma segunda capitular
textual no primeiro parágrafo: duas iniciais grandes na mesma página competiriam
entre si e quebrariam a unidade dos 84 fragmentos. A capitular de família é o
primeiro elemento de leitura e a assinatura visual do código.

## 4. Caderno de Provas Iconográficas

Foram acrescentadas **6 pranchas** ao final do romance, antes do glossário:

| Prisma | Imagem | Legenda |
|---|---|---|
| Paciente | `placa_00` | Paciente 1.260. Retrato de arquivo. |
| Admissão | `placa_01` | Registro de admissão. Colônia de Barbacena, 1917. |
| Médico | `placa_02` | Dr. Heitor Oliveira. Arquivo pessoal, 1979. |
| Homem do pano preto | `placa_03` | Imagem não catalogada. |
| Lúcia | `placa_04` | Rodoviária de Barbacena, 2026. |
| Fotografia 5 | `placa_05` | Arquivo pessoal de Lúcia Mendes, 2026. |

As imagens são o **arquivo iconográfico existente** do projeto (5 fotos sépia +
`joaquim.png`), recortadas para remover as legendas embutidas e reapresentadas
com legendas de ficção documental.

**Não são provas históricas.** O caderno abre com essa advertência e fecha
repetindo que as imagens pertencem ao pacto ficcional, não ao processo
histórico. Nenhuma imagem nova de vítimas foi inventada. O modelo de geração de
imagens estava indisponível nesta conexão; a solução editorial foi usar o
arquivo que o livro já possuía.

## 5. Verificação

| Item | Resultado |
|---|---|
| PDF | 421 pp; 160×230 mm; fontes embutidas; sem referências indefinidas |
| PDF SHA-256 | `9ee4c4679fe7d42b1c30605f3bebaae5dfe42cfb18567cf93f96444f5cb955be` |
| EPUB | 84 seções; 105 links; 0 quebrados; 0 LaTeX cru; **13 imagens** |
| EPUB palavras | 53.554 |
| EPUB SHA-256 | `b0fad09043777b1d0e4d743524d78a37056488fa6f26a94e035efa708460e9ac` |
| Fragmentos com capitular | 84/84 |
| Contraste mínimo | 6,68:1 (EPI) |
| Gate | `tests/test_r1076_molambudos_design.py` |

## 6. Limites

- Direção de arte interna; não é parecer profissional independente.
- Capa e lombada precisam ser recalculadas para **421 pp**; a capa em 300 DPI
  continua pendente.
- As imagens são ficção documental; não são documentos históricos.
- Traduções EN/ZH/TRI não foram atualizadas.
- PDF tagged/PDF-UA segue bloqueado pelo toolchain.
- Nenhuma nota 10/10 é declarada. O design melhora legibilidade, identidade e
  imersão; a recepção crítica continua externa.

## 7. Variante de impressão

O R1076 é a edição **digital/sensorial**. Para impressão em papel cream, existe
o candidato **R1077**: 422 pp, sem fundo sépia, aberturas tipográficas, imagens
≥300 DPI e TAC médio 11,4%. Ver `reports/r1077/README.md`.
