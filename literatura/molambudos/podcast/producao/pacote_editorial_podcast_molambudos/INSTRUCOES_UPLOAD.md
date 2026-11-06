# 📤 Instruções de Upload — Podcast Molambudos (26 episódios)

> Pacote gerado e verificado em 2026-09-22.
> Todos os arquivos têm sha256 registrado em `METADADOS_PODCAST.json` e `audio/SHA256SUMS.txt`.

---

## 1. Conteúdo do pacote

| Item | Arquivo | Observação |
|---|---|---|
| 26 episódios | `audio/podcast_epNN_memXX.m4a` | m4a (AAC 44100 Hz stereo), ~31–39MB cada |
| Capa do podcast | `capa_podcast.jpg` | 1400×1400 px (exigência mínima das plataformas) |
| Feed RSS | `podcast_feed.xml` | RSS 2.0 + namespace podcasting (26 itens) |
| Infográfico 1 | `infografico_molambudos.png` | Material de divulgação |
| Infográfico 2 (podcast) | `infografico_podcast.png` | Idem |
| Mapa mental | `mindmap_molambudos.json` | Idem |
| Apresentação | `slides_molambudos.pdf` | 15 slides, material de divulgação |
| Preview 30s | `preview_ep01_30s.m4a` | Trailer/amostra para redes sociais |
| Metadados | `METADADOS_PODCAST.json` | Título, descrição, sha256, origens |
| Guia | `README_PODCAST.md` | Tracklist, ordem técnica, notas honestas |

**Título sugerido:** Molambudos — O Diário do Paciente 1.260 (Série em Áudio)
**Autor:** Marcelo Dias de Carvalho Filho (coautor: Marcelo Claro)
**Gênero:** Horror literário / Ficção especulativa / Narrativa imersiva em segunda pessoa

**Descrição padrão para as plataformas:**
> Uma série imersiva em áudio de 26 episódios baseada no romance "Molambudos — O
> Diário do Paciente 1.260". Do sertão do Ceará ao Hospital Colônia de Barbacena,
> o diário de Joaquim Antônio Correia atravessa décadas — e contamina quem lê.
> Você é o Paciente 1.263.

⚠️ **AVISO obrigatório (conteúdo):** a obra contém representações ficcionais de
violência institucional psiquiátrica (eletrochoque, lobotomia, cárcere), fome e
morte, descrições médicas explícitas e narrativa em segunda pessoa. Incluir
aviso de conteúdo em todas as plataformas.

---

## 2. Fluxo recomendado (pipeline de publicação)

```
┌────────────────────────────────────────────────────────────────────┐
│  1. HOSPEDAGEM DO FEED (ex.: GitHub Pages, Cloudflare Pages,       │
│     Vercel, Netlify, S3+CloudFront — qualquer host estático)       │
│        → publicar podcast_feed.xml + capa_podcast.jpg              │
│        → obter URL pública do feed (ex.: https://site/feed.xml)    │
│                                                                     │
│  2. AGREGADOR/PLAYER INDEPENDENTE (ex.: Podverse, AntennaPod,      │
│     Podcast Index)                                                  │
│        → adicionar a URL do feed via pAdmin (Podcast Index)        │
│                                                                     │
│  3. DISTRIBUIDORES PRINCIPAIS (Spotify, Apple Podcasts, YouTube)   │
│        → ver seções 4–6                                             │
│                                                                     │
│  4. DIVULGAÇÃO: preview 30s + infográficos + slides + mind map     │
│     (redes sociais; ver seção 7)                                    │
└────────────────────────────────────────────────────────────────────┘
```

**IMPORTANTE — onde os áudios ficam:** o feed RSS referencia cada episódio por
uma URL pública de áudio (tag `<enclosure url="...">`). Hoje o `podcast_feed.xml`
usa caminhos locais/relativos (`audio/podcast_ep01_mem01.m4a`). **Antes de
publicar**, substitua as URLs do feed pelos endereços públicos dos 26 arquivos
m4a (faça upload dos áudios para o host escolhido e reescreva cada `<enclosure>`).
Alternativa: usar um distribuidor que hospede os áudios (Anchor/Spotify for
Podcasters, Podbean, Buzzsprout) — nesse caso o feed é gerado pelo distribuidor e
você só envia os m4a + capa + metadados no painel web.

---

## 3. Pré-requisitos técnicos (já atendidos)

- [x] Áudios em m4a/AAC 44100 Hz stereo (compatível com todas as plataformas)
- [x] Duração real registrada por episódio (feed usa duração estimada a 257kbps;
      após hospedar os m4a, confirme com `ffprobe`/player — ver `README_PODCAST.md`)
