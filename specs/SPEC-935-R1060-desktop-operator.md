# SPEC-935-R1060 — desktop-operator com política e aprovação humana

**Status:** implementação autorizada; piloto dependente do ambiente gráfico.
**Origem:** avaliação do fork `MarceloClaro/agent-desktop1`, idêntico ao
`vercel-labs/agent-desktop` (Apache-2.0, Rust), 2 commits atrás e sem releases.
**Objetivo:** cobrir a lacuna de operação de apps nativos no Core sem expor o
MCP completo de 56 comandos e sem permitir ações destrutivas por padrão.

## 1. Escopo

Entregar uma camada local que:

1. executa apenas `status`, `list-apps`, `snapshot`, `click`, `type` e `wait`;
2. exige allowlist de aplicativos para `snapshot`, `click` e `type`;
3. exige aprovação humana de uso único para `click` e `type`, vinculada a
   comando, app, ref e hash do texto;
4. nega por padrão `clipboard-*`, `screenshot`, `launch`, `open-system-surface`,
   `key-down`, `key-up`, `mouse-*`, `--headed`, `--force`, `--trace`,
   `--session`, `--cursor-overlay` e `--debug`;
5. redige e limita a saída antes de devolvê-la ao agente;
6. expõe um servidor MCP com exatamente seis ferramentas, sem ferramenta de
   aprovação;
7. registra um perfil `desktop-operator` no catálogo do Core.

**Fora de escopo:** instalar o binário automaticamente, habilitar o MCP
completo do upstream, operar apps do Windows a partir do WSL, publicar,
executar comandos de shell do usuário ou usar clipboard/screenshot.

## 2. Arquitetura

```
agente → MCP desktop-operator (6 tools)
      → policy.build_argv / approvals.verify
      → runtime subprocess (argv fixo, stdin para texto)
      → agent-desktop CLI (upstream fixado)
      → envelope JSON → redação/limite → agente
```

O wrapper não interpreta shell, não aceita argv arbitrário e não repassa
flags globais. Texto de `type` vai por `stdin`, não por argumento.

## 3. Contrato das ferramentas

| Ferramenta | Efeito | Regras |
|---|---|---|
| `desktop_status` | lê saúde/permissões | sem app; somente leitura |
| `desktop_list_apps` | lista apps | sem app; somente leitura |
| `desktop_snapshot` | lê árvore de acessibilidade | app na allowlist; `-i --compact`; profundidade ≤ 8; superfície `window` |
| `desktop_wait` | espera condição | um único modo: ms, elemento, texto ou janela; sem menu/evento/notificação |
| `desktop_click` | ativa um ref | app na allowlist; ref qualificado; aprovação de uso único |
| `desktop_type` | insere texto | app na allowlist; ref qualificado; ≤ 10.000 bytes; sem NUL; aprovação vinculada ao hash do texto |

Não existe ferramenta para criar aprovação. A aprovação é criada apenas pela
CLI local, por decisão humana explícita.

## 4. Política

- Allowlist vazia significa **negar** `snapshot`, `click` e `type`.
- Nome de app: `[A-Za-z0-9._@/-]{1,120}`, comparação case-insensitive.
- Ref: `@<snapshot_id>:e<N>`, sem refs nus.
- `type`: UTF-8, ≤ 10.000 bytes, sem `\x00`; controle permitido apenas `\n` e `\t`.
- Timeout: 1.000–30.000 ms para snapshot; 0–60.000 ms para espera por tempo;
  demais 1.000–30.000 ms.
- Saída: máximo 256 KiB, JSON válido, strings longas truncadas e marcadas.
- Ambiente do subprocesso: apenas `PATH`, `HOME`, `DISPLAY`, `WAYLAND_DISPLAY`,
  `XDG_RUNTIME_DIR`, `DBUS_SESSION_BUS_ADDRESS`, `LANG`, `LC_ALL`, `NO_COLOR`.
  Nenhum segredo do processo pai é repassado.
- Binário: caminho configurado, cache isolado do piloto ou `PATH`; ausência
  gera erro explícito, nunca instalação automática.

## 5. Aprovação

Token `v1.<payload>.<hmac>` com payload canônico:

```json
{"v":1,"command":"click","app":"xmessage","ref":"@abc123:e4","text_sha256":null,"exp":1760000000,"nonce":"..."}
```

- HMAC-SHA256 com segredo local de 32 bytes, arquivo `0600`.
- TTL máximo de 300 s; `exp` obrigatório.
- Uso único: nonce consumido por criação exclusiva de arquivo.
- `type` exige `text_sha256`; trocar o texto invalida o token.
- Token de um ref/app/comando não serve para outro.
- CLI `approve` exige `--confirm`; o MCP não emite tokens.

## 6. Redação e evidência

- Redigir e-mail, CPF, CNPJ, cartão, telefone, `Bearer`, chaves sensíveis e
  strings hex/base64 longas.
- Não registrar texto digitado, clipboard ou screenshot em log.
- Cada resposta inclui `policy`: decisão, comando, app, uso de aprovação e
  duração. `external_validation=false`.
- Snapshot é dado não confiável: o prompt do agente proíbe seguir instruções
  encontradas na árvore de acessibilidade.

