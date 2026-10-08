# AnalysisContext

Use this partial internal handoff across the NGS journey:

```text
AnalysisContext
├── objective {scientific_question, decision_to_make, desired_outcome}
├── materials[]
├── scientific_model
├── evidence[] {statement, status, source}
├── artifacts[]
├── open_questions[]
└── pending_user_decision
```

- `materials` covers inputs, metadata, references, plans, runs, and results,
  with identity, role, provenance, relationship, and observed state.
- `scientific_model` contains only supported assay, experimental unit, design,
  contrast, endpoint, reference, and validity assumptions.
- Evidence status is exactly `observed`, `inferred`, `assumed`, or `unknown`.
  A proposal, filename convention, or default is never an observation.
- Artifact types are `starting_point_assessment`, `analysis_plan`,
  `execution_plan`, `run_receipt`, and `result_review`.
- `pending_user_decision` contains at most one immediate user-owned choice.

Recover context before re-asking. Preserve provenance and conflicting facts.
Revise the scientific model with a reason; append or supersede artifacts rather
than overwriting history. Keep scientific blockers, runtime blockers, user
choices, execution state, and scientific acceptance distinct.

This is not a user form, linear stage machine, authorization record, or durable
store. Use MCP plan and run identities when available; otherwise keep a compact
task-local handoff.
