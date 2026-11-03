---
spec_id: SPEC-935-R920
title: Cenários acadêmicos MiroFish do projeto à defesa
component: academic.adversarial_research.simulation, academic.adversarial_research.service
status: proposed
test_file: tests/test_r920_academic_simulation.py
evidence_contract:
  version: 1
  mode: criterion-runtime-v1
  criteria:
    planejamento:
    - tests/test_r920_academic_simulation.py::test_plan_has_no_execution
    reproducao:
    - tests/test_r920_academic_simulation.py::test_cases_are_deterministic_and_stage_specific
    evidencia:
    - tests/test_r920_academic_simulation.py::test_preserve_negative_evidence_without_approval
    integridade:
    - tests/test_r920_academic_simulation.py::test_stale_or_tampered_plan_rejected_before_execution
    limites:
    - tests/test_r920_academic_simulation.py::test_strict_limits_and_global_reservations
    cancelamento:
    - tests/test_r920_academic_simulation.py::test_cooperative_cancel_and_timeout
    local:
    - tests/test_r920_academic_simulation.py::test_local_only_without_scores_or_answers
    servico:
    - tests/test_r920_academic_simulation.py::test_service_actions_persist_and_verify
---

# R920 — ensaio acadêmico sintético, não validação científica

## Contrato

Reutilizar o motor MIT `mirofish.social.engine.SocialSimulationEngine` e os
verificadores locais existentes. Não copiar AGPL, criar perfis permanentes,
chamar LLM/rede/subprocessos ou fabricar participantes, evidências e respostas.
Papéis de cientistas/banca são objetos efêmeros referenciando SPECIALISTS.
O ensaio não controla a aplicação ChatGPT nem constitui revisão por pares.

Novo módulo `academic/adversarial_research/simulation.py` expõe
`plan_simulation(project, cases=None, seed=42, limits=None)`,
`run_simulation(plan, cancelled=False, should_stop=None)` e
`render_simulation_report(result)`. O serviço existente acrescenta operações
`simulation_plan` (project/cases/seed/limits), `simulation_run` (plan/cancelled)
e `simulation_report` (simulation_id). Rejeitar campos desconhecidos.

Estágios: projeto, metodologia, qualificacao, analise, resultados, pre_defesa,
defesa. Cenários: base, banca_divergente, fonte_indisponivel. Grupos:
cientistas_metodo, cientistas_resultados, banca_interdisciplinar. Cada caso:
case_id único, stage/group/scenario, rounds e agents (defaults 4/6; 1–12).
Até 24 casos. Default: um caso pre_defesa_base. Seed inteiro não booleano.
Limites globais: max_steps 1–34 (default34), max_rounds 1–288 (default288),
max_actions 1–3456 (default3456), timeout_seconds finito >0 até120 (default30).
Não renovar orçamento por caso. Reservar agents*rounds antes de cada caso;
ações não usadas não permitem exceder o teto reservado. Não cortar casos.

Planejar somente faz intake e hashes; zero revisão-base, motor, persistência
ou MetaBus. Preservar projeto original. Plano contém project, cases, seed,
limits, artifact_sha256, evidence_manifest e simulation_id determinístico
academic-sim-<32hex>; plan_sha256 cobre todos os campos exceto ele próprio.
JSON canônico UTF-8, ensure_ascii=False, sort_keys=True, allow_nan=False,
separators=(",",":"). Revalidar estrutura, hashes e arquivos antes da execução;
recalcular o hash não torna configuração inválida aceitável.

Executar revisão-base `review_research` UMA VEZ por chamada, sem callbacks de
agentes, e motor uma vez por caso admitido. Remover legacy_board/score/verdict
da saída; sentimento é apenas dinâmica sintética, nunca aprovação. Cada etapa
tem perguntas e evidências próprias; qualitativo não exige poder estatístico.
Perguntas tipadas: stage, question, required_evidence, target_claim_ids e origin
local_rule/question_template/hypothetical. Pergunta local preserva objection_id,
alvos e evidência exigida. Cenários alteram interação/premissas, nunca fontes
factuais: fonte_indisponivel é hipótese, não constatação. Nenhuma resposta é
inventada. Objeções e evidências negativas permanecem pendentes.

Resultado possui base_review, evidence_manifest, cases, unresolved_objection_ids,
unresolved_gaps, usage, status completed/partial/cancelled, stop_reason,
execution_started, simulation_executed, execution_complete e trajectory_sha256.
usage: review_steps, cases_executed, rounds_executed, actions_executed,
actions_reserved. Cancelamento prévio não executa nada. should_stop é callback
interno booleano sem argumentos, consultado entre casos; não integra JSON.
Prazo monotônico global; interrupção cooperativa, não preempção rígida durante
um caso/revisão. Preservar resultados parciais. Revisão incompleta impede
execution_complete mesmo quando todos os casos sociais terminaram.

Trajetória cases é JSON estável sem campos de relógio (inclusive datas de
perfis/actions); sub-seed SHA por caso, nunca hash() Python. Flags obrigatórias
false: scientifically_approved, external_validation, agent_inference_executed,
llm_inference_executed, confidence_promoted. human_review_required=true.
Não emitir score, verdict ou respostas-modelo. Renderer declara SIMULAÇÃO e
“não constitui validação científica”, perguntas/evidências e revisão humana.

Somente simulation_run do serviço persiste atomicamente em self.state/simulations
com report_sha256 canônico cobrindo tudo exceto ele próprio; registra observação
no primário sem promover confiança. Consulta valida ID, tamanho, symlink e hash,
sem executar novamente. Não modificar engine/board nem seu comportamento legado.

## Critérios de Aceitação Executáveis

- `planejamento` — plano e hashes sem execução/efeitos.
- `reproducao` — mesmos dados/seed geram trajetória idêntica, perguntas e situações diferenciadas.
- `evidencia` — revisão única, não mutação, contradições preservadas, sem aprovação sentimental.
- `integridade` — adulteração e arquivos obsoletos recusados antes do motor/revisão.
- `limites` — validação estrita e reserva global de rounds/ações.
- `cancelamento` — cancelamento/prázo cooperativos conservam saída parcial.
- `local` — sem rede, inferência, pontuação ou resposta fabricada.
- `servico` — fachada do primário persiste e consulta com integridade.
