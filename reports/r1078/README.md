# R1078 — Book Studio Universal: landscape GitHub e arquitetura de gaps

**Data:** 2026-11-05  
**Status:** pesquisa concluída; fase 0 executada com ferramentas externas em
`/tmp/opencode` (EPUBCheck, Ace, Vale e LanguageTool). Nenhum dos 109
repositórios do landscape foi clonado ou embutido no Core.
**Escopo:** mapear candidatos no GitHub para transformar o Core/Book Studio em
diagramador, editor e assistente literário universal, cobrindo os gaps observados
no Molambudos e no pipeline editorial atual.

> Este relatório não declara que os repositórios “resolvem” os gaps. Ele registra
> candidatos, licença, atividade, modo de integração e risco. As ferramentas
> executadas na fase 0 são externas, com versão registrada, e não foram
> incorporadas ao Core. A integração exige spec, teste, revisão de licença e
> aprovação humana.

## 1. Diagnóstico: os gaps que o Molambudos expôs

| ID | Gap | Evidência no projeto | Estado atual | Severidade |
|---|---|---|---|---|
| G1 | Capa, lombada, bleed/trim e 300 DPI | capa exterior a ~163 DPI; candidata a 137 DPI; lombada a recalcular para 421/422 pp | bloqueia upload KDP | **alta** |
| G2 | ISBN, ONIX, metadados e ficha catalográfica | sem nova ISBN para edição impressa; metadados dispersos | manual | **alta** |
| G3 | PDF/UA e PDF tagged | `tagpdf`/`luaotfload` bloquearam o pipeline | não produzido | **alta** |
| G4 | EPUB acessível | 13 imagens, 84 seções, mas sem Ace/EPUBCheck no gate | parcial | **alta** |
| G5 | Editor/copyediting pt-BR | revisão R1075 reduziu DOC em 18,3%, mas sem linter contínuo | manual | **alta** |
| G6 | Assistente literário | 84 fragmentos, 4 famílias, arco de Lúcia e linha ontológica mantidos por planilha/texto | manual | **alta** |
| G7 | Diagramação/tipografia/layout | 421 pp; TAC médio 304,4% na R1076; variante print-safe R1077 com 11,7% | frágil | **alta** |
| G8 | Diagramas visuais | mapas, grafo de leitura e caderno iconográfico feitos sob medida | sob medida | média |
| G9 | Ingestão/Document IR | PDF, EPUB e DOCX tratados por scripts específicos | parcial | média |
| G10 | Proveniência/versionamento | hashes SHA-256 e manifestos, mas sem C2PA/RO-Crate/DVC | parcial | média |
| G11 | Tradução/QA trilíngue | EN/ZH/TRI não atualizadas | pendente | **alta** |
| G12 | Áudio/vídeo/podcast | podcast com 26 episódios; sem gate de loudness/ASR | parcial | média |
| G13 | Distribuição | KDP manual; sem API pública de upload | manual | **alta** |
| G14 | UX/Studio | CLI + scripts; sem dashboard, biblioteca de assets e aprovações | inicial | média |
| G15 | Testes/QA | 147 testes; doctor 22/22; falta regressão visual e PDF diff | parcial | média |

### 1.1 O que já está resolvido e não deve ser refeito

- Edição canônica: 435 pp, hash `3378f438…`.
- R1075: 421 pp; DOC 18.316→14.969 (−18,3%); CONT 7; LUC 23.
- R1076: edição digital/sensorial; Cuidado `#FF4D4D` (6,42:1 sobre preto).
- R1077: variante print-safe; 422 pp; 20 imagens; mínimo 300 DPI; TAC médio
  11,7%; máximo 173,4%.
- Catálogo: 48 registros.
- Checksums: 16/16, 3/3, 2/2.
- Testes: 165 (147 anteriores + 5 do landscape + 13 do Book Studio); `doctor` 22/22.
- Nenhuma nota 10/10, publicação ou validação externa é declarada.

## 2. Método e critérios

A varredura usou a API do GitHub em 2026-11-05, com consultas por tópico,
palavra-chave e lote de repositórios conhecidos. Para cada candidato foram
registrados: estrelas, licença, linguagem, último push, descrição e URL. Quando
o GitHub retornou “Other”, o texto do LICENSE foi lido para classificar.

