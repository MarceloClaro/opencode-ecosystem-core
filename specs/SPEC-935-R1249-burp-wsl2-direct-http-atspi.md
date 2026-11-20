---
spec_id: SPEC-935-R1249
title: Adaptar Burp MCP oficial a WSL2 via HTTP direto e AT-SPI
component: integrations.burp_wsl2_plan
status: specified
test_file: tests/test_r1249_burp_wsl2_adaptation.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    R1249-TRANSPORT:
      - tests/test_r1249_burp_wsl2_adaptation.py::test_plan_selects_official_streamable_http_without_java_or_proxy
      - tests/test_r1249_burp_wsl2_adaptation.py::test_catalog_surfaces_plan_without_claiming_burp_enabled
      - tests/test_r1249_burp_wsl2_adaptation.py::test_primary_plan_exposes_wsl2_transport
    R1249-SAFETY:
      - tests/test_r1249_burp_wsl2_adaptation.py::test_plan_remains_loopback_only_and_does_not_claim_target_activity
    R1249-AT-SPI:
      - tests/test_r1249_burp_wsl2_adaptation.py::test_atspi_backend_is_available_after_typelib_install
---

# SPEC-935-R1249 — adaptação WSL2 do Burp MCP oficial

## Objetivo

Substituir, para OpenCode neste workspace WSL2, o caminho stdio→SSE por conexão
remota MCP Streamable HTTP diretamente ao endpoint oficial `/mcp`. Essa escolha
elimina a necessidade de extrair `mcp-proxy-all.jar` e de configurar o Java como
launcher do proxy. O BApp continua sendo PortSwigger oficial e requer instalação
na interface do Burp.

Preparar o backend AT-SPI já incluído no Core para a interface gráfica WSLg,
estagiando o typelib Ubuntu `gir1.2-atspi-2.0` e sua dependência
`gir1.2-freedesktop` em diretório temporário do usuário. A instalação global
via apt foi impedida porque sudo exige senha; não pedir nem guardar senha. Os
`.deb` serão obtidos do repositório Ubuntu, hash conferido e apenas extraídos
(sem post-install). Cada ação de clique/tipagem continua sujeita ao token de
aprovação humana de uso único; não contornar a aprovação por automação shell/X11.

## Evidência documental consultada

- Microsoft Learn, WSL GUI apps: `https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps`.
- Microsoft Learn, WSL networking: `https://learn.microsoft.com/en-us/windows/wsl/networking`.
- PortSwigger oficial, BApp Manifest, commit observado
  `291034081160bc944b6df3eccd60c6fc99b477e1`:
  `https://raw.githubusercontent.com/PortSwigger/mcp-server/291034081160bc944b6df3eccd60c6fc99b477e1/BappManifest.bmf`.
- PortSwigger oficial, README no mesmo commit: endpoint Streamable HTTP `/mcp`,
  legacy SSE, Community e Pro; `https://github.com/PortSwigger/mcp-server/tree/291034081160bc944b6df3eccd60c6fc99b477e1`.
- OpenCode MCP docs: cliente remoto usa Streamable HTTP,
  `https://opencode.ai/docs/mcp-servers/`.

Essa compatibilidade é documental; não será declarada conexão operacional sem
prova de execução local após o BApp estar instalado.

## Estado observado antes da mitigação

- Ubuntu 24.04.5 no WSL2; `DISPLAY=:0` e `WAYLAND_DISPLAY=wayland-0` presentes.
- `agent-desktop` ausente; o operador Core foi observado como
  `binary_not_found`.
- O fallback AT-SPI existe no Core, mas falhou com `Namespace Atspi not available`.
- `at-spi2-core` está instalado; `gir1.2-atspi-2.0` e
  `gir1.2-freedesktop` não estão instalados no sistema e têm candidatos no
  repositório Ubuntu Noble.
- Burp, Java e a extensão ainda não foram instalados/carregados.

## Contrato

1. Selecionar apenas o endpoint oficial
   `http://127.0.0.1:9876/mcp` para esta configuração OpenCode dentro da mesma
   distro WSL; manter bind loopback, sem `0.0.0.0`, portproxy ou exposição LAN.
2. Marcar `requires_java=false` e `requires_proxy_jar=false` para o caminho HTTP
   direto. Não instalar/extrair o proxy stdio nesta rota.
3. Manter a configuração MCP do OpenCode ausente até a extensão oficial estar
   instalada e o endpoint estar disponível. Não declarar conexão/habilitação a
   partir do plano.
4. Estagiar os dois `.deb` oficiais e suas hashes em `/tmp/opencode`, sem
   instalação global ou scripts; verificar status AT-SPI pelo backend já
   existente usando `GI_TYPELIB_PATH`. Não instalar `agent-desktop` nem
   contornar seus gates.
5. Após iniciar Burp, carregar somente o BApp oficial PortSwigger. Não navegar a
   sites-alvo, não enviar requisições, não rodar scanner e não testar ferramenta
   MCP que opere sobre alvo.
6. A documentação atual indica que o BApp usa `enabled=true` como padrão e pode
   abrir listener ao ser carregado. A extensão deve permanecer em loopback; não
   alterar configuração do projeto Burp. Ferramentas de edição de config são
   desativadas por padrão e aprovações de requisição HTTP permanecem ativas.
7. A conexão posterior do cliente, se autorizada no passo de execução, poderá
   verificar handshake/lista de ferramentas apenas; nenhuma tool de request,
   scanner ou escrita será chamada sem escopo/autorização separados.

## Critérios de aceitação

- `R1249-TRANSPORT`: catálogo valida a proveniência declarada e seleciona
  Streamable HTTP em loopback sem exigir Java ou JAR proxy.
- `R1249-SAFETY`: plano deixa explícito `burp_installed=false`,
  `extension_installed=false`, `opencode_server_configured=false`,
  `mcp_connected=false`, `http_requests_sent=false` e
  `target_testing_authorized=false` até execução observada.
- `R1249-AT-SPI`: o backend local responde `ok=true` depois que o typelib for
  estagiado e carregado via `GI_TYPELIB_PATH`. Acesso à GUI não remove a
  aprovação humana por ação.

## Verificação e limites

- Testes primeiro; registrar RED antes do plano/integração e GREEN depois.
- Rodar testes R1249, regressão R1239 e `git diff --check`.
- Verificar versão/hash dos `.deb`, estado do staging e executar apenas o
  comando de status AT-SPI; não iniciar Burp nem conectar ao endpoint nesta fase.
- A instalação posterior do Burp/BApp é fase operacional separada; se AT-SPI
  não conseguir expor a UI ou exigir privilégios não disponíveis, parar e pedir
  intervenção humana.
