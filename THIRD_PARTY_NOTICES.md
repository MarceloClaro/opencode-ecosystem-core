# THIRD_PARTY_NOTICES

Registro de componentes de terceiros integrados ao OpenCode Ecosystem Core
(SPEC-935-R471 e subspecs). A redistribuição de qualquer componente exige
análise de licença prévia; este arquivo é o registro canônico.

## Componentes da R471 (Fase 1–6)

| Componente | Origem | Licença | Uso no Core | Restrição |
|---|---|---|---|---|
| open-swe | langchain-ai/open-swe | MIT | Fábrica de pesquisa (M1) | Nenhuma além das exigências MIT |
| OpenShell | NVIDIA | Apache-2.0 | Sandbox declarativo (M2) | Redistribuição exige avisos Apache-2.0 |
| NemoClaw | NVIDIA | Apache-2.0 | Operação padronizada de agentes (M2) | Redistribuição exige avisos Apache-2.0 |
| Personal-AI-Router (PAIR) | NVIDIA | Apache-2.0 | Roteador local de inferência (M3) | Sem sharding de GPU; roteia requisições independentes |
| DeepSeekGUI | See-Sol-Lab | camada de produto **PolyForm Perimeter 1.0.1**; upstream DeepSeek Harness **MIT** | Workbench de supervisão desktop (M4) | Uso interno de pesquisa/estudo permitido; **redistribuição competitiva vedada** sem licença |
| minimind | jingyaogong/minimind | Apache-2.0 | Currículo didático 64M (M5) | Treinamento real exige GPU; sem GPU documenta-se limitação |
| SciHubEVA | leovan/SciHubEVA | MIT | Frontend opt-in do resolvedor restrito (M6) | Nunca padrão; herda gates fail-closed da R470 |
| tig | rsrohan99/tig | **sem licença declarada** (license: null) | Executor alternativo multi-provedor (M7) | Invocação externa opcional; **vedada redistribuição**, inclusão em bundle ou venda de código derivado sem autorização |
| openclaw-qa | ythx-101 | conteúdo **CC BY-SA 4.0** (share-alike) | Observatório de campo (M8) | **Nenhuma incorporação de conteúdo**; citar com atribuição; derivados sob mesma licença |

## Política geral

- Credenciais nunca são persistidas em sandbox, recibo ou configuração.
- Falha de componente externo degrada para o fluxo nativo sem perda de dados
  (invariante 10 da SPEC-935-R471).
- Este registro não constitui parecer jurídico; consulte a licença de cada
  componente antes de redistribuir.