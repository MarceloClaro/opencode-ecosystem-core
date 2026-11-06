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
