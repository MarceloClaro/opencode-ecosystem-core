# R1080 — Análise dos 23 repositórios de tipos, tradução e imagem

**Status:** análise de referência; nenhum repositório foi clonado ou embutido.
**Uso:** inspiração de *layout*, tipografia, hifenização e tradução — não de
estilo literário. O estilo vem do catálogo R1080.

## 1. Classificação

| Repositório | Stars | Licença | Categoria | Uso no Book Studio |
|---|---:|---|---|---|
| `Tufte-LaTeX/tufte-latex` | 1.896 | não declarada | design de livro | referência de margens, notas, figuras |
| `academic-templates/tex-book-template` | 120 | CC-BY-4.0 | template de livro | estrutura de capítulo, frontmatter |
| `hyphenation/tex-hyphen` | 73 | não declarada | hifenização | padrões PT/EN; ZH exige regra própria |
| `CTeX-org/ctex-doc` | 81 | não declarada | tipos chineses | referência para ZH (LaTeX/CTeX) |
| `CTeX-org/tex-by-topic-cn` | 78 | NOASSERTION | tipos chineses | referência conceitual; não copiar |
| `mnjey/XDUthesisBachelor` | 39 | não declarada | tese chinesa | referência de estrutura acadêmica ZH |
| `NiuTrans/MTBook` | 2.793 | não declarada | tradução automática | referência conceitual de MT/QA |
| `notcc/texufpel` | 68 | NOASSERTION | ABNT/UFPel | referência de classe brasileira |
| `livro-aberto/tex-design-development` | 19 | não declarada | design de livro | referência de projeto editorial |
| `Amet13/tex-thesis` | 101 | CC-BY-SA-4.0 | tese | referência de estrutura |
| `jemmybutton/byrne-euclid` | 1.358 | GPL-3.0 | livro ilustrado | referência visual; GPL impede cópia |
| `AareyanManzoor/Matsumura-Commutative-Algebra` | 28 | não declarada | matemática | referência de composição densa |
| `harvard-ml-courses/cs181-textbook` | 371 | não declarada | textbook | referência de didática visual |
| `sswatson/MultivariableCalculus.tex` | 61 | não declarada | textbook | referência de figuras 3D |
| `AmirAlavi/nature-tex` | 27 | MIT | artigo científico | referência de layout Nature |
| `vermiculus/bible` | 22 | não declarada | livro clássico | referência de texto longo e notas |
| `geezhu/Category-A-Textbook` | 157 | não declarada | textbook chinês | referência de livro didático ZH |
| `KimHe/Ku-book` | 20 | GPL-3.0 | livro chinês | referência; GPL impede cópia |
| `igaiga/rails_textbook` | 60 | não declarada | textbook técnico | referência de código + texto |
| `rpgtex/DND-5e-LaTeX-Template` | 1.639 | MIT | RPG/layout | referência de caixas, tabelas, cor |
| `contextgarden/not-so-short-introduction-to-context` | 79 | não declarada | ConTeXt | referência de layout avançado |
| `MartinThoma/LaTeX-examples` | 1.693 | MIT | exemplos | truques de LaTeX |
| `AlonzoLeeeooo/awesome-text-to-image-studies` | 763 | MIT | imagem | mapa de pesquisa; não é modelo |

## 2. O que aproveitar

### 2.1 Tipografia e layout

- **Tufte-LaTeX** e **tex-book-template**: margens, notas laterais, figuras,
  abertura de capítulo, frontmatter.
- **contextgarden**: fluxo de página, layers, composição avançada.
- **nature-tex**: hierarquia visual de artigo, útil para coleções e relatórios.
- **DND-5e-LaTeX-Template**: caixas, tabelas, ícones e cor — útil para romance
  ilustrado, com cuidado para não virar “manual de RPG”.

### 2.2 Línguas e tradução

- **CTeX** e **tex-by-topic-cn**: referência para ZH; não copiar sem licença.
- **tex-hyphen**: padrões de hifenização PT/EN. Chinês não usa hifenização
  silábica; a quebra de linha segue regras próprias. O Book Studio deve tratar
  ZH como caso separado.
- **NiuTrans/MTBook**: referência conceitual de tradução automática; não é
  ferramenta. Para QA, usar COMET/sacreBLEU (R1078).
- **texufpel**: referência ABNT; o Molambudos já usa abnTeX2, então é
  comparação, não substituição.

### 2.3 Imagem

- **awesome-text-to-image-studies**: mapa de pesquisa. Não instala modelo, não
  gera imagem e não garante licença. Útil para escolher arquitetura e entender
  trade-offs (difusão, controle, edição, avaliação).
- Para edição determinística, usar PIL/ImageMagick/cairosvg/WeasyPrint.
- Para edição generativa, exige API/modelo local e divulgação.

## 3. Licenças em números

- 13 sem licença declarada;
- 2 com `NOASSERTION`;
- 2 GPL-3.0 (Byrne-Euclid, Ku-book);
- 2 Creative Commons (tex-book-template, tex-thesis);
- 4 MIT (nature-tex, DND-5e, MartinThoma, awesome-text-to-image-studies).

Nenhum foi clonado ou embutido. A ausência de licença não é permissão.

## 4. O que não fazer

- Não copiar código GPL/AGPL para o Core (Byrne-Euclid, Ku-book).
- Não tratar “sem licença” como permissão; verificar antes de usar.
- Não usar template como prova de qualidade editorial.
- Não transplantar layout de matemática/tese para romance sem adaptação.
- Não confundir `awesome-list` com ferramenta executável.

## 4. Lacuna que esses repositórios não cobrem

Eles ensinam **formato**, não **voz**. O catálogo R1080 cobre:

- sensorialidade;
- tensão psicológica;
- indução narrativa;
- motivos recorrentes;
- horror sistêmico;
- tradução PT-BR/EN/ZH com sensibilidade cultural.

O Book Studio deve tratar os repositórios como **referência de composição** e o
catálogo como **referência de estilo**.