Critérios de decisão:

1. **Licença primeiro.** MIT/Apache/BSD podem ser biblioteca; LGPL/MPL exigem
   linkagem dinâmica ou CLI; GPL/AGPL só como processo externo ou referência.
2. **Manutenção.** `pushed_at` recente, não arquivado, issues ativas.
3. **Adequação ao gap.** Popularidade não é qualidade; estrelas não são prova.
4. **Modo de integração explícito.**
   - `core-native`: implementado no Core, sem dependência externa.
   - `adapter`: CLI/serviço externo, com contrato e sandbox.
   - `library`: importado como biblioteca.
   - `reference`: estudado, não embutido.
   - `avoid`: risco de licença, segurança ou falsa autoridade.
5. **Risco.** Licença, supply chain, dados, rede, qualidade da alegação.

## 3. Top 12 para adotar agora (P0)

| # | Repositório | Licença | Modo | Gap | Papel |
|---|---|---|---|---|---|
| 1 | `typst/typst` | Apache-2.0 | adapter | G3, G7 | motor de composição para interiores e variantes |
| 2 | `quarto-dev/quarto-cli` | MIT | adapter | G4, G7, G14 | orquestração de livro em PDF/EPUB/HTML/DOCX |
| 3 | `Kozea/WeasyPrint` | BSD-3-Clause | library | G3, G4, G7 | HTML/CSS para PDF, paginação e PDF/UA |
| 4 | `pdfcpu/pdfcpu` + `qpdf/qpdf` | Apache-2.0 | adapter | G1, G7, G15 | validação, merge, split, otimização, estrutura |
| 5 | `veraPDF/veraPDF-library` | GPL-3.0 | adapter | G3, G15 | validação PDF/A e PDF/UA |
| 6 | `w3c/epubcheck` + `daisy/ace` | BSD-3-Clause + MIT | adapter | G4, G15 | conformidade e acessibilidade EPUB |
| 7 | `thoth-pub/thoth` + `xlcnd/isbnlib` | Apache-2.0 + LGPL-3.0 | adapter/library | G2, G13 | ONIX 3.0, Crossref, ISBN |
| 8 | `languagetool-org/languagetool` + `vale-cli/vale` + `textstat/textstat` | LGPL-2.1 + MIT + MIT | adapter/library | G5 | gramática, estilo e legibilidade |
| 9 | `booknlp/booknlp` + `explosion/spaCy` + `networkx/networkx` | MIT + MIT + BSD-3-Clause | library | G6 | personagens, citações, eventos, redes |
| 10 | `docling-project/docling` + `jsvine/pdfplumber` + `py-pdf/pypdf` | MIT + MIT + BSD-3-Clause | library | G9, G15 | ingestão, layout e auditoria de PDF |
| 11 | `facelessuser/coloraide` + `fonttools/fonttools` | MIT + MIT | library | G7 | cor/contraste e fontes |
| 12 | `FFmpeg/FFmpeg` + `openai/whisper` | LGPL/GPL + MIT | adapter/library | G12 | áudio, loudness, transcrição |

### 3.1 Por que esses e não os “mais famosos”

- **Typst** é Apache-2.0, rápido, scriptável e adequado a builds reprodutíveis.
  Não substitui automaticamente a trilha ABNT em LaTeX; ela continua necessária
  para ABNT estrita.
- **Quarto** orquestra múltiplas saídas, mas embarca Pandoc (GPL). Deve ser CLI
  externo, com avisos de licença.
- **WeasyPrint** é a rota permissiva para PDF/UA e paginação CSS; não é motor de
  composição tipográfica fina como Typst/SILE.
- **pdfcpu/qpdf** resolvem operações PDF sem AGPL; evitam o uso de PyMuPDF.
- **veraPDF/EPUBCheck/Ace** são gates, não geradores de qualidade: eles reprovam,
  não aprovam artisticamente.
- **LanguageTool** cobre pt-BR; Vale e textstat entram como estilo e diagnóstico.
- **BookNLP** é Inglês. Para PT-BR, a arquitetura precisa de spaCy/Stanza e
  avaliação própria; não se deve alegar paridade.
