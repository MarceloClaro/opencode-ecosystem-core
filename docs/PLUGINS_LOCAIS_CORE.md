# Plugins locais do Core

Os pacotes privados `opencode-ecosystem-core`, `opencode-rea`,
`opencode-mirofish-offline` e `opencode-lean4` conectam ChatGPT Work/Codex ao
runtime local. O host oferece a conversa; o MarceloClaro continua coordenando
as operações. Não publicar o servidor na internet nem copiar credenciais.

| Pacote | Entrada | Escopo |
|---|---|---|
| Core | `integrations.ecosystem_mcp` | Orquestração, biblioteca, pesquisa e integrações |
| REA | `integrations.component_mcp --component rea` | Estado e inspeção estática com recibo |
| MiroFish Offline | `integrations.component_mcp --component mirofish` | Estado e execução do runtime externo |
| Lean 4 | `integrations.component_mcp --component lean4` | Estado e verificação delimitada com compilador |

O instalador Core e o instalador de componentes são separados. Consulte a
ajuda antes de executar, pois o manifesto diferencia origem, destino e
instalação no host:

```powershell
Get-Help .\scripts\install_chatgpt_core_plugin.ps1 -Detailed
Get-Help .\scripts\install_component_plugins.ps1 -Detailed
```

Os recibos [R912](verification-chatgpt-plugin-r912.json) e
[R913](verification-component-plugins-r913.json) registram instalações e sondas
anteriores. Instalação no host, ferramentas disponíveis na conversa, transporte
MCP e operação concluída exigem verificações próprias. Reiniciar/reabrir um
cliente pode ser necessário após atualização do runtime.

## REA

`rea_action` encaminha ao bridge existente e preserva evidência, hashes e
limitações. Análises estáticas não executam automaticamente o aplicativo alvo.
Camadas declaradas e engines prontas são estados distintos. Veja
[assistente REA](ASSISTENTE_REA_LOCAL.md) e [integração REA](REA.md).

## MiroFish Offline

O checkout e OASIS são externos, por composição, com licença própria. O estado
`installation_only` não comprova autenticação ou inferência. No checkout
amostrado, `LiveScientificRuntime` exige um endpoint loopback previamente ativo;
o gerenciador sob demanda presente em uma versão anterior foi removido.

R913 preserva tanto uma execução sintética concluída quanto o timeout posterior
do gerenciador antigo. Nenhuma delas demonstra disponibilidade atual sob carga.
`completed` indica o contrato operacional observado, não previsão validada de
população real ou evidência científica elegível.

## Lean 4

Há duas rotas. O plugin usa `LocalLeanVerifier`: namespace sem rede, bibliotecas
somente leitura, prazo e limites de recursos; falta de compilador/isolamento não
recebe aprovação sintática. A CLI `marceloclaro lean4` usa o verificador legado,
que pode retornar `syntax_verified`; esse estado não comprova compilação.

Na fonte local amostrada, a interface do plugin extrai o primeiro nome de
teorema, exige a forma lexical admitida pela regex e relata os axiomas apenas
dele. O limite de espaço de endereçamento é 4 GiB. Recibos históricos de uma
versão que examinava todos os nomes ou usava 16 GiB não certificam estes bytes.
Não afirmar que todas as fórmulas do livro foram comprovadas por essas sondas.

## Dados e fronteiras

Execução local não torna a conversa hospedada offline. Conteúdo devolvido ao
ChatGPT/Codex pode ser processado pelo aplicativo. Downloads e fontes do
NotebookLM são processados no serviço Google; essa é outra integração, descrita
no [guia NotebookLM](GEMINI_NOTEBOOK_CORE.md). Licenças, autenticação, memória
disponível e autorização da operação são verificadas separadamente.