- [x] Capa 1400×1400 px (mínimo exigido: 1400×1400; máx. recomendado: 3000×3000)
- [x] Feed RSS 2.0 com namespace podcasting (`podcast_feed.xml`)
- [x] GUIDs estáveis (sha256 do arquivo) — não mudam entre re-uploads
- [ ] **PENDENTE:** URLs públicas dos 26 m4a (depende do host escolhido)

---

## 4. Spotify (via Spotify for Podcasters)

1. Crie conta em **spotifyforpodcasters.com** (grátis) com a conta Spotify.
2. **Novo programa** → cole a URL pública do feed RSS (`https://seusite/feed.xml`).
3. O Spotify valida o feed; se tudo ok, preenche automaticamente capa, título,
   descrição e episódios.
4. Aguarde a aprovação (normalmente dias). Acompanhe em "Programas → Status".
5. **Nota:** Spotify hoje também permite hospedar direto (sem feed), enviando os
   arquivos m4a + capa pelo painel — escolha "Importar por RSS" se já tiver o
   feed público, ou "Hospedar no Spotify" se preferir simplificar.

## 5. Apple Podcasts (Apple Podcasts Connect)

1. **podcastsconnect.apple.com** → "Podcaster" → valide o Apple ID.
2. Role até **"Enviar um programa"** → cole a URL do feed público.
3. O Apple fará a validação técnica (exige capa 1400×1400, feed UTF-8, título
   ≤75 caracteres). Corrija o que apontar e reenvie.
4. **Aprovação:** normalmente 1–5 dias úteis. O primeiro episódio pode levar até
   24h para aparecer após aprovação.
5. **Importante:** `<itunes:category>` já está definido no feed (Fiction → Drama /
   Horror). Mantenha os GUIDs — eles não podem mudar para não duplicar episódios.

## 6. YouTube (YouTube Studio / Podcasts)

1. **Podcasts no YouTube:** YouTube Studio → "Conteúdo" → "Podcasts" → "Importar
   do RSS" → cole a URL do feed público.
2. YouTube gera automaticamente vídeos de áudio (estático com capa) para cada
   episódio.
3. Alternativa manual: publicar cada m4a como vídeo usando `slides_molambudos.pdf`
   ou a capa como imagem de fundo (a geração de vídeo fica a cargo do editor).
4. **Descrição/aviso:** adicione o AVISO de conteúdo + link para o livro
   (`projetos/molambudos/`) em cada vídeo.

---

## 7. Divulgação (matérias prontas no pacote)

- **Trailer 30s:** `preview_ep01_30s.m4a` → Instagram Reels/TikTok/Shorts
  (converta para vídeo com a capa estática + o trecho de áudio).
- **Infográficos:** `infografico_molambudos.png` (Protocolo de Contágio) e
  `infografico_podcast.png` (jornada + cadeia 1.260→1.263) → posts/grid.
- **Slides:** `slides_molambudos.pdf` (15 págs) → carrossel no LinkedIn/Instagram.
- **Mind map:** `mindmap_molambudos.json` → use para roteiro de vídeo/live sobre
  a estrutura (ou converta com ferramenta de visualization de JSON).

---

## 8. Checklist final antes de publicar

1. ☐ Hospedar os 26 m4a e o `podcast_feed.xml` em host público (HTTPS).
2. ☐ Substituir `<enclosure url="...">` no feed pelas URLs públicas dos m4a.
3. ☐ Confirmar duração de cada episódio no feed (ajustar se divergir >5s).
4. ☐ Publicar `capa_podcast.jpg` em URL pública e atualizar `itunes:image`.
5. ☐ Testar o feed: valide em validator.w3.org/feed e em Podbase
   (podbase.org/validate) ou Cast Feed Validator.
6. ☐ Submeter o feed ao Podcast Index (pAdmin) + Spotify + Apple + YouTube.
7. ☐ Publicar materiais de divulgação (seção 7) com o AVISO de conteúdo.

---

## 9. Rastreabilidade (provas)

- **Registro de evolução:** R561 (infográfico 1), R562 (infográfico podcast),
  R563 (mind map + slides), R564 (preview + instruções) — `evolution/cycles.json`,
  409+ ciclos.
- **Integridade:** `audio/SHA256SUMS.txt` (26 m4a) + `METADADOS_PODCAST.json`
  (sha256 de todos os artefatos) — gate zip-vs-físico 14/14 após R563.
- **Origem:** todos os áudios, capa composta e artifacts (infográficos, mind map,
  slides) gerados/baixados via CLI real do NotebookLM (`nlm`) e verificação local
  (OCR, PIL, ffmpeg, mutagen). Nenhuma alegação sem prova física.