- **Docling/pdfplumber/pypdf** são permissivos e suficientes para IR e auditoria.

## 4. Mapa por camada

### 4.1 Ingestão e Document IR (G9)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `docling-project/docling` | 70.166 | MIT | library | PDF/DOCX/PPTX/HTML → JSON estruturado |
| `datalab-to/marker` | 40.790 | Apache-2.0 | adapter | PDF → Markdown/JSON, tabelas |
| `grobidOrg/grobid` | 5.220 | Apache-2.0 | adapter | estrutura de artigos e referências |
| `apache/tika` | 4.130 | Apache-2.0 | adapter | metadados e texto de 1.000+ formatos |
| `ocrmypdf/OCRmyPDF` | 35.245 | MPL-2.0 | adapter | camada OCR + PDF/A |
| `tesseract-ocr/tesseract` | 77.378 | Apache-2.0 | adapter | OCR |
| `jsvine/pdfplumber` | 10.876 | MIT | library | coordenadas de caracteres/linhas |
| `py-pdf/pypdf` | 10.287 | BSD-3-Clause | library | split/merge/crop/metadados |
| `pymupdf/PyMuPDF` | 11.074 | AGPL-3.0 | **avoid** | rápido, mas AGPL |

**Contrato:** `DocumentIR` com blocos, estilos, origem, página, bounding box,
hash e confiança. Nenhum texto entra no pipeline sem proveniência.

### 4.2 Editor e copyediting (G5)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `languagetool-org/languagetool` | 15.232 | LGPL-2.1 | adapter | gramática/estilo pt-BR |
| `vale-cli/vale` | 6.334 | MIT | adapter | linter de prosa e guia de estilo |
| `textlint/textlint` | 3.205 | MIT | adapter | linter plugável |
| `textstat/textstat` | 1.393 | MIT | library | legibilidade |
| `Automattic/harper` | 17.426 | Apache-2.0 | adapter | corretor offline; verificar pt-BR |
| `hunspell/hunspell` | 2.619 | LGPL-2.1 | library | spellcheck pt_BR |
| `nuspell/nuspell` | 269 | LGPL-3.0 | library | spellcheck rápido |
| `amperser/proselint` | 4.595 | BSD-3-Clause | adapter | prosa EN |
| `get-alex/alex` | 5.106 | MIT | adapter | linguagem inclusiva EN |

**Gate:** nenhum texto é “aprovado” por linter. O relatório aponta ocorrências,
gravidade, trecho e sugestão; a decisão é humana.

### 4.3 Assistente literário (G6)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `booknlp/booknlp` | 946 | MIT | library | personagens, citações, eventos (EN) |
| `explosion/spaCy` | 34.030 | MIT | library | NER, dependências, pt |
| `stanfordnlp/stanza` | 7.906 | Apache-2.0 | library | NLP multilíngue |
| `networkx/networkx` | 17.386 | BSD-3-Clause | library | grafo de personagens |
| `MaartenGr/BERTopic` | 7.932 | MIT | library | temas e motivos |
| `fastdatascience/faststylometry` | 55 | MIT | library | Burrows Delta |
| `computationalstylistics/stylo` | 230 | GPL-3.0 | reference | estilometria em R |
| `JasonKessler/scattertext` | 2.349 | Apache-2.0 | library | comparação de linguagem |
| `WestHealth/pyvis` | 1.214 | BSD-3-Clause | library | grafo interativo |

**Contrato:** `LiteraryReport` com personagens, relações, arco de sentimento,
POV, timeline, motivos, inconsistências e confiança. O assistente **sugere**;
não reescreve o romance sem aprovação.

