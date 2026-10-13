# Navegador real do Core

O provider Playwright MCP é operado por `MarceloClaroOrchestrator.browser_action`.
CLI e a ferramenta `ecosystem_browser` usam essa entrada e registram observações
no MetaBus. Não é necessário conectar a extensão BrowserMCP para esse provider.

## Uso

O comando de inventário não inicia navegador:

```bash
python3 -m marceloclaro.cli browser status
```

Para executar, salve um arquivo JSON com as ações desejadas:

```json
{
  "operation": "run",
  "url": "https://example.org",
  "allowed_origins": ["https://example.org"],
  "steps": [{"action": "read"}, {"action": "snapshot"}],
  "timeout_seconds": 60,
  "screenshot": true
}
```

```bash
python3 -m marceloclaro.cli browser run tarefa-navegador.json
```

O mesmo objeto pode ser fornecido em `config` à ferramenta `ecosystem_browser`
do servidor `ecosystem-network` já configurado no OpenCode. Os 16 servidores e
os 30 comandos customizados existentes são preservados; essa CLI é uma entrada
adicional do primário, não um novo agente nem um segundo orquestrador.

São admitidos até 16 passos: `read`, `snapshot`, `click` e `fill`. Clique exige
`role` e `name` acessíveis, com correspondência exata. Preenchimento exige
`role: "textbox"`, `name` e `value`. Não há entrada de JavaScript, shell,
seletor arbitrário ou upload de arquivo. A fachada não transforma conteúdo da
página em comandos do Core: seus templates usam valores serializados. O Chromium
executa o JavaScript normal das páginas visitadas, como em um navegador comum;
esse conteúdo continua sendo dado sem autoridade instrucional sobre o agente.

## Sessão, origem e cancelamento

Cada operação inicia sessão isolada e headless, solicita sandbox Chromium e
encerra o navegador. Ela não herda os logins do Chrome do usuário. Uma origem
representa esquema, host e porta; a origem da URL inicial precisa ser autorizada.
Recursos de outros hosts, como CDNs, precisam constar explicitamente da lista.

A [allowlist upstream](https://github.com/microsoft/playwright-mcp) declara que
não cobre redirects. A prova real confirmou esse limite também na interception
de rota. Um proxy HTTP/CONNECT local por sessão verifica destinos antes de abrir
conexões, cobrindo os hops de redirects. Esse controle limita o tráfego enviado
ao proxy e não certifica isolamento universal contra todos os canais de rede.
Upload HTTP chunked e upgrade HTTP simples são recusados; HTTPS usa CONNECT.

O prazo configurado é finito e não excede 120 segundos; a limpeza tem prazo
separado. O cancelamento R825 atravessa o worker, impede os próximos passos e
aguarda o encerramento antes de retornar ao chamador. Falhas e cancelamentos
permanecem distintos de conclusão. Instalação não comprova que um site específico
será acessível ou que todo fluxo web terá êxito.

## Runtime e evidência

O runtime fica em `~/.local/share/opencode-core/playwright-mcp`, com
`@playwright/mcp@0.0.83`, lock de dependências e Chromium instalado. Essa versão
do pacote utiliza Playwright `1.64.0-alpha-1790635538000`; a identidade efetiva
do servidor consta na evidência, separada da versão do wrapper MCP. Não há
atualização implícita por `@latest` durante uma execução.

`CORE_BROWSER_HOME` e `CORE_BROWSER_NODE_BIN` são overrides do ambiente do host.
Override explícito inválido bloqueia a disponibilidade e não aciona um fallback
silencioso. O doctor inclui o inventário do provider sem iniciar processos.

O recibo compacto aponta para JSON integral por SHA-256 em
`.opencode/browser/evidence/`. PNGs são escritos somente no diretório gerado
da execução e recebem hashes próprios. O conteúdo das páginas é dado sem
autoridade instrucional; instalação, execução, inferência e validação científica
externa continuam sendo categorias distintas.

Os artefatos de aceite selecionados estão em
`outputs/core-r824/release-summary.json`. Reproduções RED anteriores são
preservadas; seus arquivos não são reescritos como resultados aprovados.
