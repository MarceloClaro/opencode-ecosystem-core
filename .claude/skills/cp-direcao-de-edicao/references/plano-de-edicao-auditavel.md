# Plano de edição auditável

Antes de renderizar, descreva a linha de tempo em JSON e valide com o Core:

```bash
python3 -m integrations.video_edit_plan validate plano.json
```

O validador confere origem, frames, sobreposição de faixas, crop, legenda,
codec, destino e direitos. Ele não abre o vídeo nem renderiza. Use o resultado
para corrigir o plano, não como prova de qualidade.

Para conferir o arquivo entregue, produza um relatório de metadados com a
ferramenta que você já autorizou e rode:

```bash
python3 -m integrations.video_edit_plan verify plano.json relatorio.json
```

O retorno `render_metadata_matched` confirma apenas dimensões, fps, duração,
codecs e contêiner dentro das tolerâncias. `visual_quality_verified` permanece
`false`.

Formato completo, códigos de erro e limites:
[Edição de vídeo auditável](../../../../docs/EDICAO_VIDEO_AUDITAVEL_R1024.md).

A decisão de direção continua nesta skill; o validador só impede erros
mecânicos que custam retrabalho.