### 4.4 Diagramação e tipografia (G7)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `typst/typst` | 57.007 | Apache-2.0 | adapter | composição moderna |
| `quarto-dev/quarto-cli` | 6.155 | MIT | adapter | projeto e múltiplas saídas |
| `jgm/pandoc` | 46.830 | GPL-2.0 | adapter | conversão universal |
| `Kozea/WeasyPrint` | 9.760 | BSD-3-Clause | library | HTML/CSS → PDF |
| `tectonic-typesetting/tectonic` | 5.230 | MIT | adapter | TeX autocontido |
| `sile-typesetter/sile` | 1.790 | MIT | adapter | tipografia fina |
| `pagedjs/pagedjs` | 1.561 | MIT | library | paginação/preview |
| `abntex/abntex2` | 1.158 | LPPL-1.3c | library | ABNT |
| `facelessuser/coloraide` | 365 | MIT | library | cor/contraste/CMYK |
| `fonttools/fonttools` | 5.308 | MIT | library | fontes/subsetting |

**Contrato:** `DesignTokens` com paleta HEX/CMYK, pares de contraste, escala
tipográfica, grid, margens, bleed e opções de acessibilidade.

### 4.5 Produção gráfica e pré-impressão (G1, G3, G15)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `pdfcpu/pdfcpu` | 8.897 | Apache-2.0 | adapter | validar/otimizar/merge |
| `qpdf/qpdf` | 5.559 | Apache-2.0 | adapter | transformação que preserva conteúdo |
| `pikepdf/pikepdf` | 2.819 | MPL-2.0 | library | PDF cirúrgico |
| `veraPDF/veraPDF-library` | 352 | GPL-3.0 | adapter | PDF/A e PDF/UA |
| `ArtifexSoftware/ghostpdl` | 302 | AGPL-3.0 | adapter | inkcov/render/PDF-X (externo) |
| `ImageMagick/ImageMagick` | 17.805 | ImageMagick License | adapter | DPI/perfis/raster |
| `libvips/libvips` | 11.782 | LGPL-2.1 | library | imagem em lote |
| `opendataloader-project/opendataloader-pdf` | 30.177 | Apache-2.0 | adapter | acessibilidade PDF |

**Core-native obrigatório:** fórmula KDP de capa/lombada/bleed, cálculo de
spine por páginas e gramatura, gate de TAC/CMYK, gate de DPI, checklist de
preflight. Nenhum repositório substitui a arte em 300 DPI.

### 4.6 EPUB e acessibilidade (G4)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `w3c/epubcheck` | 1.985 | BSD-3-Clause | adapter | conformidade EPUB |
| `daisy/ace` | 101 | MIT | adapter | acessibilidade EPUB |
| `kovidgoyal/calibre` | 26.357 | GPL-3.0 | adapter | conversão/gestão (externo) |
| `pgaskin/kepubify` | 899 | MIT | adapter | EPUB → Kobo |
| `Sigil-Ebook/Sigil` | 7.020 | GPL-3.0 | reference | editor EPUB |
| `standardebooks/tools` | 1.685 | GPL-3.0 | reference | toolset editorial |
| `dequelabs/axe-core` | 7.764 | MPL-2.0 | library | acessibilidade HTML |
| `pa11y/pa11y` | 4.590 | LGPL-3.0 | adapter | acessibilidade web |

**Gate:** EPUBCheck + Ace + checagem de alt text/nav/reading order. Passar não
significa “acessível”; significa “sem erros automatizados detectáveis”.

### 4.7 Metadados, ISBN e distribuição (G2, G13)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `thoth-pub/thoth` | 55 | Apache-2.0 | adapter | ONIX 3.0, Crossref, OA |
| `xlcnd/isbnlib` | 281 | LGPL-3.0 | library | ISBN |
| `citation-js/citation-js` | 213 | MIT | library | CSL/BibTeX/RIS/DOI |
| `retorquere/zotero-better-bibtex` | 7.276 | MIT | adapter | BibTeX do Zotero |
| `titusz/onixcheck` | 28 | Apache-2.0 | library | validação ONIX |
| `JabRef/jabref` | 4.872 | MIT | reference | gestão BibTeX |
| `zotero/zotero` | 15.859 | AGPL-3.0 | reference | gestor de referências |
| `abntex/biblatex-abnt` | 151 | LPPL (confirmar) | library | ABNT/BibLaTeX |

**Limite:** ISBN, ficha catalográfica, depósito legal e direitos autorais são
institucionais. Nenhum repositório resolve isso.

