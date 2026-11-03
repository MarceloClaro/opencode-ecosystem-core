# Curadoria R1023 — Remotion para edição audiovisual

Referência do guia oficial da skill Remotion (`remotion-dev/codex-plugin`,
MIT, commit `d65ee2b49d83dd9259f101cf1ebeecd036ef904c`). O plugin não foi
instalado e nenhum comando `npx` foi executado.

## O que o guia acrescenta aos fluxos cp-*

- **Prévia antes de renderizar.** Quando o projeto já roda, abra o Studio e
  confira a composição antes de editar ou renderizar. A prévia interativa é o
  padrão; render é exceção.
- **Render só por pedido explícito.** "Renderize", "exporte" ou "dê-me o MP4"
  são pedidos claros. "Faça um vídeo" não autoriza render.
- **Preserve mudanças do usuário.** Se aparecer alteração inesperada no código,
  não sobrescreva: pergunte ou trate como intencional.
- **Diagnóstico de ambiente.** Falha de watcher (`EMFILE`) pede polling; erro
  de sandbox do Chromium pode ser do host, não do projeto.

## Como usar sem overclaim

Essas regras orientam decisão editorial e evitam render prematuro. Elas não
provam que Remotion está instalado, que o Studio abre neste host, que a
composição é boa ou que o vídeo final foi produzido. A skill `cp-direcao-de-edicao`
continua responsável por decidir o que mostrar; esta referência só condiciona
quando uma prévia ou render faz sentido.

Licença MIT cobre o plugin, não o produto Remotion, os modelos, as mídias ou
serviços de terceiros.
