# Podcast Molambudos

Produção real em `producao/`:

- `audio/` — 26 episódios `.m4a` + `podcast_R550.m4a` (piloto) + `SHA256SUMS.txt` e receipts.
- `pacote_editorial_podcast_molambudos/` — pacote editorial completo.
- `pacote_editorial_podcast_molambudos_gh/` — pacote para GitHub/feed.
- `slides_molambudos.pdf` — slides da produção.
- `infografico_molambudos_raw.png` e `infografico_podcast_raw.png`.
- `mindmap_molambudos.json` — mapa mental.
- `podcast_feed.xml` — feed.
- `trailer_podcast.mp4` — trailer.
- `deploy_estatico_cloudflare/` — instruções e código de deploy.
- `README_PODCAST.md` — tracklist, ordem física e notas de honestidade.
- `METADADOS_PODCAST.json` — metadados.

## Teaser geográfico R1096 (fora do feed)

Peça promocional separada, derivada da R1075. A **v2** é a versão recomendada;
a v1 fica para comparação.

### Versão 2 — corte de impacto (recomendada)

- `producao/trailer_geografia_r1096_v2.mp4` — abertura fria sem sussurro,
  corte seco, textura do podcast, leito de 26 vozes e letreiro dos episódios.
- `producao/audio/teaser_geografia_r1096_v2.m4a` — áudio AAC 48 kHz estéreo
  com capa embutida; narração em nível natural (−16,0 LUFS).
- `producao/TEASER_GEOGRAFIA_R1096_V2.json` — metadados, hashes e limites.
- `producao/transcricao_teaser_geografia_r1096_v2.md` — transcrição e camadas
  de áudio.

### Versão 1 — base

- `producao/trailer_geografia_r1096.mp4` — vídeo 1920 × 1080, 30 fps, 76 s.
- `producao/audio/teaser_geografia_r1096.m4a` — áudio AAC 48 kHz estéreo com
  capa embutida.
- `producao/TEASER_GEOGRAFIA_R1096.json` — metadados e hashes.
- `producao/transcricao_teaser_geografia_r1096.md` — transcrição, créditos,
  fontes e limites.

`producao/capa_teaser_geografia_1400.jpg` é compartilhada pelas duas versões:
frente real do livro e contracapa como textura. O teaser **não** foi inserido
em `podcast_feed.xml` e não altera a tracklist, os receipts ou os áudios dos 26
episódios. Voz sintetizada, mapas ilustrativos e retratos ficcionais; nenhuma
publicação automática.

## Estado

- 26/26 episódios presentes; `podcast_R550.m4a` é um piloto adicional.
- Ordem de escuta: ordem física do manuscrito, não numérica linear.
- EP26 = MEM-26 + material de epílogo que não casou o padrão `## MEM-NN`.
- Produção NotebookLM em três janelas por quota; recuperação por `artifact_id`.
- Nenhuma publicação automática; deploy exige autorização.

## Limites

- Áudio gerado por NotebookLM; não é leitura humana validada.
- Metadados e feed não provam qualidade editorial.
- Nenhuma validação externa.