### 4.8 Diagramas e visualização (G8)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `mermaid-js/mermaid` | 91.020 | MIT | library | fluxos, timelines, estados |
| `d2lang/d2` | 25.799 | MPL-2.0 | adapter | diagramas modernos |
| `yuzutech/kroki` | 4.398 | MIT | adapter | servidor de diagramas |
| `cytoscape/cytoscape.js` | 11.267 | MIT | library | redes |
| `vega/vega-lite` | 5.545 | BSD-3-Clause | library | gráficos declarativos |
| `plantuml/plantuml` | 13.402 | LGPL-3.0 | adapter | UML |
| `jgraph/drawio` | 9.204 | Apache-2.0 | reference | editor completo |
| `excalidraw/excalidraw` | 135.214 | MIT | reference | esboço |
| `Leaflet/Leaflet` | 45.860 | BSD-2-Clause | library | mapas |
| `maplibre/maplibre-gl-js` | 12.031 | BSD-3-Clause | library | mapas vetoriais |

**Uso literário:** árvore genealógica, mapa de Barbacena, timeline de 1914–2026,
grafo de personagens, arco de tensão, mapa de rotas e linhas de leitura.

### 4.9 Áudio, vídeo e podcast (G12)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `openai/whisper` | 112.036 | MIT | library | ASR |
| `m-bain/whisperX` | 25.105 | BSD-2-Clause | library | timestamps/diarização |
| `rhasspy/piper` | 11.317 | MIT | adapter | TTS local |
| `coqui-ai/TTS` | 46.184 | MPL-2.0 | library | TTS (verificar manutenção) |
| `FFmpeg/FFmpeg` | 66.584 | LGPL/GPL | adapter | áudio/vídeo |
| `jiixyj/libebur128` | 494 | MIT | library | loudness EBU R128 |
| `motion-canvas/motion-canvas` | 19.706 | MIT | library | animação programática |
| `ManimCommunity/manim` | 42.273 | MIT | library | animação matemática |
| `midrender/revideo` | 4.180 | MIT | library | vídeo programático |
| `remotion-dev/remotion` | 71.052 | Remotion License | **avoid** | restrição comercial |

### 4.10 Infraestrutura de IA e governança (G10, G14)

| Repositório | Stars | Licença | Modo | Papel |
|---|---:|---|---|---|
| `ollama/ollama` | 186.037 | MIT | adapter | inferência local |
| `ggml-org/llama.cpp` | 133.492 | MIT | library | CPU/GPU |
| `huggingface/transformers` | 168.588 | Apache-2.0 | library | modelos |
| `huggingface/sentence-transformers` | 19.258 | Apache-2.0 | library | embeddings |
| `run-llama/llama_index` | 52.821 | MIT | library | RAG |
| `deepset-ai/haystack` | 26.929 | Apache-2.0 | library | RAG |
| `stanfordnlp/dspy` | 38.946 | MIT | library | programas com LM |
| `dottxt-ai/outlines` | 16.003 | Apache-2.0 | library | saída estruturada |
| `treeverse/dvc` | 15.961 | Apache-2.0 | adapter | versionamento de artefatos |
| `ResearchObject/ro-crate-py` | 92 | Apache-2.0 | library | proveniência |
| `contentauth/c2pa-rs` | 439 | Apache-2.0/MIT | library | proveniência de imagem |
| `sigstore/sigstore` | 540 | Apache-2.0 | adapter | assinatura |
| `in-toto/in-toto` | 1.055 | Apache-2.0 | adapter | integridade de build |

## 5. Licenças: o que pode entrar e como

