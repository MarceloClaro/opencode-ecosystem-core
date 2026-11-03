---
spec_id: SPEC-935-R923
title: ITS-FINE instalado por composição e autonomia delimitada no Core
component: integrations.itsfine_core, marceloclaro.orchestrator
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    instalacao:
    - tests/test_r923_itsfine_core.py::test_status_checks_hashes_without_running_installed_code
    - tests/test_r923_itsfine_core.py::test_tampered_or_unsafe_installation_blocks_execution
    planejamento:
    - tests/test_r923_itsfine_core.py::test_plan_is_pure_and_sealed
    autonomia:
    - tests/test_r923_itsfine_core.py::test_safe_run_executes_only_fixed_read_only_commands
    - tests/test_r923_itsfine_core.py::test_forged_or_stale_plan_never_runs
    - tests/test_r923_itsfine_core.py::test_budget_cancel_timeout_and_errors_are_explicit
    primario:
    - tests/test_r923_itsfine_core.py::test_primary_dispatch_and_cli_contract
    integracao:
    - tests/test_r913_component_plugins.py::test_installed_lean_accepts_truth_and_rejects_false
    - tests/test_r923_itsfine_core.py::test_selected_extraction_preserves_old_version_metadata
    - tests/test_r923_itsfine_core.py::test_drvfs_options_are_opaque_and_specific_mount_required
    - tests/test_r923_itsfine_core.py::test_selected_scope_caps_bytes_read_not_unread_script_sizes
    - tests/test_r922_academic_plugin_integration.py::test_restricted_frontmatter_is_not_split_by_internal_dashes
    - tests/test_r922_academic_plugin_integration.py::test_punctuated_quoted_secret_is_rejected_without_leak
    - tests/test_r922_academic_plugin_integration.py::test_canonical_service_rejects_lexical_symlink_root
    - tests/test_r922_academic_plugin_integration.py::test_selected_inventory_does_not_touch_unrelated_packages
    - tests/test_r922_academic_plugin_integration.py::test_drvfs_projection_is_data_only_and_requires_observed_mount
    - tests/test_r920_academic_simulation.py::test_cases_are_deterministic_and_stage_specific
    - tests/test_r920_academic_simulation.py::test_preserve_negative_evidence_without_approval
    - tests/test_r920_academic_simulation.py::test_service_actions_persist_and_verify
    - tests/test_r919_core_gaps.py::test_chat_once_rejects_malformed_message
    - tests/test_r919_core_gaps.py::test_tool_message_preserves_output_that_fits_context
    - tests/test_r916_documentation_atlas.py::test_current_r916_receipt_matches_map_and_flow_artifacts
---

# R923 — ItsFine Core: composição, não fork não autorizado

## Evidência de origem

Pedido literal: `npx @sandeco/itsfine install`. Auditoria inicial via npm pack
--ignore-scripts, versão 0.0.15; SHA-512 SRI
`sha512-LpfBJTaZaGBOpH6u1A8DzrsIGFxMjpWL7ZqaVAv8CNeoNtaE+sLxw9DmMiGyfHMlB4UHqDmU9dF8JNpqLSm7hw==`.
124 arquivos regulares, 871654 bytes descompactados. REA real analisou pacote
distribuído (ev_277240ca2186690029c50bf9aaeb83aeb8b2de9760cadf85903c2078bda1ed3e),
sem executá-lo. Cobertura JS não cobre semanticamente o runtime Python.
Não há licença raiz declarada no package.json nem LICENSE raiz no pacote;
licença Laya de terceiro não relicencia o projeto. Não copiar/redistribuir um
fork: instalar para uso local autorizado e desenvolver adaptador original.

## Instalação autorizada

Usar o pacote auditado/pinado e o instalador npm solicitado, com seleção
explícita `--engines opencode --yes` para não ativar hooks Claude por default.
Não alterar allow_process/dados/transferência/cloud: política pertence ao
usuário. Não instalar torch, baixar pesos, iniciar treino, servir API, acessar
Kaggle/Colab, credenciais ou dados do usuário. Bootstrap de jsonschema isolado
é dependência da instalação, não engine pronta. Registrar versão, SRI, hashes,
comando observado e resultado do verificador. AGENTS.md preserva conteúdo
fora do bloco do instalador; novas skills são instruções, não inferência.

## Adaptador original

`integrations.itsfine_core.ItsFineCore(root)` com métodos status(),
plan(run_id=None), run_safe(plan, max_steps=3, timeout_seconds=30,
cancelled=False). API JSON fechada via primary.itsfine_action(config), CLI
`python3 -m integrations.itsfine_core status|plan|run [--run-id ID]`.
Operações sem hook/import de código upstream no processo do Core.