## 7. Aceitação (TDD)

Testes em `tests/test_r1060_desktop_operator.py` devem provar:

1. allowlist vazia nega snapshot/click/type;
2. status e list-apps funcionam sem aprovação;
3. app fora da allowlist e nome com metacaractere são negados;
4. comandos proibidos e flags proibidas são negados;
5. ref nu/malformado é negado;
6. texto acima do limite ou com NUL é negado;
7. click/type sem aprovação, com aprovação errada, expirada ou reutilizada
   falham; aprovação válida executa o binário falso e é consumida;
8. token de `type` vinculado ao hash do texto;
9. redação e truncamento produzem JSON válido;
10. ambiente do subprocesso não contém segredo do pai;
11. MCP expõe exatamente seis ferramentas e nenhuma de aprovação;
12. argumentos são montados como lista, sem `shell=True`;
13. `wait` aceita um único modo e rejeita menu/evento/notificação.

## 8. Piloto

1. Instalar `agent-desktop@1.1.0` em prefixo isolado, com integridade npm
   registrada; não instalar globalmente.
2. Executar `status` e `list-apps` somente leitura.
3. Abrir app descartável, capturar snapshot e conferir refs.
4. Emitir aprovação humana para uma única ação semântica, executar e verificar
   com novo snapshot.
5. Se o ambiente não expuser acessibilidade, registrar bloqueio e não simular
   sucesso.

## 9. Riscos e limites

- Controle de apps é sensível; allowlist e aprovação não substituem sandbox.
- Prompt injection via texto da UI permanece possível; snapshots são tratados
  como dados, nunca instruções.
- WSL enxerga apps Linux do WSLg, não apps Windows.
- O wrapper não audita o binário upstream; a versão e a integridade npm devem
  ser fixadas e monitoradas.
- Aprovação local não é assinatura humana criptográfica; é um gate operacional
  com segredo local.
- Nenhuma validação externa, publicação ou operação de app de produção.

## 10. Resultado da implementação (2026-11-05)

**Status:** implementação concluída; piloto real concluído via fallback AT-SPI.
O caminho agent-desktop segue bloqueado pelo bug upstream. Nada foi publicado.

| Item | Resultado |
|---|---|
| Pacote upstream | `agent-desktop@1.1.0`, Apache-2.0, prefixo isolado |
| Binário | `~/.cache/opencode-pilot/desktop-operator/node_modules/.bin/agent-desktop` |
| Integridade npm | registrada em `pilots/r1060-desktop-operator/install-receipt.json` |
| MCP | `desktop-operator` com seis ferramentas, registrado no `opencode.json` |
| Perfil | `agents/catalog/desktop-operator.md`, registrado no Blackboard |
| Testes | **46 passed** com binário falso |
| `status` real | ok; acessibilidade `granted` |
| `list-apps` com app, via agent-desktop | falha `native_window_unproven` |
| `list-apps`/`snapshot` via fallback AT-SPI | ok; refs qualificados |
| `type`/`click` reais via AT-SPI | `delivered_verified`; clique em “Aplicar” confirmado por novo snapshot |
| Aprovações reais | 3 tokens de uso único, nenhum persistido |

### Causa do bloqueio

Issue upstream aberta `vercel-labs/agent-desktop#435`: em Ubuntu 26.04 /
GNOME Shell 50.1 / Wayland, comandos de inventário e snapshot falham com
`ACTION_NOT_SUPPORTED` / `native_window_unproven`. O erro foi reproduzido em
WSLg e em Xvfb+Openbox com `gtk3-demo` e `zenity`. `status` permanece saudável,
portanto não é suficiente para declarar a integração operacional. O fallback
AT-SPI local cobre apps Linux e permitiu concluir snapshot/type/click/wait no
piloto; ele não corrige o binário upstream.

### Decisões de segurança verificadas

- Allowlist vazia nega `snapshot/click/type`; `status/list-apps` continuam.
- Comandos e flags proibidos são negados antes de qualquer subprocesso.
- Texto de `type` vai por stdin e é vinculado ao hash na aprovação.
- Aprovação é de uso único, presa ao host, registra operador declarado e não
  pode ser emitida pelo MCP.
- Saída passa por redação, remoção de controles invisíveis, sinalização de
  instruções suspeitas e limite de 256 KiB; isso não impede prompt injection.
- Ambiente do subprocesso não repassa segredos do processo pai.
- `shell=False` e argv em lista.

### Limites

- O wrapper não corrige o adapter upstream; o fallback AT-SPI é um caminho
  alternativo para apps Linux.
- O piloto comprova operação via AT-SPI, não via agent-desktop.
- Aprovação local não substitui sandbox, consentimento ou revisão humana.
- WSL enxerga apps Linux, não apps Windows.
- `opencode.json` foi editado de forma conservadora; regeneração futura pode
  remover entradas federadas inativas, comportamento pré-existente.

### Próximo passo

Acompanhar a correção upstream para o caminho agent-desktop; manter o fallback
AT-SPI para Linux; ampliar allowlist apenas para apps descartáveis; tratar apps
Windows como escopo separado, no host; buscar validação externa antes de
publicar.
