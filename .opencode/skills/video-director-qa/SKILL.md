---
name: video-director-qa
description: Dirija e verifique vídeos code-rendered com plano mensurável, gates por
  fase, contato de frames, loudness, silêncio e frames pretos. Use antes e depois
  do render; não copia o skill original, não renderiza sem aprovação e não confunde
  QC técnico com qualidade editorial.
metadata:
  round: R1049
  source: https://github.com/win4r/video-director
  license: MIT
  adaptation: Adaptação textual original inspirada em win4r/video-director (commit
    4747e5c153509ef7f8f7fd1a0aad6acfda36280d); scripts próprios do Core, sem cópia.
---

# Video director QA

## Antes do render

- Plano em números: duração, fps, resolução, cenas, texto, áudio.
- Cada cena tem função, asset e critério de revisão.
- A transição mais difícil aparece na amostra.
- Dados, CTA, nomes e oferta são os confirmados.

## Depois do render

Use o QC local:

```bash
python3 scripts/video_qa.py --video saida.mp4 --out qa.json   --expect-frames 600 --expect-fps 30/1 --contact-sheet contato.png
```

O relatório cobre streams, frames decodificados, fps, duração, loudness,
silêncio e frames pretos. Contato de frames ajuda a inspeção visual; não a
substitui.

## Gates

1. Plano válido antes de executar.
2. Render termina e arquivo existe.
3. Streams e frames conferem.
4. Áudio não está mudo/clipado; loudness dentro da faixa declarada.
5. Contato visual sem frame preto inesperado.
6. Nenhuma aprovação estética automática.

## Limites

O QC não ouve, não entende ironia, não valida tradução e não prova sincronia
labial. Esses pontos exigem revisão humana. A skill não instala dependências.
