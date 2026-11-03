---
spec_id: SPEC-935-R928
title: AI Edge Quantizer isolado e ensaio TFLite sintético CPU
component: integrations.ai_edge_quantizer_core, integrations.ai_edge_quantizer_worker
status: proposed
test_file: tests
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    fonte:
    - tests/test_r928_ai_edge_quantizer.py::test_status_and_source_plan_are_inert_and_pinned
    - tests/test_r928_ai_edge_quantizer.py::test_source_acquisition_checks_git_blobs_and_never_downloads_models
    - tests/test_r928_ai_edge_quantizer.py::test_source_acquisition_rejects_unsafe_entries_without_publication
    ambiente:
    - tests/test_r928_ai_edge_quantizer.py::test_environment_plan_uses_dedicated_lock_and_confirmation
    - tests/test_r928_ai_edge_quantizer.py::test_existing_foreign_environment_is_preserved
    - tests/test_r928_ai_edge_quantizer.py::test_prepare_does_not_inflate_subsecond_budget
    plano:
    - tests/test_r928_ai_edge_quantizer.py::test_demo_plan_is_sealed_fixed_and_has_no_external_model_input
    - tests/test_r928_ai_edge_quantizer.py::test_demo_requires_confirmation_and_rejects_stale_plan
    isolamento:
    - tests/test_r928_ai_edge_quantizer.py::test_worker_namespace_has_no_network_or_workspace_mount
    - tests/test_r928_ai_edge_quantizer.py::test_worker_namespace_binds_only_the_declared_python_alias
    - tests/test_r928_ai_edge_quantizer.py::test_environment_sources_remain_attested
    resultado:
    - tests/test_r928_ai_edge_quantizer.py::test_metrics_reject_nonfinite_values_and_false_success
    - tests/test_r928_ai_edge_quantizer.py::test_failed_worker_never_publishes_success
    - tests/test_r928_ai_edge_quantizer.py::test_report_rechecks_artifact_hashes_and_paths
    - tests/test_r928_ai_edge_quantizer.py::test_report_refuses_overclaims_and_numeric_drift
    primario:
    - tests/test_r928_ai_edge_quantizer.py::test_primary_dispatch_is_closed_and_preserves_plan_seal
    - tests/test_r928_ai_edge_quantizer.py::test_primary_preserves_sealed_results
---

# R928 — integração aprovada explicitamente pelo usuário

## Origem e fronteiras

Fork `MarceloClaro/ai-edge-quantizer`, commit fixo
`87cda53576a55a71114a4945b3ff18e27c2fa42b`, Apache-2.0, código Alpha 0.3.0.
Não confundir com releases atuais do upstream. Uma URL autorizou inspeção;
o usuário respondeu sim à integração isolada e ao ensaio pequeno/sintético.
gallery, OpenManus e lqc-textbook são apenas análises de leitura separadas.

Não baixar checkpoints, modelos prontos, dados de calibração ou testes com
modelos binários do repo. Não treinar, mudar modelo padrão, executar agentes
OpenManus, instalar APK/Android SDK ou modificar ambientes ITS-FINE/Core.
Não supor que GGUF, .task, .litertlm e .tflite sejam intercambiáveis.

## API original do Core

`EdgeQuantizerCore(root)` em integrations/ai_edge_quantizer_core.py:
status(), source_plan(), acquire_source(plan, confirm=False, timeout_seconds=300),
environment_plan(), prepare(plan, confirm=False, timeout_seconds=900),
demo_plan(run_id='synthetic-int8'), demo(plan, confirm=False, timeout_seconds=180),
report(run_id). Helpers validate_config e validate_metrics são públicos puros.
Fachada primary.ai_edge_quantizer_action(config); CLI `marceloclaro edge-quantizer`.
Schema fechado, sem URL, script, receita livre, modelo ou diretório arbitrário.
Planos JSON canônicos selados; primário não altera plano com metadados após selo.
Todos os efeitos exigem confirm=True, revalidação de inputs e orçamento finito.

## Aquisição seletiva e ambiente

Cache `.ai-edge-quantizer` fora do versionamento; ambiente próprio Python 3.12
em `.ai-edge-quantizer/venv`, sem tocar nos motores existentes. Fonte em source/,
manifesto source-manifest.json e receipt environment.json.
Consultar árvore Git do commit fixo; baixar só LICENSE, setup.py, requirements.txt,
fontes Python e receitas/políticas JSON necessárias sob ai_edge_quantizer/.
Excluir testes, colabs, *_test.py, test_utils.py e qualquer formato de modelo
(.tflite/.task/.litertlm/.gguf/.bin/.safetensors/.npz). Nunca executar setup na
aquisição. Conferir tamanho, UTF-8, SHA256 e Git blob SHA1 de cada arquivo,
rejeitar path traversal, symlinks, duplicações e metadados truncados.
Limites 256 arquivos, 1 MiB por arquivo, 8 MiB agregados. Publicação por staging
somente após validar tudo; preservar licença e originais.

