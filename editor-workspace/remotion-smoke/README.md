# Remotion smoke project

Projeto mínimo para validar o backend Remotion do editor universal.

## Estado

- Remotion CLI **4.0.540** instalado em `node_modules` (244 pacotes).
- Instalação com `npm install --ignore-scripts --no-audit --no-fund`.
- Aceite de licença registrado pelo operador em
  `~/.config/opencode/remotion-license-ack.json` (escopo `install`).
- `remotion --version` → `@remotion/cli 4.0.540`.
- `remotion compositions src/index.ts` → composição `Smoke`, 50 frames,
  25 fps, 1280×720.
- Navegador usado: Chromium do Playwright em
  `~/.cache/ms-playwright/chromium-1252/chrome-linux64/chrome`.

Recibo: `reports/r1043/remotion-install-receipt.json`.

## O que foi e não foi provado

Provado: o projeto empacota, o navegador inicia e a composição é descoberta.

**Não provado:** render, still, bundle de produção, áudio, sincronização,
qualidade visual e aprovação editorial. Render/still/bundle continuam exigindo
`REMOTION_RENDER_APPROVED=1` e decisão do operador.

## Comandos

```bash
cd editor-workspace/remotion-smoke
./node_modules/.bin/remotion compositions src/index.ts \
  --browser-executable=/home/marceloclaro/.cache/ms-playwright/chromium-1252/chrome-linux64/chrome
```

A licença Remotion não é OSI; verifique os termos atuais para o seu caso.
