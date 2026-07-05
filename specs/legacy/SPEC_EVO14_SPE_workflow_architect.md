# SPEC_EVO14_SPE_WORKFLOW_ARCHITECT -- Workflow Architect Engine v1.0

**Domain**: agency-agents/specialized/specialized-workflow-architect
**Python**: 3.12, stdlib only
**Status**: Draft

---

## CT-01: Workflow Completeness
Step 2 sem success path = is_complete=False. step_count=2, has_cleanup=False.

## CT-02: Handoff Contract Validation
HandoffContract: is_rest=True, schema_keys={"email","password","name"}, timeout=10s.

## CT-03: Full Workflow Tree
3 steps, todos com success path + branches (failure, timeout, conflict). is_complete=True, 2 handoffs.

## CT-04: Missing Handoff Detection
3 steps multi-actor sem handoff contracts definidos gera aviso de validacao.

---

## Implementation
- `scripts/workflow_architect_engine.py`: WorkflowTree, Step, StepOutcome, HandoffContract
- `tests/test_workflow_architect.py`: 4 CTs via pytest