| Classe | Exemplos | Regra no Core |
|---|---|---|
| Permissiva (MIT/Apache/BSD/ISC) | Typst, Quarto, WeasyPrint, pdfcpu, qpdf, pypdf, Docling, spaCy, BookNLP, NetworkX, ColorAide, FontTools, EPUBCheck, Ace, Thoth, Mermaid, D2, Kroki, Vega-Lite, Whisper, Piper, Ollama, llama.cpp, DVC | biblioteca ou adapter |
| Copyleft fraco (LGPL/MPL) | LanguageTool, Hunspell, Nuspell, libvips, PlantUML, isbnlib, pikepdf | linkagem dinâmica ou CLI; revisar |
| Copyleft forte (GPL/AGPL) | Pandoc, Calibre, Sigil, Scribus, Manuskript, novelWriter, bibisco, Booktype, Pressbooks, Standard Ebooks, veraPDF, Ghostscript, PyMuPDF, MuPDF, LibreTranslate, Vivliostyle | **somente CLI externo ou referência**; nunca `library` |
| Source-available | Remotion, tldraw | evitar como dependência central; revisar contrato |
| Sem licença clara | alguns geradores de capa pequenos | não copiar código; estudar fórmula e reimplementar |

**Regra de ouro:** o Core não incorpora código GPL/AGPL. Ele chama ferramentas
externas, com contrato, versão fixada e sandbox. Se o Core distribuir um bundle
com Pandoc/Calibre/Ghostscript, precisa cumprir as obrigações de cada licença.

## 6. O que nenhum repositório resolve

1. **Arte de capa em 300 DPI.** O gargalo do Molambudos é asset, não software.
   Nenhum repo transforma 163 DPI em 300 DPI sem upscale artificial.
2. **Lombada, contracapa e prova física.** A fórmula pode ser implementada, mas
   a arte e a prova de impressão são humanas.
3. **ISBN, ficha catalográfica, depósito legal e direitos.** São institucionais.
4. **Qualidade literária, sensibilidade e aceitação editorial.** Ferramentas
   apontam padrões; não julgam mérito.
5. **Tradução literária.** COMET/chrF medem proximidade; não substituem revisão
   humana, voz autoral e adequação cultural.
6. **PDF/UA final.** Validadores detectam erros; a remediação de leitura, ordem
   e alt text é manual.
7. **Upload KDP/IngramSpark.** Não há API pública; o envio é manual.
8. **Veracidade histórica e ética da ficção documental.** Nenhum repo decide se
   uma imagem inventada de vítima é aceitável.
9. **LGPD e dados de leitores.** Consentimento, minimização e retenção são
   decisões jurídicas e de produto.

## 7. Arquitetura proposta: Book Studio Universal

### 7.1 Princípio

O Book Studio não deve ser um monolito que “faz tudo”. Deve ser um **orquestrador
de contratos** com adaptadores substituíveis. Cada ferramenta externa entra por
um contrato, com licença, versão, sandbox e proveniência.

```
Fonte (Markdown/LaTeX/Typst/DOCX)
        │
        ▼
[Ingest & IR] Docling/Marker/GROBID/Tika/OCRmyPDF
        │  DocumentIR + hashes
        ▼
[Editorial] LanguageTool/Vale/textlint/textstat
        │  EditorialReport
        ▼
[Literary] spaCy/Stanza/BookNLP/NetworkX/BERTopic/stylometry
        │  LiteraryReport
        ▼
[Design] Typst/Quarto/Pandoc/WeasyPrint/ABNT LaTeX + DesignTokens
        │  Layout + PrintSpec
        ▼
[Print] KDP formula + pdfcpu/qpdf/pikepdf + Ghostscript/veraPDF
        │  PreflightReport
        ▼
[Ebook/A11y] Pandoc/Quarto + EPUBCheck/Ace + PDF/UA
        │  A11yReport
        ▼
[Metadata] Thoth/isbnlib/citation-js/Better BibTeX
        │  MetadataRecord (ONIX/ISBN/DOI)
        ▼
[Release] SHA-256 + DVC/RO-Crate/C2PA/Sigstore
        │  ReleaseManifest
        ▼
[Studio] Tauri/PDF.js/CodeMirror + asset library + approvals
```

### 7.2 Contratos mínimos

