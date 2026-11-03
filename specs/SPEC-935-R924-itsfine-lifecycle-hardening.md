---
spec_id: SPEC-935-R924
title: Ciclo de instalação e motores ITS-FINE, validação de extrator e Lean
component: integrations.itsfine_lifecycle, integrations.itsfine_core, integrations.local_lean
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    distribuicao:
    - tests/test_r924_itsfine_hardening.py::test_distribution_sri_and_missing_upstream_tests_are_explicit
    - tests/test_r924_itsfine_hardening.py::test_distribution_rejects_links_traversal_and_wrong_identity
    instalador:
    - tests/test_r924_itsfine_hardening.py::test_install_plan_is_noninteractive_offline_and_version_pinned
    - tests/test_r924_itsfine_hardening.py::test_install_requires_confirmation_and_unchanged_package_and_policy
    processo:
    - tests/test_r924_itsfine_hardening.py::test_bounded_runner_limits_output_timeout_and_kills_descendants
    motores:
    - tests/test_r924_itsfine_hardening.py::test_engine_plan_separates_text_and_voice_and_pins_lock
    - tests/test_r924_itsfine_hardening.py::test_engine_prepare_is_explicit_and_never_marks_gpu_ready_from_metadata
    - tests/test_r924_itsfine_hardening.py::test_engine_status_rechecks_receipt_and_environment
    - tests/test_r924_itsfine_hardening.py::test_engine_status_does_not_trust_a_forged_ready_receipt
    verificacao:
    - tests/test_r924_itsfine_hardening.py::test_primary_exposes_verified_lifecycle_without_arbitrary_commands
    - tests/test_r924_itsfine_hardening.py::test_verifier_refuses_parent_symlink_race_before_body_read
    extrator:
    - tests/test_r924_itsfine_hardening.py::test_duplicate_yaml_cannot_hide_restricted_license_or_invocation_policy
    lean:
    - tests/test_r924_itsfine_hardening.py::test_lean_rejects_sorryax_and_multiple_theorems_before_compiler
    - tests/test_r924_itsfine_hardening.py::test_lean_rejects_sorry_axiom_in_compiler_output
    - tests/test_r924_itsfine_hardening.py::test_lean_resource_failure_is_not_semantic_rejection
    regressao:
    - tests/test_r913_component_plugins.py::test_installed_lean_accepts_truth_and_rejects_false
    - tests/test_r923_itsfine_core.py::test_primary_dispatch_and_cli_contract
    - tests/test_r923_itsfine_core.py::test_safe_run_executes_only_fixed_read_only_commands
    - tests/test_r922_academic_plugin_integration.py::test_primary_facade_validates_and_dispatches_selected_operations
---

# R924 — correções adicionais pedidas pelo usuário

## Escopo e limites

Preservar alterações anteriores, políticas manuais e upstream instalado.
Corrigir no Core por composição, sem relicenciar/modificar cópias gerenciadas
de terceiros e sem declarar testes upstream disponíveis quando não publicados.
Não treinar, baixar pesos, ler datasets/credenciais, ativar serviços ou editar
`.its-fine/policy.json`. Preparação de dependências autorizada pelo pedido;
rede somente para distribuições oficiais/pacotes necessários, com recibos.

## Instalador e distribuição

Novo `integrations.itsfine_lifecycle`: `audit_distribution(archive_path)`,
`installation_plan(root, archive_path)`, `install_pinned(root, plan, confirm=False,
timeout_seconds=120)`, `engine_plan(root, engine)`, `prepare_engine(root, plan,
confirm=False, timeout_seconds=1200)` e `engines_status(root)`.

Auditar TGZ sem extrair/executar: SRI SHA512 exato da 0.0.15 publicado no npm,
package.json com nome/versão corretos, limite 256 arquivos/4 MiB total expandido,
paths canônicos sob package/, nenhuma duplicação/link/dispositivo/FIFO.
Ler somente metadados de distribuição, não corpos arbitrários no host.
Relatar separadamente testes declarados, presentes e ausentes. O npm não
publica a suíte upstream e não informa repositório inequívoco: marcar
`upstream_tests_status=not_shipped` até evidência real, sem fabricar substituto.

Plano de instalação selado por JSON canônico inclui SHA do TGZ e da política,
argv fixo npm exec --yes --offline --package <TGZ validado> -- itsfine install
--target <raiz> --engines opencode --yes --no-deps. Sem latest/update/fallback,
stdin DEVNULL, ignore-scripts para lifecycle npm, ITSFINE_SKIP_REGISTRY=1.
`confirm=True` obrigatório. Revalidar plano/pacote/política antes de executar.
Caso runtime-deps faltem, interromper e relatar, não instalar silenciosamente.
Revalidar hashes gerenciados depois e não promover exit code zero a instalação
correta sem verificação. A política já existente deve conservar seus bytes.

