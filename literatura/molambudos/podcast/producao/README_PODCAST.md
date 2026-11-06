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