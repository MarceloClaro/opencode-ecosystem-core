# Fontes dos Volumes — Alfabetizar Bem

Pasta com as fontes utilizadas pelos 5 volumes (compilados com **XeLaTeX** + `fontspec`).

## Arquivos

| Arquivo | Origem | Uso |
|---|---|---|
| `irineu cursivo escolar.ttf` | Fornecido pelo autor (MarceloClaro). Nome interno: `Cursive scolaire © Jean-Claude Gineau 97` (274 glyphs; acentos PT confirmados por fontTools: Ã Õ Á É Í Ó Ú Â Ê Ô À Ç etc. presentes). | Fonte cursiva de modelo (`\fontecursiva`) para exercícios de caligrafia. |
| `Mestra2(MeMimaPuntejada).TTF` | Fornecida pelo autor (Downloads). 266 glyphs; acentos PT confirmados; **fsType=0 (incorporação permitida)** — verificado por fontTools. | Fonte **pontilhada** (`\papalavra`) — palavras e ligações do Caderno Motor (SPEC-935-R209). |
| `Mestra4(DoblePautaPuntejada).TTF` | Fornecida pelo autor (Downloads). 266 glyphs; acentos PT confirmados; **fsType=0 (incorporação permitida)** — verificado por fontTools. | Fonte **pontilhada em pauta dupla** (`\papauta`) — letras-modelo do Caderno Motor. |
| `Irineu Brasil Infantil A.pdf` | Amostra oficial da fonte **Irineu Brasil Infantil A** (Cia. Letra de Mão / EEV) — download do site oficial, mesma amostra em `C:\Users\marce\Downloads\`. | **Referência apenas.** Contém a fonte incorporada como *subset* de 27 glyphs (só as letras da amostra) — **não utilizável como fonte** no LaTeX. |

## Licenças e restrições — IMPORTANTE

- **Irineu Brasil Infantil A (completa)**: o site oficial
  (`fonteirineuletrademao.eev.com.br`) informa que as fontes **não são vendidas a
  escolas, empresas, editoras, designers ou curiosos** — somente a professoras em
  exercício, mediante contato comercial (WhatsApp). A fonte completa **não está
  disponível para download aberto**. Por isso este projeto não a redistribui.
  Para habilitá-la nos volumes: adquirir legalmente a fonte e colocar a TTF em
  `fontes/Irineu Brasil Infantil A.ttf` (trocar 1 arquivo + recompilar — o preâmbulo
  já declara o nome; basta remover o comentário do `\setmainfont`/`\titulofonte`).
- **irineu cursivo escolar.ttf**: fontes escolares de Jean-Claude Gineau são
  distribuídas gratuitamente para fins educacionais. Verificar a licença junto ao
  autor para uso editorial amplo.
- **Mestra2 / Mestra4** (Memima Puntejada / Doble Pauta Puntejada): sem restrição
  de incorporação (fsType=0) — podem ser embutidas nos PDFs.
- **SchoolScriptDashed**: **NÃO incorporada**. `fsType=2` (restrição de licença de
  incorporação) verificado por fontTools — mantida fora até licença confirmada.

## Como as fontes são usadas no LaTeX

No preâmbulo de cada volume (`VolumeN/main.tex`):

```latex
\RequirePackage{fontspec}
\defaultfontfeatures{Path=../fontes/, Extension=.ttf}
\newfontfamily\fontecursiva{irineu cursivo escolar}   % modelo de escrita cursiva
% \newfontfamily\titulofonte{Irineu Brasil Infantil A}  % desbloquear quando licenciada
```

O corpo do livro permanece em Latin Modern (mesma métrica do baseline pdflatex),
evitando re-paginação; a fonte cursiva aparece no modelo de caligrafia (página de
rosto de cada volume).

## Compilação

```bash
cd VolumeN && xelatex -interaction=nonstopmode main.tex   # 2x
```

Não usar `pdflatex` (não suporta TTF nativamente).