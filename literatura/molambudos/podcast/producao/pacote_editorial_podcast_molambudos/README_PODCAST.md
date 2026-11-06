# 🎧 Podcast Molambudos — Episódio por Capítulo

**Pacote editorial final — 26 episódios de áudio real (1 por entrada do diário)**
Produzido via NotebookLM (`nlm` CLI v0.11.6) pelo executor físico SPEC-973
(`agent_runners/nlm_executor.py`), com verificação de integridade criptográfica.

- Data de produção: 2026-09-22
- Formato: `.m4a` (AAC-LC, gerado pelo NotebookLM — Deep Dive, idioma pt-BR)
- Volume total: **~1.014 MB** (26 arquivos)
- Verificação: `SHA256SUMS.txt` (gerado no diretório `audio/`)

---

## Tracklist (ordem de escuta recomendada = ordem do manuscrito físico)

> **Nota editorial importante**: o manuscrito *Molambudos — O Diário do Paciente
> 1.260* **não apresenta os capítulos em ordem numérica linear** na sua forma
> física. A sequência real das entradas do diário é:
> `MEM-01..11 → MEM-17 → MEM-18 → MEM-12 → MEM-21 → MEM-19 → MEM-22 → MEM-23
> → MEM-20 → MEM-24 → MEM-25 → MEM-13..16 → MEM-26`.
> Os episódios seguem essa ordem **física** (recomendada para leitura/escuta
> continuada). Cada arquivo usa `epNN` = posição na ordem física e `memXX` =
> número real do capítulo no manuscrito.

| # | Arquivo | Capítulo real | Áudio |
|---|---------|---------------|-------|
| EP01 | `podcast_ep01_mem01.m4a` | MEM-01 — O Sertão Antes do Fim | 31.8MB |
| EP02 | `podcast_ep02_mem02.m4a` | MEM-02 — A Caminhada dos Retirantes | 44.4MB |
| EP03 | `podcast_ep03_mem03.m4a` | MEM-03 — A Morte do Pai | 21.4MB |
| EP04 | `podcast_ep04_mem04.m4a` | MEM-04 — A Vala | 20.7MB |
| EP05 | `podcast_ep05_mem05.m4a` | MEM-05 — O Olho Amarelo | 17.9MB |
| EP06 | `podcast_ep06_mem06.m4a` | MEM-06 — O Curral do Governo | 42.9MB |
| EP07 | `podcast_ep07_mem07.m4a` | MEM-07 — A Mãe Levada | 51.1MB |
| EP08 | `podcast_ep08_mem08.m4a` | MEM-08 — A Chegada ao Colônia | 69.6MB |
| EP09 | `podcast_ep09_mem09.m4a` | MEM-09 — Os Primeiros Anos | 37.0MB |
| EP10 | `podcast_ep10_mem10.m4a` | MEM-10 — O Primeiro Homicídio | 21.8MB |
| EP11 | `podcast_ep11_mem11.m4a` | MEM-11 — O Isolamento | 52.0MB |
| EP12 | `podcast_ep12_mem17.m4a` | MEM-17 — O Eletrochoque | 46.4MB |
| EP13 | `podcast_ep13_mem18.m4a` | MEM-18 — A Tentativa de Fuga | 38.0MB |
| EP14 | `podcast_ep14_mem12.m4a` | MEM-12 — A Rasga Mortalha | 42.7MB |
| EP15 | `podcast_ep15_mem21.m4a` | MEM-21 — O Jornal | 17.1MB |
| EP16 | `podcast_ep16_mem19.m4a` | MEM-19 — O Visitante | 58.2MB |
| EP17 | `podcast_ep17_mem22.m4a` | MEM-22 — As Vozes | 47.2MB |
| EP18 | `podcast_ep18_mem23.m4a` | MEM-23 — A Neve de Cinzas | 48.2MB |
| EP19 | `podcast_ep19_mem20.m4a` | MEM-20 — A Morte do Vizinho de Cela | 49.9MB |
| EP20 | `podcast_ep20_mem24.m4a` | MEM-24 — A Enfermeira que Chorava | 16.7MB |
| EP21 | `podcast_ep21_mem25.m4a` | MEM-25 — A Morte no Espelho | 39.9MB |
| EP22 | `podcast_ep22_mem13.m4a` | MEM-13 — O Médico Novo | 31.1MB |
| EP23 | `podcast_ep23_mem14.m4a` | MEM-14 — O Diário Emerge | 36.7MB |
| EP24 | `podcast_ep24_mem15.m4a` | MEM-15 — A Entidade Fala | 46.8MB |
| EP25 | `podcast_ep25_mem16.m4a` | MEM-16 — A Morte no Colônia | 57.0MB |
| EP26 | `podcast_ep26_mem26.m4a` | MEM-26 — A Última Página | 27.7MB |