Lock dedicado `integrations/ai-edge-quantizer-locks/py312.txt` com hashes e
versões completas, incluindo nightlies datadas (inicialmente tf-nightly
2.23.0.dev20261018 e ai-edge-litert-nightly 2.4.0.dev20261018; validar compatibilidade
real, sem fallback latest). Instalar dependências por uv/hash-check; importar
somente a fonte auditada em montagem read-only do worker, sem executar setup.py
ou instalar outro quantizador PyPI que não corresponda ao fork fixado.
Rejeitar venv preexistente sem marker Core. Sondar imports/versões em processo
separado, não no Core. Recibo vincula fonte, lock, worker e versão de Python;
metadata não comprova quantização ou compatibilidade de qualquer modelo.

O TDDHistory deve agregar TODAS as fontes cobertas do novo site-packages
gerenciado, como já faz para ITS-FINE; não ocultar dependências em diretório
venv ignorado. Marker específico core_edge_quantizer_environment_v1,
root e group=edge-quantizer, pyvenv 3.12; manter limites e cobertura antigos.
Vincular source-manifest, environment receipt e lock à identidade de fontes.

## Ensaio CPU autorizado

Worker standalone só importa NumPy/TensorFlow/quantizador no subprocesso.
Gerar localmente tf.Module com entrada [1,32], pesos/bias FP32 determinísticos,
saída [1,64], matmul+bias+relu. Não usar from_pretrained/model zoo/fit/optimizer.
Converter sem otimizações para .tflite FP32; quantizar via receita real
dynamic_wi8_afp32 do fork; executar float e quantizado no intérprete LiteRT CPU.
Usar seed42 e 16 entradas sintéticas, sem claim de dataset representativo.
Salvar float.tflite, quantized.tflite, recipe.json, evaluation.json e metrics.json.
Os arquivos devem ter hashes/tamanhos e os FlatBuffers marcador TFL3.

Sandbox bwrap sem rede, sem montagem da raiz do workspace/dados/credenciais,
somente runtime/venv/worker read-only e staging de saída read-write. CUDA
desabilitado; avaliação final com 1 thread. Processos com limites reais de
tempo/saída e encerramento do grupo via runner existente. Não instalar/desativar
proteções para fazer teste passar; sandbox indisponível é bloqueio explícito.

Gates congelados do toy: conversão float vs fórmula max_abs<=1e-4; quantizado
vs float MSE<=1e-3 e max_abs<=0.1, todos finitos, ao menos um tensor INT8.
Não exigir redução de tamanho para declarar numérico, nem inventar velocidade.
Relatar bytes/ratio medidos e deixar claro que overhead/modelo pequeno limita
generalização. Validate() com dados aleatórios upstream não é aceite de tarefa.

O Core recomputa MSE/max_abs dos arrays de evaluation.json em stdlib, valida
gates/artifacts/caminhos, e só publica manifest.json de sucesso após tudo.
Não confiar em status=passed do worker. Falha/timeout é relatório explícito;
nada de sucesso parcial ou arquivo anterior sobrescrito. report() revalida selo
e cada hash sem executar. Repetir um run_id íntegro pode reutilizar artefato;
deriva/conflito recusa. Inputs/outputs limitados, sem diretório arbitrário.

Flags: training_executed=false, external_checkpoint_downloaded=false,
user_data_read=false, policy_modified=false, externally_validated=false.
synthetic_inference_executed só true quando observado no ensaio validado;
falha incerta não vira alegação falsa de que nada executou.

## Critérios de Aceitação Executáveis

- `fonte` — origem fixada, arquivo selecionado/hash verificados e aquisição sem modelo externo.
- `ambiente` — venv própria, lock e confirmação; preservar ambientes/instalações alheios.
- `plano` — plano imutável, puro e fechado antes dos efeitos.
- `isolamento` — namespace sem rede/workspace e dependências fontes não ignoradas.
- `resultado` — erro/false success/deriva recusados; números e artefatos revalidados.
- `primario` — fachada/CLI preservam a autoridade do primário e o selo.

Ensaio real separado dos testes mockados e da suíte do quantizador. Resultado
numérico toy não é qualidade semântica, validação científica externa, pipeline
PyTorch→TFLite genérico nem comprovação de funcionamento no Gallery.
