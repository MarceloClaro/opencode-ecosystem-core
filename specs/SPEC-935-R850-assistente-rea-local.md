---
spec_id: SPEC-935-R850
title: Assistente REA local com isolamento, configuração e evidências
component: integrations.rea_assistant, marceloclaro.rea_cli
status: implemented
test_file: tests/test_r850_rea_assistant_local.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    localidade:
    - tests/test_r850_rea_assistant_local.py::test_ida_rejeita_endpoint_remoto
    - tests/test_r850_rea_assistant_local.py::test_url_local_rejeita_porta_invalida
    - tests/test_r850_rea_assistant_local.py::test_ambiente_de_worker_nao_leva_credenciais
    - tests/test_r850_rea_assistant_local.py::test_namespace_real_isola_rede_do_host
    evidencia:
    - tests/test_r850_rea_assistant_local.py::test_camada_rejeita_dict_sem_evidence
    - tests/test_r850_rea_assistant_local.py::test_descoberta_observa_instalacao_no_mesmo_processo
    - tests/test_r850_rea_assistant_local.py::test_detecta_tipos_sem_executar_alvo
    - tests/test_r850_rea_assistant_local.py::test_explicacao_distingue_achados_e_limites
    interface:
    - tests/test_r850_rea_assistant_local.py::test_cli_encaminha_setup_e_inspect_ao_primario
    - tests/test_r850_rea_assistant_local.py::test_setup_registra_perfil_local_sem_alterar_config_global
    - tests/test_r850_rea_assistant_local.py::test_setup_rejeita_endpoint_de_modelo_remoto
    - tests/test_r850_rea_assistant_local.py::test_mcp_expoe_somente_interface_local
---

# R850 — Assistente local de engenharia reversa

O usuário solicita compreender aplicativos sem fontes, por CLI e MCP, com
setup registrado junto ao agente, explicações em português, evidências e limites.
A implementação amplia a ponte REA existente e mantém MarceloClaro como entrada.

## Critérios de Aceitação Executáveis

- `localidade` — subprocessos analíticos em namespaces Linux de usuário/rede/PID,
  com somente loopback, ambiente limitado e interrupção do processo PID 1 e seus
  descendentes. Ausência de isolamento bloqueia análise; não há fallback de rede.
- `evidencia` — decisões de sucesso exigem Evidence identificada da operação
  solicitada; entrada e saída guardam digests e versões. Prontidão não é execução,
  instruções não são código reconstruído, limitações do provider permanecem.
- `interface` — CLI setup/inspect/explain/site, MCP stdio com schemas e erros
  estruturados, perfis locais Linux e WSL/Windows, registro transacional sem
  substituir configuração global do operador e sem promover confiança.

## Escopo e arquitetura

Inspeção estática de JavaScript/Electron, ELF/PE/Mach-O via Ghidra instalado,
metadados .NET e HTML/assets locais. Autodetecção por assinatura/extensão, com
tipo explícito quando necessário. Outras camadas disponíveis podem ser
selecionadas pelo registro existente. IDA/Hopper são opcionais e exigem instalação
do operador; nenhuma licença ou capacidade é inventada.

O processo analítico usa `unshare` sem privilégio de root no host, loopback
habilitado dentro da rede privada e limpeza por namespace PID. O worker consulta
o primário e a ponte estática, nunca executa a aplicação alvo. A explicação é
determinística; um LLM não é requisito para ler o resultado.

Sites são arquivos exportados ou snapshots obtidos exclusivamente de URL literal
loopback, sem redirects, proxy herdado ou execução de JavaScript. Isso permite
analisar estrutura e referências; não demonstra comportamento dinâmico. Nenhum
serviço remoto é acessado com dados do alvo.

O perfil de agente fornecido permite apenas modelo com endpoint loopback e
desabilita provedores/MCPs externos herdados. MCP stdio entrega dados ao cliente
local: o cliente precisa conservar essa política. Um cliente que depois envia
esses dados à nuvem não integra a garantia do modo local. Isolamento de rede não
é sandbox universal de arquivos nem defesa contra o dono do host.

## Verificação e proveniência

Doctor antes das alterações; RED real pelo primário R839 antes do produto.
Falhas de API ausente ficam classificadas como bootstrap, separadas das
contraprovas funcionais de URL, Evidence e descoberta. Mesmo oráculo no GREEN.
Execuções reais: namespace com tentativa de conexão a servidor no host,
JavaScript empacotado, ELF conhecido sem execução, .NET local, HTML e MCP stdio.
Dados de prova sintéticos/locais, artefatos por hash, nenhuma validação externa.

Fontes: MCP transportes 2025-11-25, manual `unshare(1)` e documentação OpenCode
de providers locais; versões REA instaladas permanecem identificadas.
