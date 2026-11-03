# Plano de edição na revisão

Na revisão, valide o plano antes de discutir acabamento:

```bash
python3 -m integrations.video_edit_plan validate plano.json
python3 -m integrations.video_edit_plan verify plano.json relatorio.json
```

`validate` encontra sobreposição, corte fora da origem, legenda ilegível,
codec incompatível e destino que sobrescreve o original. `verify` compara
dimensões, fps, duração, codecs e contêiner do arquivo entregue com o plano.

Nenhum dos dois prova qualidade visual, sincronização da fala ou loudness
medido. Use os códigos para corrigir uma causa por vez e preservar o material
aprovado. Formato completo:
[Edição de vídeo auditável](../../../../docs/EDICAO_VIDEO_AUDITAVEL_R1024.md).