| Contrato | Conteúdo | Gate |
|---|---|---|
| `DocumentIR` | blocos, estilos, página, bbox, origem, hash, confiança | nenhum texto sem proveniência |
| `DesignTokens` | HEX/CMYK, contraste, escala, grid, margens, bleed | contraste ≥4,5:1; TAC ≤210% em texto |
| `PrintSpec` | trim, bleed, spine, TAC, PDF/X, DPI, fontes | 300 DPI; fontes embutidas; TAC <300% |
| `EditorialReport` | gramática, estilo, repetição, legibilidade | nenhuma aprovação automática |
| `LiteraryReport` | personagens, relações, timeline, POV, motivos, inconsistências | confiança explícita; revisão humana |
| `A11yReport` | PDF/UA, EPUB a11y, alt text, reading order | EPUBCheck + Ace + checklist manual |
| `MetadataRecord` | ISBN, ONIX, BISAC/THEMA, DOI, direitos | ONIX válido; ISBN válido |
| `ReleaseManifest` | artefatos, SHA-256, assinatura, C2PA | checksums + aprovação |

### 7.3 Protocolo de adaptador

```
check()   -> presença, versão, licença, capacidades
plan()    -> entradas, saídas, tempo, rede, riscos
run()     -> subprocesso em sandbox, sem shell injection
verify()  -> valida o artefato com gate independente
report()  -> saída estruturada + hashes + logs
```

Regras:

- rede desligada por padrão; allowlist explícita;
- diretório temporário por job; limites de CPU/memória/tempo;
- versão fixada e registrada no `ReleaseManifest`;
- nenhum segredo em linha de comando;
- `license_class` obrigatório; GPL/AGPL só `external_cli` ou `reference`;
- `human_gate` para publicar, apagar, enviar, pagar e chamar API externa.

### 7.4 Studio (G14)

O Studio é a camada de UX, não o motor. Proposta:

- **Shell:** Tauri (MIT) ou web local; PDF.js (Apache-2.0) para preview.
- **Editor:** CodeMirror 6 (MIT) ou ProseMirror (MIT) para Markdown/LaTeX.
- **Jobs:** fila local com estados `queued/running/failed/needs_review/done`.
- **Assets:** biblioteca com hash, licença, DPI, CMYK, alt text e proveniência.
- **Aprovações:** toda saída entra em `needs_review`; nada é publicado sozinho.
- **Comparação:** diff de texto, diff visual de PDF e regressão de página.

## 8. Roadmap proposto

| Fase | Escopo | Entregável | Critério de aceitação |
|---|---|---|---|
| **R1078** | contratos, KDP, design tokens, manifesto | `contracts/`, `book.json`, gate de licença | schema validado; fórmula KDP testada; nenhuma dependência GPL como library |
| **R1079** | produção | Typst/Quarto/WeasyPrint + pdfcpu/qpdf/veraPDF + EPUBCheck/Ace | PDF 160×230; fontes embutidas; ≥300 DPI; TAC <300%; EPUB passa |
| **R1080** | editorial + literário | LanguageTool/Vale/textstat + spaCy/BookNLP/NetworkX | relatório pt-BR; grafo de personagens; timeline; nenhuma aprovação automática |
| **R1081** | metadados + tradução + diagramas | Thoth/isbnlib/citation-js + COMET/sacreBLEU + Mermaid/D2 | ONIX válido; ISBN válido; baseline COMET/chrF; diagramas exportados |
| **R1082** | áudio/vídeo + Studio | WhisperX/Piper/FFmpeg/ebur128 + Tauri/PDF.js | loudness; legendas; preview; aprovações |
| **R1083** | hardening | licença, sandbox, proveniência, docs | 100% dos gates; auditoria de licença; release reproduzível |

### 8.1 O que fazer primeiro no Molambudos

1. **Capa 300 DPI e lombada.** Sem isso, nenhum upload KDP é honesto.
2. **PDF/UA com Typst ou WeasyPrint.** Escolher um, medir e documentar o que
   falta para conformidade.
3. **EPUBCheck + Ace** no release R1076/R1077.
4. **LanguageTool + Vale** sobre os 84 fragmentos, com relatório versionado.
5. **BookNLP/spaCy** para personagens, citações e timeline; comparar com o
   mapa manual já existente.
6. **Thoth + isbnlib** para metadados e ONIX.
7. **Gate de licença** antes de qualquer nova dependência.

## 9. Riscos e anti-overclaim

- **Estrelas não são qualidade.** Muitos repos populares não têm testes, licença
  clara ou manutenção.