## Processos e fronteiras

Runner interno bounded_process com argv explícito, shell=False, sem TTY,
prazo finito e teto de bytes durante leitura, não só após buffering ilimitado.
Sessão própria POSIX e fechamento do grupo de filhos em timeout/excesso ou
término do pai. Retornar bytes delimitados, status e hashes; não exportar logs
ou stderr privados nos recibos da fachada. Diretórios de trabalho explícitos.

## Ambientes dos motores

Python 3.12 já presente é usado para ambientes independentes do Core 3.14.
hf-peft/hf-encoder compartilham `.its-fine/venv`; hf-tts usa
`.its-fine/venvs/hf-tts`. Não modificar o Python do Core. Locks de dependências
por ambiente em `integrations/itsfine-locks/{text,voice}-py312.txt`, com versões
exatas, hashes e origem; geração via resolvedor não é prova de importação.
TTS preserva transformers 4.57.3/accelerate 1.12.0, texto usa >=5.16,<6.
Torch/torchaudio CPU fixados e compatíveis quando o host não expõe GPU.
Nenhuma substituição silenciosa por modelo/treino em nuvem.

Planos vinculam engine.json gerenciado, lock, política e versão Python.
Preparação exige confirmação, roda comandos fixos venv/sync com hash-check,
sem setup.py arbitrário, sem pip upgrade irrestrito ou flags do usuário.
Uma venv nova recebe marcador Core; não sobrescrever ambiente alheio.
Recibo não pode declarar prontidão apenas por metadata ou engine-setup.json.
Sondar imports requeridos e pequena operação tensor/gradiente em CPU, sem
modelo pré-treinado, treino/otimizador ou acesso ao Hub; OFFLINE nas sondas.
Registrar versões/pip check, lock SHA e fingerprints do interpretador.
`dependencies_ready`, `cpu_probe_passed`, `accelerator_available` e
`training_ready` são campos distintos. CPU preparado não vira GPU disponível;
driver ausente no host é bloqueador externo, não algo que um flag conserta.
Consulta revalida lock/venv/recibo e não confia em engines_prontos legado.

## Fachada e verificador

Ampliar `ItsFineCore`, CLI e primary.itsfine_action para verify,
install_plan/install, engine_plan/engine_prepare e engines_status, em schema
fechado e sem executar ações privilegiadas por simples status/plan.
Planos mantêm selo após passar pelo primário. Não alterar modelo padrão,
hooks de outros hosts ou permissões por automação.
O verificador Core confina cada componente com dir_fd/O_NOFOLLOW antes de
abrir corpo, inclusive sob corrida de symlink em diretório pai. Manter versão,
hashes, limites, JSON sem chaves duplicadas e separação verificação/executar.

## Extrator e Lean

Recusar chaves YAML duplicadas e merge keys no frontmatter e openai.yaml antes
de ler corpos ou permitir invocação; safe_load com last-key-wins não basta.
Manter licenças restritas reference_only e testes de não leitura por descritor.

Lean recusa `sorryAx` explícito e mais de um theorem/lemma por entrada antes
do compilador: a interface não pode rotular um arquivo inteiro com relatório
somente da primeira prova. Conservar namespace sem rede, heap de 2 GiB e
espaço virtual de 6 GiB. Output com sorryAx/admissões nunca é machine_checked,
mesmo se exit=0. Falha de recurso/thread/memória tem estado operacional
`resource_exhausted`, não é prova falsa nem rejeição semântica. Assunções
encontradas no relatório são explícitas. Não aceitar axioma inventado.

## Critérios de Aceitação Executáveis

- `distribuicao` — identidade/SRI/paths e ausência de testes upstream são tratados honestamente.
- `instalador` — execução confirmada, fixa, não interativa, sem atualização implícita e sem mudar política.
- `processo` — tempo/saída/descendentes limitados de verdade.
- `motores` — planos e ambientes separados, locks e sondas; metadata não vira prontidão.
- `verificacao` — fachada fechada e abertura de arquivos confinada por componentes.
- `extrator` — YAML ambíguo não oculta licença/política.
- `lean` — admissão/múltiplas provas recusadas e recursos diferenciados de semântica.
- `regressao` — contratos locais prévios continuam passando.
