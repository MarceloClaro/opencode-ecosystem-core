# SPEC-935-R1088 — Recuperação dos MCPs e revisão operacional do Core

## Pedido, autorização e limites

Em 11/11/2026 o operador solicitou corrigir `failed` em `/mcps` e revisar o
OpenCode Ecosystem Core. Autorizou restaurar dependências públicas necessárias,
sem credenciais, modelos de IA ou alterações de serviços do sistema. Preservar
as alterações preexistentes em `opencode.json` e `.opencode/package*.json`.
Não migrar toda a configuração nem alterar permissões para esconder falhas.

Autorização adicional explícita: restaurar também o servidor Qdrant e o modelo
`sentence-transformers/all-MiniLM-L6-v2`, serviço no escopo do usuário,
somente loopback `127.0.0.1:6333`; smoke com sentinela técnica sem dados pessoais.

## Diagnóstico inicial observado

- `opencode --version`: 1.19.5; a CLI instalada não expõe `api`/`service` da
  documentação V2 atual. Usar apenas comandos confirmados pela CLI local.
- `opencode mcp list`: 15 conexões e 15 falhas. Ausentes Node/npx/uvx,
  runtimes federados/REA, venv científico, script Colibri no caminho antigo e
  diretório explicitamente configurado do editor.
- `python3 -m marceloclaro.cli doctor`: falta Whoosh no Python do sistema.
  `.venv/bin/python -m marceloclaro.cli doctor`: 15 pass, 7 warn, 0 fail.
- A revisão externa `task-ac74021a` bloqueou sem executor/parecer. Fallback
  local sob CFP `r1088-mcp-review`; não alegar revisão externa concluída.

## Aceites verificáveis

1. Corrigir o caminho Colibri para o módulo versionado; testar initialize e
   tools/list reais sem carregar modelo nem disparar inferência.
2. Restaurar a raiz explicitamente configurada do editor e o ambiente
   científico isolado; manter confinamento e aprovações de render.
3. Instalar dependências autorizadas em ambientes isolados/escopo usuário,
   com versões/origem registradas. Não executar instaladores shell remotos,
   hooks npm ou baixar modelos implicitamente. Falta de versão publicada,
   licença, serviço ou credencial continua bloqueio explícito.
4. Corrigir no gerador a preservação de entradas federadas obsoletas: uma
   entrada anterior não pode contornar `activated_servers`/recibos R1015.
   Preservar MCPs independentes do operador, inclusive sob `mcp.servers`.
5. Novos testes negativos devem falhar antes da implementação e passar
   depois. Executar regressões de configuração/MCP/segurança pertinentes,
   diagnóstico Core e inventário de conexão real final, com limites claros.
6. Registrar resultados, hashes/versões, bloqueios e reflexão. Conexão MCP
   não prova inferência, qualidade científica ou funcionamento de backends.

## Plano e critério de parada

1. Guardar inventário e diff inicial; escrever testes de regressão RED.
2. Corrigir gerador e caminhos; restaurar dependências públicas disponíveis.
3. Observar initialize/tools/list e smoke não destrutivo; sem render ou dados
   privados; sentinelas apenas em temporários locais.
4. Aplicar somente entradas recuperadas e escolhas explícitas; revalidar
   configuração, testes e diagnóstico. Documentar pendências sem declará-las
   consertadas. Revisão operacional focal, não auditoria integral do Core.

O gate de software exige testes passando. Componentes externos sem condições
de restauração nesta máquina permanecem reportados, nunca sucesso artificial.