status inspeciona apenas install-manifest, hashes de arquivos gerenciados e
política/estado mínimos, sem executá-los ou ler artefatos de treino. Rejeitar
symlinks, traversal, duplicações/chaves JSON, arquivos não regulares e volumes
excessivos. Não exportar política, usuário, diretórios de dados ou stdout cru.
Versão admitida 0.0.15. Status instalado não é treino/inferência/autenticação.
Integridade local por hashes não é atestação contra o dono do host.

Plano determinístico selado (SHA JSON canônico) vincula manifest_sha256 e
policy_sha256, run_id validado e sequência de no máximo 3 ações: verify local,
engines e opcionalmente route ID. Planejar não executa nada. run_safe revalida
plano inteiro reconstruído e instalação antes de cada processo, usa argv fixo,
stdin DEVNULL, shell=False, tempo global, teto de saída e nenhum fallback/retry.
Nunca aceitar comando/script/modelo/URL/paths arbitrários como argumentos.
Leia o plano e proponha próxima skill; não invocar skills-filhas implicitamente.

Cancelamento prévio produz zero comandos; orçamento/prazo esgotado produz
partial, erros operacionais explícitos sem vazar stdout/stderr. Executar apenas
CLI instalada auditada `engines`/`route`, sem aprovar/submit/treino/instalar/etc.
Saída route é projetada para next_skill permitido e reason limitado, sem
logs/dados privados. Mesmo ambiente/política permissivos não elevam autonomia.
Resultado inclui counters, recibos dos processos e flags
training_executed=false, inference_executed=false, policy_modified=false,
externally_validated=false, human_approval_required=true. Nenhuma conclusão
de qualidade de modelo ou prontidão científica.

## Critérios de Aceitação Executáveis

- `instalacao` — status inerte e hashes/caminhos impedem executar instalação obsoleta/adulterada.
- `planejamento` — plano selado reproduzível, puro e sem concessão de permissões.
- `autonomia` — ações fixas executadas sob orçamento e parada, sem comandos livres ou vazamento.
- `primario` — fachada/CLI validados e observações sem promoção de confiança.
- `integracao` — contraprovas do SDK, MiroFish, plugins e recibo preservadas no estado final.

## Gaps e limite da versão

No caminho de plugins selecionados, opções de mountinfo são campos opacos;
não decodificar barras de um caminho Windows como escape de mountpoint.
Conservar seleção do mount efetivo, verificação de dispositivo e recusa de
metadata/ambiguidade. Limitar contagem/profundidade de todos os nós; teto de
bytes de leitura/cópia considera apenas candidatos instrucionais/manifestos/
licenças efetivamente legíveis, não binários/scripts excluídos que nunca são
abertos. Caminho R921 estrito continua com seus limites históricos. Não
alterar limites para permitir leitura de scripts, segredos ou código restrito.
O ponteiro de diretório `skills: "./skills/"` encontrado nos manifests reais
é equivalente a `./skills`; normalizar somente essa barra final no campo de
diretório, mantendo recusa de traversal, barras duplicadas e paths de arquivos.
O destino selecionado inspeciona cadeia lexical, registro canônico e somente
pacotes-alvo; não percorre arquivos privados de outros pacotes legados. O
registro retido continua validado estruturalmente, sem promover versão antiga
a pronta nem reabrir suas origens. O caminho estrito R921 conserva a política
de inspeção integral anterior.

Regressão operacional Lean observada nesta entrega: limite virtual de 4 GiB
impediu criar thread para prova trivial no compilador 4.34.1; sondas isoladas
de 6 e 8 GiB passaram. Fixar teto virtual mínimo observado de 6 GiB, preservando
namespace sem rede, CPU/prazo, arquivos, nofile, -j1 e heap Lean -M2048. Não
remover o limite, alterar fontes rejeitadas, aceitar sorry ou promover prova
inválida. Executar o teste real positivo/negativo antes de fechar a regressão.

REA fornece evidências, não reescreve nem valida automaticamente o programa.
Documentar lacunas observadas: parser instalador interativo por default,
seleção OpenCode escreve .agents sem configuração explícita .opencode,
update pode consultar/delegar latest, verify legado não confina todas as chaves
de manifesto antes de ler arquivos, testes upstream não vêm no tgz, ausência
de licença raiz. Recibos e wrapper de autonomia delimitada tratam integração e
governança, não demonstram melhoria de qualidade ou treino funcional sem dados.
