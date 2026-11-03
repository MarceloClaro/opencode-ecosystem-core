# Remotion: CLI e API verificados
## Escopo
Referência de apoio para implementar ou revisar uma edição Remotion. Os comandos foram conferidos na documentação oficial em 1º de novembro de 2026. A disponibilidade local, a versão instalada e a licença aplicável precisam ser confirmadas no projeto; documentação não é prova de execução.

## Requisitos e criação
- Node.js 16 ou superior, ou Bun 1.0.3 ou superior, conforme a página de instalação.
- Linux requer glibc 2.35 ou superior e dependências de sistema adicionais; macOS requer versão suportada pela documentação vigente.
- Projeto novo em branco:
  `npx create-video@latest --yes --blank my-video`
- Alternativa interativa:
  `npx create-video@latest`
- Iniciar o Studio no projeto:
  `npm run dev`

## Agent Skills do Remotion
- Instalação global, que altera o ambiente do usuário:
  `npx -y skills@latest add remotion-dev/skills -g -y`
- Instalação dentro do projeto, quando disponível na versão instalada:
  `npx remotion skills add`
- Essas ações instalam conteúdo de terceiros. Exigem autorização e revisão da origem/licença; não são necessárias para apenas escrever instruções de edição.

## Render e still
- Render básico, usando o ID da composição:
  `npx remotion render HelloWorld`
- Render com codec e caminho de saída:
  `npx remotion render --codec=vp8 HelloWorld out/video.webm`
- Still de uma composição:
  `npx remotion still --props='{"custom":"data"}' my-comp out.png`
- O ID da composição e os argumentos disponíveis dependem do projeto. Confirme no Studio ou na configuração antes de prometer um comando.

## Animação e 3D
- Em Remotion, derive movimento, sincronização eduração dos frames da composição. Não use CSS animations, transitions ou timers como relógio de movimento.
- Para 3D documentado, a integração usa Three.js e React Three Fiber por `ThreeCanvas` de `@remotion/three`. Confirme a versão, as dependências e o ambiente de renderização no guia oficial.
- Uma aparência em perspectiva não comprova geometria 3D; uma máscara aproximada não comprova canal alfa.

## Links oficiais
- Instalação: https://www.remotion.dev/docs
- API: https://www.remotion.dev/docs/api
- Render: https://www.remotion.dev/docs/render
- Still: https://www.remotion.dev/docs/stills
- Agent Skills: https://www.remotion.dev/docs/ai/skills
- Three.js: https://www.remotion.dev/docs/three
- Repositório: https://github.com/remotion-dev/remotion
- Licença: https://www.remotion.dev/docs/license

## Limites
- O endereço `https://www.remotion.dev/docs/cli/` retornou 404 na data da conferência. Os comandos acima foram confirmados por páginas oficiais equivalentes e pelo índice de documentação; não trate o 404 como prova de que o comando não existe.
- A licença do Remotion tem condições específicas e pode exigir licença empresarial. Verifique antes de uso comercial.
- Nenhum comando desta referência foi executado nesta revisão. A aprovação de uma skill não autoriza instalar, renderizar, publicar ou contratar serviços.