---

## Notas editoriais de honestidade técnica (anti-overclaim)

1. **EP26 — conteúdo ampliado por limite de segmentação**: o trecho que originou
   o EP26 contém o capítulo MEM-26 **mais** todo o material posterior do
   manuscrito que não casa o padrão de cabeçalho `## MEM-NN` (ex.: o header
   `## 🪦 MEM-27 — A Última Página` inicia com emoji e ficou fora da
   segmentação; também DOC-09, escalas de contaminação, avaliação do paciente
   1.261 etc.). Portanto o EP26 deve ser entendido como **"MEM-26 + epílogo
   material do manuscrito"** — decisão editorial consciente registrada como
   lição R557 no EvolutionRegistry.

2. **Rate limit real do servidor**: a produção total foi concluída em **três
   janelas** (lote 2..15; retomada 16..26; recuperação de downloads), porque o
   NoteboookLM impõe cota de geração (`RESOURCE_EXHAUSTED`) após ~15 episódios
   consecutivos. Não houve perda de dados: todo áudio pendente foi recuperado
   a partir do `artifact_id` gravado nos receipts — **26/26 presentes**.

3. **Ordenação física, não linear**: ver tracklist acima. Os nomes dos arquivos
   carregam o capítulo real (`memXX`) para evitar ambiguidade (lição R554).

4. **Integridade**: cada receipt (`receipt_epNN.json`) guarda o sha256 do áudio
   correspondente; `SHA256SUMS.txt` no diretório `audio/` consolida os 26.

---

## ReproProdução (comandos reais usados)

1. Segmentação física: `agent_runners/nlm_executor.py::segmentar_por_capitulo(texto)`
   (autodetect `## MEM-NN`, fabuloso determinístico, gate sha256 48/48).
2. Geração de um episódio: `NlmPodcastExecutor.create_notebook → add_source_text
   → create_audio(fmt="deep_dive", length="long", language="pt-BR") → download`.
3. Lote em background: `setsid nohup python3 research/producao_real/gerar_episodios.py`
   (já substituído pelo runner resiliente `retomar_episodios.py` com backoff
   anti-rate-limit e recuperação `recuperar_downloads.py`).

---

## Conteúdo do pacote

- `audio/*.m4a` — 26 episódios
- `audio/SHA256SUMS.txt` — digest consolidado
- `audio/receipt_epNN.json` — metadados + sha256 por episódio (proveniência)
- `README_PODCAST.md` — este documento
- `gerar_episodios.py` / `retomar_episodios.py` / `recuperar_downloads.py` / `gerar_ep26.py`
  — pipeline executável (reprodutibilidade)
---

## Material gráfico adicional

- **`infografico_molambudos.png`** — infográfico gerado pelo NotebookLM a partir do
  notebook canônico *Molambudos — O Diário do Paciente 1.260* (download via
  `nlm download infographic`, artifact `46393e94…`, status `completed`).
  Conteúdo verificado por OCR: "Protocolo de Contágio — O Ciclo da Contaminação:
  Do Prontuário 1.260 ao Leitor" (cadeia de hospedeiros). 2752×1536 RGBA.