- **Repo não é integração.** A lista é um mapa; nada foi executado.
- **Validador não é aprovação.** EPUBCheck/Ace/veraPDF reprovam; não certificam
  mérito literário.
- **Tradutor automático não é tradução publicada.** COMET/chrF são métricas.
- **Assistente literário não é editor.** Ele sugere; o humano decide.
- **PDF/UA não é “acessível por decreto”.** Exige leitura, alt text e ordem.
- **KDP não é “publicado”.** Exige capa, lombada, ISBN, prova e aceite da
  plataforma.
- **Nenhuma nota 10/10, Qualis A1 ou aceite editorial é declarada.**

## 10. Estado da execução

- **R1078 aprovada e fase 0 implementada** em `marceloclaro/bookstudio/`:
  contratos, KDP, design tokens, gate de licença, manifesto de release e CLI.
- **R1079 parcial:** o preflight dos artefatos existentes passou (422 pp,
  160×230 mm, 15 fontes embutidas, 20 imagens ≥300 DPI, TAC 11,7%/173,4%,
  EPUBCheck/Ace). pdfcpu/qpdf/veraPDF e um build novo ainda pendem.
- **R1080–R1083 autorizadas**, mas não concluídas neste ciclo. O LanguageTool/Vale
  já produziu evidência inicial; spaCy/BookNLP/NetworkX, Thoth/COMET, áudio/vídeo
  e o shell do Studio continuam pendentes.
- A capa 300 DPI foi investigada: a frente é vetorial e pode ser re-renderizada;
  a contracapa precisa de re-layout por proporção incompatível.
- A edição R1076/R1077 permanece intacta; o EPUB revisado recebeu apenas o
  `accessibilitySummary` e foi revalidado.
- Nenhuma publicação, ISBN nova ou upload KDP foi executado.

## 11. Arquivos

| Caminho | Conteúdo |
|---|---|
| `reports/r1078/README.md` | este relatório |
| `reports/r1078/github_landscape.json` | 109 repositórios com licença, stars, gap, modo e prioridade |
| `reports/r1078/kdp_specs.json` | lombada e capa completa para 421/422/435 pp |
| `reports/r1078/cover/` | template KDP 422 pp, achados de capa e 300 DPI |
| `reports/r1078/pdfua/` | piloto Typst × WeasyPrint com métricas de estrutura |
| `reports/r1078/editorial/` | LanguageTool 6.6 e Vale 3.26 sobre os 84 fragmentos |
| `marceloclaro/bookstudio/` | contratos, KDP, tokens, licença, release, EPUB e CLI |
| `specs/SPEC-935-R1078-book-studio-universal.md` | arquitetura e critérios da fase 0 |
| `tests/test_r1078_bookstudio_contracts.py` | 13 testes de contratos, KDP, tokens, licença e release |
| `tests/test_r1078_book_studio_landscape.py` | gate do manifesto (schema, cobertura, licença) |

## 12. Fase 0 executada (evidência)

| Entrega | Resultado |
|---|---|
| Contratos | `BookProject`, `DesignTokens`, `KDPCoverSpec`, `ReleaseManifest`; `DocumentIR` segue pendente |
| KDP | 422 pp premium color: lombada 0,9904 in; capa 13,8389 × 9,3051 in; 4152 × 2792 px |
| Capa | frente vetorial re-renderizada em 1890 × 2717 px; contracapa com proporção incompatível |
| EPUB | EPUBCheck 5.4.0: 0 erros/0 avisos; Ace 1.4.6: 26 pass/0 fail |
| PDF/UA | WeasyPrint 67: 58 nós, `pt-BR`, XMP `pdfuaid`; Typst 0.15.1: 39 nós, `pt`, XMP `pdfuaid` |
| Editorial | LanguageTool 6.6: 650 ocorrências; Vale 3.26: 95 alertas |
| Licença | 109 repos: nenhuma violação GPL/AGPL como biblioteca |
| Testes | 13 testes novos do Book Studio; **165 testes** na suíte; `doctor` 22/22 |

**Nota final:** o valor desta pesquisa não está na lista, mas na disciplina de
não confundir catálogo com execução, licença permissiva com qualidade e
ferramenta de validação com aprovação editorial.
