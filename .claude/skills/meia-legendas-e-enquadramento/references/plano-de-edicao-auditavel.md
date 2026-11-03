# Plano de edição para legenda e enquadramento

Legenda e crop podem ser descritos no plano de edição e validados antes do
render:

```bash
python3 -m integrations.video_edit_plan validate plano.json
```

O validador calcula CPS por frame (`caracteres não vazios / segundos`), recusa
legenda após o fim do vídeo, sobreposição na mesma faixa e crop fora da origem.
Também avisa quando a proporção do crop difere da saída.

Isso não mede sincronização com a fala real nem verifica se o crop corta o
rosto. Para o arquivo entregue, compare metadados com:

```bash
python3 -m integrations.video_edit_plan verify plano.json relatorio.json
```

O resultado confirma apenas metadados; a conferência visual e a escuta
continuam necessárias. Formato e limites:
[Edição de vídeo auditável](../../../../docs/EDICAO_VIDEO_AUDITAVEL_R1024.md).