- **`infografico_podcast.png`** — segundo infográfico, gerado via chat do NotebookLM
  (`nlm notebook query` → novo artifact `76354c2f…`, status `completed`), focado na
  série de podcast: jornada do paciente pelos capítulos, temas do diário e cadeia
  de contágio do leitor (Mensagem: "Crie um novo infográfico... diferente do anterior").
  Conteúdo verificado por OCR: 62 anos de cárcere em Barbacena, transmissão por
  hospedeiros da cadeia 1.260→1.263. 2752×1536 RGBA.

- **`mindmap_molambudos.json`** — mapa mental da estrutura narrativa (JSON),
  gerado via chat do NotebookLM (`nlm download mind-map`, artifact `89ee21db…`);
  contém arquitetura em 5 partes, rotas hipertextuais e 3 atos.
- **`slides_molambudos.pdf`** — apresentação em slides (15 páginas, 19MB),
  gerada via chat do NotebookLM (`nlm download slide-deck`, artifact
  `99a7c298…`, geração ~9min). OCR confirma: "Uma série imersiva em áudio de
  26 episódios", "A Cadeia de Contágio Narrativo 1.260→1.263", página final
  "O paciente 1.260 morreu para que você escutasse."

## Distribuição

- **`INSTRUCOES_UPLOAD.md`** — guia passo a passo para publicar o podcast
  (host do feed, Podcast Index, Spotify for Podcasters, Apple Podcasts Connect,
  YouTube Studio/Podcasts) com checklist final.
- **`preview_ep01_30s.m4a`** — trailer de 30s (início do EP01 com fades de 2s;
  AAC 128kbps; duração 30.00s validada por ffmpeg e mutagen) para redes sociais.

## Divulgação adicional

- **`trailer_podcast.mp4`** — vídeo promocional de 30s (capa com efeito Ken Burns
  + áudio do preview; H.264 1080×1080 25fps + AAC; sha256 `25b06431…`).
  Pronto para Instagram Reels / TikTok / YouTube Shorts.
- **`index_podcast.html`** — página de destino do podcast (landing page): capa,
  trailer com player, 26 players de áudio, aviso de conteúdo, infográficos,
  slides, feed, metadados e instruções de upload. Basta hospedar junto com os
  demais arquivos do pacote (ou usar como base para a página oficial).

## Mind map em Mermaid

O mind map do NotebookLM (`mindmap_molambudos.json`) foi convertido para sintaxe
**Mermaid** (`mindmap_molambudos.mmd`) e renderizado em **SVG**
(`mindmap_molambudos.svg`) localmente com a biblioteca Mermaid v11 headless
(jsdom + dompurify + canvas nativo + stub `getBBox` — sem necessidade de
navegador/Chromium). O `index_podcast.html` agora inclui seção dedicada com o
SVG exibido e o código Mermaid colapsável (fonte editável do diagrama; pode ser
aberto em mermaid.live).

## Correção do mind map (R567)

- **SVG corrigido**: o render inicial via stub jsdom produzia `viewBox="-10 -10
  228685.92 41.6"` (layout colapsado — SVG em branco). Regenerado com
  `mermaid-cli` (mmdc) + Chromium real via Puppeteer: `viewBox="5 5 1643.94
  852.17"` (layout radial correto, 46 labels).
- **Mermaid DINÂMICO no index**: o bloco hardcoded foi removido. O
  `index_podcast.html` agora carrega `mindmap_molambudos.mmd` via `fetch()` e
  renderiza no navegador com a biblioteca Mermaid v11 (CDN jsdelivr) na div
  `#mermaid-live`. Edite o `.mmd` e recarregue a página — o diagrama e o código
  atualizam automaticamente. Fallback para o SVG estático se o CDN falhar.

## Acesso público (túnel)

- **Link ativo (temporário):** https://imported-exec-institute-looksmart.trycloudflare.com/index_podcast.html
- Tipo: Cloudflare quick tunnel (`cloudflared tunnel --url http://127.0.0.1:8090`),
  processo PID 96298; URL muda se o túnel for reiniciado.
- Testado via internet: 7/7 assets 200 OK.
- Para link permanente: usar domínio próprio + Cloudflare Tunnel nomeado (arquivo de config),
  ou hospedar o pacote em host estático (GitHub Pages/Cloudflare Pages) com os 26 m4a + feed.
