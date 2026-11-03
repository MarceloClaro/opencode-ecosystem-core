# QC de vídeo e animação — checklist

## 1. Fonte e direitos

- [ ] URL/arquivo, autor, data e hash da fonte registrados.
- [ ] Licença da obra e autorização de uso documentadas.
- [ ] Consentimento de voz/imagem quando houver clone ou dublagem.
- [ ] Nenhum dado pessoal, credencial ou conteúdo confidencial no projeto.

## 2. Imagem

- [ ] 1920×1080 (ou 1080×1920) a 30 fps, H.264 High, `yuv420p`.
- [ ] `+faststart` para reprodução progressiva.
- [ ] Rosto, slide e legenda sem colisão; margens de 5–10%.
- [ ] Crop/zoom sem corte de testa, queixo, mãos ou informação essencial.
- [ ] Cor consistente entre planos; sem clipping de branco/preto.
- [ ] Movimento derivado do frame; sem tremor ou zoom nervoso.

## 3. Áudio

- [ ] −16 LUFS integrado; true peak ≤ −1,5 dBTP.
- [ ] 48 kHz, estéreo, AAC 192 kbps.
- [ ] Fala inteligível; sem clipping, bomba ou cortes secos.
- [ ] Música/SFX abaixo da voz; sem mascarar consoantes.
- [ ] Sincronia labial conferida em pelo menos 3 pontos.

## 4. Legenda

- [ ] Até 2 linhas por bloco; ≤17 CPS.
- [ ] Timing conferido contra a fala; sem antecipação/atraso.
- [ ] Acentuação, nomes próprios e números conferidos.
- [ ] Contraste e tamanho legíveis no celular.
- [ ] SRT/ASS preservados para reedição.

## 5. Dublagem e voz

- [ ] Voz sintética identificada como sintética quando exigido.
- [ ] Clone de voz coberto por consentimento; não imita pessoa real sem autorização.
- [ ] Tradução revisada por humano; não é verbatim.
- [ ] Nenhuma promessa, opinião ou endosso inventado.

## 6. Lip sync

- [ ] Boca acompanha a nova trilha em fala, pausa e transição.
- [ ] Sem tremer, derreter ou trocar identidade.
- [ ] Chunking sem salto visível nas emendas.
- [ ] Qualidade compatível com o uso declarado; não declarar “profissional” sem revisão.

## 7. Entrega

- [ ] 16:9, 9:16 e 1:1 derivados do mesmo master.
- [ ] Nome e versão claros; original preservado.
- [ ] Manifesto com SHA-256, `ffprobe`, loudness e decisões.
- [ ] Nada publicado sem autorização e revisão final.

## 8. O que o QC automático não prova

`ffprobe` e R1024 provam container, duração, dimensões, codecs, legendas e
metadados. Não provam qualidade visual, sincronia labial, inteligibilidade,
adequação editorial ou direitos. Esses pontos exigem olho, ouvido e revisão
humana.
