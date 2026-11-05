# R1059 — prévia “Monte Roraima” (estudo de estilo)

Prévia vertical de **10 s** que recria a *linguagem visual* de um explicador
fornecido pelo usuário, sem reutilizar sua marca, voz, textos ou assets.

| Item | Valor |
|---|---|
| Arquivo | `out/roraima-preview-final.mp4` |
| Formato | **720×1280, 9:16, 30 fps, 300 frames, 10,000 s** |
| Tamanho | **1.486.095 bytes** |
| SHA-256 | `dfe16e765371ae29f8aab77df361c8db35978dee9ba2c170cfd403f55d9fe7d4` |
| Voz | Edge TTS `pt-BR-FranciscaNeural` (sintética) |
| Motores | Motion Canvas 3.17.2 + Remotion 4.0.540 |
| QC | aprovado: −14,47 LUFS · true peak −4,51 dBTP · 0 s de preto |

## O que a prévia mostra

1. Mapa da América do Sul com zoom lento até a tríplice fronteira.
2. Mesa de pedra ilustrada, com nuvens na base e estratos sedimentares.
3. Legendas-pílula em amarelo, uma ideia por batida.
4. Linhas tracejadas até as etiquetas de **Brasil, Venezuela e Guiana**.
5. Pulso no platô e crédito de fontes no rodapé.

## Como foi produzido

- **Referência:** MP4 de 82,17 s, 720×1280, 30 fps, obtido por HTTPS sem
  autenticação. A URL assinada não é armazenada; a mídia não é redistribuída.
- **Análise:** 9 folhas de contato a 2 fps, sondagem `ffprobe`, detecção de
  cenas e transcrição automática. Cobertura **parcial** — ver
  `reference/referencia-de-edicao.md`.
- **Motion Canvas:** cena vetorial original `src/tepui.tsx`, exportada como
  300 PNG RGBA por um renderer local no navegador.
- **Remotion:** composição `src/r1059-roraima/RoraimaVideo.tsx` posiciona o
  mapa por coordenadas WGS84, sobrepõe os frames RGBA, legendas e etiquetas.
- **Áudio:** locução própria escrita para o piloto, sintetizada localmente e
  normalizada para −14 LUFS.

## Reproduzir

```bash
# 1. dependências isoladas do Motion Canvas
cd editor-workspace/r1059-motion-canvas
npm install --ignore-scripts --no-audit --no-fund
npm run start            # http://127.0.0.1:5199/export.html

# 2. exportar os frames (via navegador/Playwright)
#    window.startPilot() grava output/r1059-tepui-v1/000000.png … 000299.png
cp output/r1059-tepui-v1/*.png ../remotion-smoke/public/r1059-tepui/

# 3. conferir assets
python3 pilots/r1059-roraima/build_assets.py --check-frames

# 4. renderizar a composição
cd editor-workspace/remotion-smoke
REMOTION_RENDER_APPROVED=1 node node_modules/@remotion/cli/remotion-cli.js \
  render src/r1059-roraima/EntryRoraima.tsx RoraimaStudy \
  ../../pilots/r1059-roraima/out/roraima-visual.mp4 --concurrency=4 --crf=18
```

O master aprovado não é sobrescrito por esse comando: ele grava um visual
intermediário. O mux com áudio e `loudnorm` está descrito no recibo
`out/render-receipt.json`.

## Fontes, licenças e limites

- **Mapa:** EOX::Maps *Terrain* (WMS), com dados de OpenStreetMap, Natural
  Earth, NASA e outros; crédito visível no vídeo. Uso não comercial; não
  redistribuir como mapa autônomo.
- **Ilustração:** vetorial original deste projeto, sem assets da referência.
- **Voz:** sintética; nenhuma clonagem da voz do narrador original.
- **Bandeiras:** faixas de cor simplificadas, não brasões oficiais.
- **Mapa ilustrativo:** projeção equirretangular, relevo generalizado e ponto
  triplo aproximado; não serve como limite oficial.
- **Altitude:** “cerca de 2.800 m” conforme o roteiro fornecido; valores
  publicados variam conforme o ponto medido.
- **Cobertura:** a referência foi amostrada a 2 fps e o áudio transcrito por
  ASR; não houve escuta humana nem confirmação de todos os cortes.
- **Direitos:** a referência não transfere licença sobre sua marca, imagens,
  voz, música ou roteiro. O piloto é um estudo de composição, não uma cópia.
- **Sem publicação:** nada foi enviado a plataformas; nenhuma validação
  externa ou revisão humana foi registrada.
