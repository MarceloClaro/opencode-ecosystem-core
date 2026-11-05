# Molambudos — revisão editorial final e decisão de acervo

**Data:** 2026-11-05  
**Obra:** *Molambudos — O Diário do Paciente 1.260*  
**Autor:** Marcelo Dias de Carvalho Filho  
**Coautoria:** Marcelo Claro  
**Natureza:** parecer editorial interno e organização de acervo. Não é validação
externa, parecer profissional independente, aprovação de banca ou certificação
de qualidade literária.

## 1. Escopo e método

Esta revisão comparou as versões existentes no projeto consolidado
`literatura/molambudos/`:

- edição canônica `Molambudos_VictoriaRegia` (KDP PT-BR 160×230 mm);
- edição experimental `Molambudos_v2` (57 pp, sete degraus);
- edição ilustrada `Molambudos_v2_Diario` (49 pp, Partes I–II);
- template antigo `literatura/templates/molambudos-antigo` (25 pp, 4 capítulos);
- builds históricos em `Molambudos_VictoriaRegia/_archive/pdf_old/`.

Método:

1. inventário de PDFs, páginas, tamanho e SHA-256;
2. extração de texto com `pdftotext` e contagem de palavras;
3. leitura dos sumários e da estrutura de cada edição;
4. comparação de similaridade parágrafo a parágrafo com `difflib`;
5. confronto com `BOOK_STUDIO_AUDIT.md`, `reports/r1071/README.md` e
   `auditorias/parecer-banca.md`;
6. inspeção de metadados, fontes embutidas e hashes dos PDFs correntes.

**Limite importante:** não houve leitura corrida integral das 435 páginas nesta
rodada. As conclusões de mérito literário abaixo se apoiam em estrutura,
amostras extensas, contagens e auditorias já produzidas. Elas não substituem
leitura humana completa, galerada e revisão de voz.

## 2. As edições em números

| Edição | Páginas | Palavras extraídas | Estrutura | Estado |
|---|---:|---:|---|---|
| `Molambudos_VictoriaRegia` | 435 | 56.430 | 84 fragmentos + `EPI-01`; MEM/DOC/LUC/CONT | canônica incompleta em extensão, mas completa em arco |
| `Molambudos_v2` | 57 | 9.265 | 7 degraus + “Anatomia de uma Voz que Convence” + mapa | esboço experimental com 112 testes |
| `Molambudos_v2_Diario` | 49 | 7.254 | 12 capítulos, Partes I–II | edição ilustrada linear, incompleta |
| template antigo | 25 | — | 4 capítulos | template superado |
| build KDP v2.0 (arquivo) | 296 | 47.115 | miolo KDP 160×230 | build anterior ao PDF de 435 pp |

A canônica é a única edição com o arco completo e o aparato editorial de
publicação: ISBN `9798189170492`, CIP, aviso de ficção histórica, capa completa,
dossiê, traduções EN/ZH e edição trilingue.

## 3. Similaridade textual: por que v2 e Diário não são “cópias inferiores”

A comparação por parágrafos (≥60 caracteres) contra a canônica mostrou:

| Edição | Parágrafos | ≥0,90 | ≥0,80 | ≥0,60 | <0,60 |
|---|---:|---:|---:|---:|---:|
| `Molambudos_v2` | 172 | 0 | 0 | 0 | 172 |
| `Molambudos_v2_Diario` | 129 | 0 | 0 | 2 | 127 |

Isso não significa que sejam obras sem relação: elas compartilham universo,
personagens, motivos e material histórico. Significa que **não são subconjuntos
literais nem cópias truncadas** da canônica. São reescritas/edições alternativas.

Consequência prática: tratá-las como “versão inferior” exigia decisão editorial,
não limpeza técnica. Elas foram colocadas em quarentena com hash e manifesto e,
após revisão do manifesto, excluídas definitivamente por decisão explícita do
autor em 2026-11-05. O registro de hashes permanece em `reports/r1073/`.

## 4. Achado técnico sobre o PDF canônico

O arquivo no caminho canônico
`Molambudos_VictoriaRegia/main_kdp_pt_160x230mm.pdf` estava com o PDF **antigo**:

- SHA-256 `77aabe2e4e055d7f53fbef17dd3857e561f50f556a94f92da0d3ff039f4ea66f`;
- 435 pp, mas sem `Title`, `Author`, `Subject` e `Keywords`;
- texto antigo em pontos como “Registro de ECT”.

O PDF reconstruído e corrigido estava em
`Molambudos_VictoriaRegia/build/molambudos-o-di-rio-do-paciente-1-260.pdf`:

- SHA-256 `3378f438d1124432b1b67fdf29161363e28276bb4a754c2a070bf5b054d56f4b`;
- 435 pp; 453,543 × 651,968 pts = 160 × 230 mm;
- metadados completos;
- 15 fontes, todas embutidas;
- texto corrigido (“Registro de Eletroconvulsoterapia”).

**Decisão:** promover o PDF reconstruído ao caminho canônico, mover o PDF
antigo para a quarentena e, após a revisão do manifesto, excluí-lo
definitivamente; o hash permanece registrado em `reports/r1073/`. Essa é a única
alteração de conteúdo do arquivo canônico nesta rodada; nenhum texto literário
foi reescrito.

## 5. Parecer literário

### 5.1 Forças da edição canônica

- **Polifonia documental.** A alternância entre memória (MEM), documento (DOC),
  lucidez (LUC) e contaminação (CONT) sustenta o efeito de arquivo e evita que o
  romance dependa de uma única voz.
- **Verossimilhança material.** CIP, ISBN, ficha técnica, fac-símiles, aviso de
  ficção histórica e nota de apoio (CVV 188) constroem o pacto de leitura e o
  enquadramento ético.
- **Ética da representação.** O texto nomeia Barbacena e os campos do Ceará como
  história real, mas localiza o horror nas instituições, não nas vítimas.
- **Circulação do motivo.** O “ciclo de contaminação” dá ao leitor uma função
  narrativa: ele não apenas lê o diário, ele é convidado a ocupar o número
  seguinte. É a ideia estrutural mais forte do livro.
- **Fechamento.** O epílogo e o material de arquivo permitem reler o conjunto
  como dossiê, não como coletânea de fragmentos.

### 5.2 Riscos e limites

- **Saturação de motivos.** A auditoria registra 162 ocorrências de “cheiro”,
  123 de “vala”, 103 de “fome”, 35 de “olho amarelo” e 27 de “paciente 1.263”.
  Contagem não é veredito, mas indica onde a leitura corrida precisa decidir
  entre condução e repetição.
- **Densidade documental.** A canônica tem 435 pp e muitos DOC/CONT. O leitor
  iniciante pode ter dificuldade de entrar; a edição ilustrada linear resolve
  melhor a entrada, mas está incompleta.
- **Galerada humana.** Persistem underfull vbox e 50 underfull hbox; é preciso
  revisar viúvas, órfãs, aberturas de página e ilustrações em resolução integral.
- **Acessibilidade digital.** O PDF não é tagged. A rodada R1074 gerou um EPUB
  de leitura (84 fragmentos), mas ele não passou por EPUBCheck; não há PDF/UA.
- **Preflight KDP.** Capa, sangria, código de barras, ISBN e página final ainda
  exigem conferência no preflight oficial. O Book Studio não certifica PDF/X.

### 5.3 v2 — o que ela tem de único

`Molambudos_v2` não é apenas uma canônica curta. Ela:

- troca o número do prontuário (1.263) e organiza a descida em **sete
  concessões**;
- inclui o ensaio “Anatomia de uma Voz que Convence”, que explicita técnicas de
  manipulação;
- traz “Mapa da Descida” e fontes iconográficas;
- tem 112 testes próprios.

O ensaio é valioso como **material companion** ou apêndice crítico. Misturá-lo à
canônica, porém, quebraria o contrato de ficção: o romance funciona porque não
explica o truque dentro da diegese. Por isso a recomendação é preservá-la como
edição alternativa documentada, não fundi-la.

### 5.4 Diário — o que ele tem de único

`Molambudos_v2_Diario` é a edição visual linear:

- 12 capítulos, Partes I–II, com entrada pelo Sertão e pela Colônia;
- gravuras de Piranesi em domínio público, com tratamento sépia;
- capa e ilustrações próprias, inclusive uma variante com “Joaquim e o Olho”;
- 49 pp, 7.254 palavras.

É a versão com melhor **onboarding** e a mais adequada a uma futura edição
ilustrada. Não substitui a canônica porque cobre apenas Parte I–II e não tem o
arco completo, o aparato de publicação nem as traduções. Ela foi preservada em
quarentena e, depois, excluída definitivamente na limpeza autorizada de
2026-11-05. O hash e o inventário permanecem em `reports/r1073/`; uma futura
edição ilustrada exigiria reconstruir o material visual.

### 5.5 Template antigo

`literatura/templates/molambudos-antigo` tem 4 capítulos e 25 pp. É o objeto do
parecer antigo `auditorias/revisao-2026-07.md`, que **não** descreve a edição
VictoriaRegia. Está superado e foi excluído definitivamente em 2026-11-05, com
hash registrado em `reports/r1073/`.

## 6. Decisão de acervo

### Manter no acervo ativo

- `Molambudos_VictoriaRegia/` com o PDF canônico promovido, traduções KDP
  EN/ZH/TRI, capas, dossiê, ficha técnica, fontes `.tex`, fragmentos e figuras.
- `podcast/producao/` (26 episódios + piloto R550, pacotes, slides, feed).
- `auditorias/`, `capas/`, `scripts/`, `specs/`, `meta/`.
- `original/`, `fragmentos/`, `capitulos/`, `misc/`, `relatorios/` como fontes e
  material analítico.
- `README.md`, `REVISAO_FINAL.md` e `release/2026-11-05/`.

### Exclusão definitiva autorizada

Os itens abaixo foram excluídos em 2026-11-05, por decisão explícita do autor,
após revisão do manifesto:

- `Molambudos_v2/` e `Molambudos_v2_Diario/` — edições alternativas com conteúdo
  único; hashes preservados.
- `Molambudos_VictoriaRegia/_archive/` — builds antigos, backups, capas antigas,
  EPUB v1.5.
- layouts não-KDP (`main.pdf`, `main_en.pdf`, `main_zh.pdf`, `main_tri.pdf`,
  `miolo_kdp_160x230mm.pdf`) — substituídos pelas edições KDP 160×230.
- `build/` antigo e PDF canônico antigo `77aabe2e`.
- `_canon_backup_R398/`, `_archive_canon_R407/`.
- rascunhos da raiz (`molambudos.md`, `molambudos-1.txt`, `.bak`).
- template antigo de 25 pp.

O manifesto completo e o hash de cada arquivo permanecem em `reports/r1073/`.

### Exclusão imediata

- artefatos de teste (`test.pdf`, `test_err.pdf`, `.aux`, `.log`, `.toc`,
  `.out`);
- diretórios vazios `anexos/` e `output/`;
- `.aux` de `capitulos/`.

As edições alternativas foram excluídas por decisão explícita do autor. O
manifesto preserva os hashes e o inventário do que existia; não há restauração
dos arquivos excluídos.

## 7. Release

O pacote `release/2026-11-05/` reúne:

- PDF canônico PT-BR 160×230 mm (435 pp, hash `3378f438…`);
- PDFs EN, ZH e trilingue;
- capas completas PT/EN/ZH;
- `metadata.json`, `SHA256SUMS.txt` e `RELEASE_NOTE.md`.

É um pacote local de revisão e entrega. Não é upload à KDP, não é publicação e
não substitui o preflight oficial.

## 8. Limites finais

- Nenhuma validação externa, banca, leitura beta ou certificação profissional.
- Nenhuma declaração de qualidade literária objetiva, nota ou prêmio.
- Nenhuma publicação, envio à KDP ou distribuição.
- Nenhum texto literário canônico foi reescrito; apenas o PDF canônico foi
  promovido ao build corrigido e o acervo foi organizado. As edições
  alternativas foram excluídas por decisão do autor, com registro de hashes em
  `reports/r1073/`.
