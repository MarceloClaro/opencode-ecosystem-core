# OpenCode Ecosystem Core no ChatGPT — R912

O Core pode fornecer suas ferramentas ao ChatGPT Work/Codex por um plugin.
Na instalação local aqui preparada, ele continua no Ubuntu/WSL e o aplicativo
inicia o servidor stdio existente. MarceloClaro permanece o primário.

## Usar neste computador

1. Abra os plugins do aplicativo e procure **OpenCode Ecosystem Core**, na
   fonte **MarceloClaro Core local**.
2. Abra uma conversa com execução local e selecione o plugin por `@`.
3. Peça: “Consulte o estado do Core pelo MarceloClaro e apresente as limitações”.
4. Para biblioteca: “Busque no Core uma referência sobre MCP e cite a página”.

Se o aplicativo ainda não mostrar o marketplace novo, reinicie o aplicativo
depois de salvar seus trabalhos. A documentação oficial orienta reiniciar para
descoberta de marketplaces locais. Não é necessário reinstalar o Core.

O inventário do instalador distingue `installed` e `enabled`. A sonda independente
comprova inicialização, ferramentas e consulta pelo comando instalado; ela não
comprova que uma conversa já aberta recarregou essas ferramentas. A ativação
efetiva é confirmada quando o aplicativo anuncia e chama `ecosystem_*` na conversa.

A instalação local R912 concluiu a versão **1.0.1**, com `installed=true` e
`enabled=true`. O launcher instalado anunciou **23 ferramentas** e recuperou uma
evidência bibliográfica citável. A conversa usada para preparar a instalação
continuou sem essas ferramentas carregadas; nenhuma inferência pelo plugin foi
executada. O recibo abaixo preserva essa distinção.

Para executar tarefas, a skill encadeia `ecosystem_text_spec` e o `spec_id`
retornado a `ecosystem_run`; workflows recebem a especificação em cada nó.
Assim, o plugin conserva o gate SDD do Core.

## O que fica local

O processo Python, os executores e a biblioteca ficam no computador. Resultados
solicitados e enviados à conversa são processados pelo ChatGPT. Não confundir
execução local com inferência totalmente offline do modelo do aplicativo.
O pacote não inclui `.env`, tokens, PDFs, dependências ou uma cópia do repositório.

O MCP completo contém leitura, escrita, rede, navegador e execução autorizada.
As anotações de ferramentas não são sandbox. Permanecem aplicáveis as permissões
do host, o escopo autorizado, os gates do Core e as exigências SDD/TDD.
Conectar não transfere login de Claude, Codex, Antigravity ou outros conectores.
ChatGPT não se torna um executor CLI do Core por receber o plugin.

## Instalação reproduzível

Pré-requisitos: Windows com WSL Ubuntu, Core instalado com `.venv` e Codex CLI
disponível. Confirme primeiro o diagnóstico do Core. A instalação não altera
credenciais nem publica endpoint. Ela usa um marketplace pessoal isolado,
preservando outros plugins e recusando sobrescrever uma fonte diferente.

Copie `scripts/install_chatgpt_core_plugin.ps1` para uma pasta local do Windows
e execute-o no PowerShell. A cópia local evita tratar o arquivo UNC como script
remoto; não altere a política global de execução.

```powershell
.\install_chatgpt_core_plugin.ps1 -CoreRoot '/home/marceloclaro/opencode-ecosystem-core' -Distro Ubuntu
```

O gerador também permite criar o pacote sem instalar:

```bash
.venv/bin/python -m integrations.chatgpt_plugin \
  --target windows-wsl --destination outputs/meu-plugin \
  --archive outputs/opencode-ecosystem-core.zip
```

O destino deve ser novo. Uma atualização de pacote exige versão e instalação
explícitas; não edite o cache do aplicativo. No Linux, use `--target linux`.
O launcher preserva limites dos argumentos, incluindo caminhos com espaços.
Os recibos da instalação ficam em `outputs/chatgpt-plugin/<identificador>/`.
O instalador confere a origem do marketplace e os cinco arquivos por SHA-256
na fonte e no cache criado pelo host. Arquivos extras, diferenças de conteúdo
e redirecionamentos impedem a instalação. O gerador também recusa substituir
um ZIP existente ou escrever por um link simbólico.

A consulta da biblioteca usa um índice local. Se fontes forem alteradas, execute
`python3 -m marceloclaro.cli biblioteca indexar` pelo Core antes da sonda de busca.
Arquivos vazios ou excluídos continuam registrados como tais; não se inventa conteúdo.

## ChatGPT no navegador

O pacote local não implanta um servidor na nuvem. Para o navegador, a OpenAI
documenta conexão por MCP HTTP e **Secure MCP Tunnel**, com associação e
autorização da conta/workspace. Isso é outra modalidade de instalação: não há
URL pública nem túnel criado por esta instalação local. Não cadastrar `localhost`
como se fosse uma URL alcançável pelo serviço remoto.

## Fontes oficiais conferidas

- [Pacote, marketplaces e instalação local](https://developers.openai.com/plugins/build/plugins).
- [Conexão de MCP como plugin](https://developers.openai.com/api/docs/guides/custom-mcp-server).
- [Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels).

O manifesto local `docs/verification-chatgpt-plugin-r912.json` discrimina o que
foi executado e o que depende da ativação na interface. A validação é local;
nenhuma certificação externa de produção é alegada.
