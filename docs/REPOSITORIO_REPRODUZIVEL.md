# Fontes reproduzíveis e estado local

O repositório contém fontes do Core, testes, especificações, documentação e assets
necessários ao livro. Perfis gerados pelo setup REA, evidências de alvos, memória
de execução, capturas do navegador e pedidos locais de plugins ficam na máquina.
A configuração é criada novamente por `rea setup`; não deve ser copiada de outro
operador. As regras de exclusão preservam todos os arquivos existentes no disco.

`outputs` fica excluído por padrão. A lista explícita em `.gitignore` preserva as
fixtures R842/R843/R844/R852 exigidas pelos testes, os arquivos da reprodução R853
e os recibos pequenos vinculados nos relatórios R820/R862. São fotografias
históricas de execução local, não uma certificação de outra instalação.

A whitelist inicial contém 65 arquivos (916.438 bytes): sete JSONs exigidos pelos
testes de motores, 14 arquivos da reprodução R853 e 44 recibos/saídas pequenos
vinculados nos relatórios. Logs completos, cópias de fontes antigas, áudios,
capturas, binários analisados e saídas integrais dos provedores ficam locais.

Os arquivos públicos de R853 foram capturados do domínio
`rx.engenhariaorofacial.com.br` para reprodução de seu contrato de interface.
Não incluem modelos treinados nem comprovação clínica. A documentação original
destina essa reprodução ao operador do domínio; a captura pública não declara uma
licença de redistribuição para terceiros. Antes de reutilizá-los fora desse
contexto, confirme a titularidade ou uma licença aplicável.

As figuras usadas pelos capítulos permanecem em `livro-core`; cópias de exportação
em `livro-core/output` ficam locais. O PDF do livro é um artefato compilado e não
faz parte das fontes versionadas.

## Conferência de uma cópia limpa

Crie um ambiente Python e instale `requirements-dev.txt`. Para a interface de
memória Streamlit, instale adicionalmente `requirements-webapp.txt`. Instale as
dependências Node declaradas em `.opencode/package.json` para as ferramentas do
OpenCode; o lock precisa corresponder ao manifesto para instalação determinística.
Motores externos e CLIs exigem configuração própria e não são incluídos no Git.

Execute `python -m pytest tests/test_r864_repository_release.py -q` e o conjunto
de testes do Core. Use `python -m marceloclaro.cli doctor` para conferir a estrutura;
o diagnóstico de instalação não confirma autenticação, inferência ou prontidão de
todos os provedores. Uma revisão em checkout limpo é necessária para detectar
caminhos pessoais e dependências transitivas antes de publicar uma entrega.

Para preparar um commit, selecione os arquivos explicitamente e confira o índice
antes de confirmar. Uma regra de `.gitignore` não retira arquivos que já sejam
rastreados. Manuscritos, dados de pesquisas paralelas, áudio, ambientes virtuais,
pacotes externos, credenciais e logs completos devem ficar fora deste commit do
Core. O contrato da separação está em SPEC-935-R864.
