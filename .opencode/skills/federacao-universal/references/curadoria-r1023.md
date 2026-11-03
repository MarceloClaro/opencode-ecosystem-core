# Curadoria R1023 — federação de repositórios

Esta nota acompanha o manifesto `federation/repository-curation-r1023.json`.
Ela é referência de leitura, não instalação.

## Regras aprendidas

1. **Fixe o commit.** Um README na branch padrão muda; o registro precisa do
   SHA consultado e do hash de cada documento lido.
2. **Separe as licenças.** Licença do código não cobre o corpus, os dados, os
   modelos, as marcas nem os links para outros repositórios.
3. **Separe descoberta de execução.** Constar no manifesto não significa que o
   projeto foi clonado, compilado, instalado ou executado.
4. **Trate fork como fork.** O conteúdo de um fork pode divergir do upstream;
   o manifesto registra o commit do fork efetivamente lido.
5. **Não transforme lista em catálogo executável.** Um índice de projetos não
   autoriza baixar ou rodar os projetos listados.

## Casos que motivaram cautela

- `book-to-skill`: o próprio projeto publica aviso de re-upload malicioso com
  desativação de TLS, coleta de dados locais e payload executável. O commit
  auditado é o do fork autorizado pelo usuário, mas a lição vale para qualquer
  instalação futura: conferir origem oficial antes de executar.
- `ciencia-de-dados-cibele-russo`: material derivado em CC BY-NC-SA 4.0, com
  vídeos originais fora da licença. Não é adequado a incorporação comercial.
- `leis_brasileiras`: licença MIT apenas para `scripts/`; o README declara que
  as conversões automáticas e o OCR não substituem o Diário Oficial.
- `remotion-dev/chromium`: espelho de árvore imensa; não há justificativa para
  clone ou build nesta rodada.

## Uso no Core

O manifesto serve para auditoria e roteamento de leitura. Para adotar um
componente, siga o fluxo da skill `federacao-universal`: proposta desativada,
licença explícita, prova de instalação isolada e autorização do operador.
