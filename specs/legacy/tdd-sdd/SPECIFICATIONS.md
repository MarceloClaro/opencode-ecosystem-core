# OpenCode Ecosystem — Formal Software Design Specification (SDD)
<!-- Version: 1.0.0 | Date: 2026-06-18 | Health Score: 96/100 -->

---

## TABLE OF CONTENTS

1. [Overview & Ecosystem Summary](#1-overview--ecosystem-summary)
2. [Specification Conventions](#2-specification-conventions)
3. [OrchestrationEngine Specification](#3-orchestrationengine-specification)
4. [MultiReasoningEngine Specification](#4-multireasoningengine-specification)
5. [ScientificProductionAgent Specification](#5-scientificproductionagent-specification)
6. [SROIScanner Specification](#6-sroiscanner-specification)
7. [Cross-Component Invariants](#7-cross-component-invariants)
8. [Error Taxonomy & Contracts](#8-error-taxonomy--contracts)
9. [Metrics & Observability Contract](#9-metrics--observability-contract)
10. [Revision History](#10-revision-history)

---

## 1. Overview & Ecosystem Summary

### 1.1 Ecosystem Identity

```
SYSTEM NAME   : OpenCode Ecosystem
AGENTS        : 128 (active, registered, health-checked)
SKILLS        : 155 (versioned, contract-bound)
MCPs          : 46  (Model Context Protocol servers)
HEALTH SCORE  : 96 / 100
SROI MODULE   : Social Return on Investment Scanner (active)
SPEC VERSION  : 1.0.0
AUTHORED      : 2026-06-18
```

### 1.2 Architectural Principles

- **Autonomy-with-Contracts**: Every agent operates autonomously but is bound by
  formal input/output contracts enforced at dispatch time.
- **Fail-Safe Degradation**: Every component declares a fallback path. No single
  failure propagates without containment.
- **Observability-First**: All state transitions emit structured telemetry events.
- **Reasoning Transparency**: Multi-reasoning chains are logged with confidence
  scores and mode labels; no black-box inference is permitted.
- **Social Impact Accounting**: SROI data is a first-class output type. Scientific
  outputs that do not quantify social impact are flagged, not blocked.

### 1.3 Component Dependency Map

```
OrchestrationEngine
  |-- dispatches to ---> [128 Agents]
  |-- consults --------> MultiReasoningEngine
  |-- integrates ------> SROIScanner
  |-- triggers --------> ScientificProductionAgent

MultiReasoningEngine
  |-- provides --------> reasoning trace, mode, confidence
  |-- receives --------> task context, agent capabilities

ScientificProductionAgent
  |-- consumes --------> SROIScanner output
  |-- reports to ------> OrchestrationEngine
  |-- uses ------------> MultiReasoningEngine (hypothesis & analysis stages)

SROIScanner
  |-- reads -----------> ecosystem telemetry, agent outputs
  |-- produces --------> SROI ratio, social value map, evolve recommendations
```

---

## 2. Specification Conventions

### 2.1 Notation

This document uses **Constrained English Specification (CES)** — a structured
plain-English equivalent of Z/Alloy notation, readable by both humans and
automated verification tools.

- `GIVEN`     -- pre-condition that MUST hold before the operation executes
- `WHEN`      -- the operation being described
- `THEN`      -- post-condition that MUST hold after successful execution
- `INVARIANT` -- property that holds at all times, regardless of operation
- `RAISES`    -- conditions under which an error is emitted
- `TYPE`      -- type alias definition
- `SCHEMA`    -- compound structure definition

### 2.2 Type Primitives

```
TYPE AgentId       = STRING (UUID v4 format)
TYPE SkillId       = STRING (snake_case, max 64 chars)
TYPE McpId         = STRING (URI format)
TYPE TaskId        = STRING (UUID v4 format)
TYPE ConfidenceVal = FLOAT  (range [0.0, 1.0])
TYPE HealthScore   = INT    (range [0, 100])
TYPE SROIRatio     = FLOAT  (range [-inf, +inf], typically [0.0, 20.0])
TYPE Timestamp     = STRING (ISO 8601 UTC)
TYPE ReasoningMode = ENUM   { deductive | inductive | abductive |
                              analogical | causal | meta }
TYPE StageStatus   = ENUM   { pending | running | passed | failed | skipped }
```

---

## 3. OrchestrationEngine Specification

### 3.1 Purpose

The OrchestrationEngine (OE) is the central nervous system of the OpenCode
ecosystem. It receives task requests, selects the optimal agent(s) based on
skill matching and load, dispatches tasks, monitors execution, handles fault
recovery, and aggregates results. It coordinates with MultiReasoningEngine
for complex routing decisions and with SROIScanner to enrich outputs.

### 3.2 Invariants

```
INVARIANT OE-I1:
  At all times, the number of concurrently dispatched tasks does not exceed
  the sum of all agent concurrency slots across all healthy agents.
  FORMALLY: |active_dispatches| <= SUM(agent.concurrency_slots)
             for all agent WHERE agent.health_status = "healthy"

INVARIANT OE-I2:
  Every dispatched task MUST have a corresponding TaskRecord with status
  in {pending, running, succeeded, failed, retrying}.
  No orphan tasks are permitted.

INVARIANT OE-I3:
  The OE maintains exactly one canonical routing table at any moment.
  Routing table updates are atomic -- no partial state is ever visible
  to concurrent dispatch operations.

INVARIANT OE-I4:
  The OE health score, derived from agent health, never exceeds 100.
  FORMALLY: 0 <= OE.health_score <= 100

INVARIANT OE-I5:
  Every error emitted by the OE carries: error_code, component_id,
  task_id (if applicable), timestamp, and a human-readable message.
```

### 3.3 Schema: TaskRequest

```
SCHEMA TaskRequest {
  task_id        : TaskId             -- REQUIRED, globally unique
  skill_required : SkillId            -- REQUIRED, must exist in skill registry
  payload        : OBJECT             -- REQUIRED, task-specific data
  priority       : INT [1..10]        -- REQUIRED, 1=lowest, 10=highest
  timeout_ms     : INT [100..3600000] -- OPTIONAL, default 30000
  require_sroi   : BOOLEAN            -- OPTIONAL, default false
  caller_agent   : AgentId            -- OPTIONAL, for chain tracking
  reasoning_hint : ReasoningMode      -- OPTIONAL, preferred reasoning mode
  metadata       : OBJECT             -- OPTIONAL, pass-through metadata
}
```

### 3.4 Schema: DispatchResult

```
SCHEMA DispatchResult {
  task_id          : TaskId
  assigned_agent   : AgentId
  status           : StageStatus
  started_at       : Timestamp
  completed_at     : Timestamp | NULL
  result_payload   : OBJECT | NULL
  reasoning_trace  : ReasoningTrace | NULL
  sroi_snapshot    : SROISnapshot | NULL
  error            : ErrorRecord | NULL
  retry_count      : INT [0..5]
}
```

### 3.5 Operation: dispatchTask

```
GIVEN
  req IS-A TaskRequest
  req.task_id NOT IN active_task_ids
  skill_registry.contains(req.skill_required) = TRUE
  EXISTS agent WHERE agent.skills.includes(req.skill_required)
                AND agent.health_status = "healthy"
                AND agent.load < agent.concurrency_slots

WHEN
  OE.dispatchTask(req)

THEN
  active_task_ids.add(req.task_id)
  selected_agent.load += 1
  task_record.status = "running"
  task_record.started_at = NOW()
  telemetry.emit({ event: "task_dispatched", task_id: req.task_id,
                   agent: selected_agent.id })

RAISES
  NO_CAPABLE_AGENT    if no healthy agent has req.skill_required
  DUPLICATE_TASK_ID   if req.task_id already in active_task_ids
  SKILL_NOT_FOUND     if skill_registry.contains(req.skill_required) = FALSE
  TIMEOUT_INVALID     if req.timeout_ms < 100 OR req.timeout_ms > 3600000
```

### 3.6 Operation: selectAgent (Load Balancing)

```
GIVEN
  candidate_agents = { a | a.health_status = "healthy"
                         AND a.skills.includes(skill_required) }
  candidate_agents IS NOT EMPTY

WHEN
  OE.selectAgent(skill_required, priority)

THEN
  RETURNS agent WHERE:
    score(agent) = (agent.concurrency_slots - agent.load)
                  * agent.health_score
                  * skill_affinity(agent, skill_required)
    agent = MAX(score) over candidate_agents

  TIEBREAK: agent with lowest task_count_total (least used globally)

RAISES
  NO_CAPABLE_AGENT if candidate_agents IS EMPTY
```

### 3.7 Operation: handleAgentFailure (Fault Tolerance)

```
GIVEN
  task_record.status = "running"
  agent.health_status transitions to "unhealthy" OR "timeout"

WHEN
  OE.handleAgentFailure(task_id, agent_id, failure_reason)

THEN
  IF task_record.retry_count < MAX_RETRIES (5):
    task_record.retry_count += 1
    task_record.status = "retrying"
    OE.dispatchTask(original_request)  -- re-dispatch to different agent
    telemetry.emit({ event: "task_retried", task_id, retry_count })
  ELSE:
    task_record.status = "failed"
    task_record.error = {
      code: "MAX_RETRIES_EXCEEDED",
      failed_agents: [...],
      last_failure: failure_reason
    }
    telemetry.emit({ event: "task_failed_permanently", task_id })

RAISES
  TASK_NOT_FOUND if task_record does not exist
```

### 3.8 Pre/Post Conditions Summary Table

| Operation         | Pre-Condition               | Post-Condition              |
|-------------------|-----------------------------|-----------------------------|
| dispatchTask      | Skill exists, agent healthy | Task running, agent loaded  |
| selectAgent       | Candidates non-empty        | Agent selected by score     |
| handleFailure     | Task running, agent failed  | Retry OR permanent failure  |
| completeTask      | Task running                | Task succeeded, agent freed |
| cancelTask        | Task pending/running        | Task cancelled, agent freed |
| refreshRouting    | Lock acquired               | Routing table updated       |

---

## 4. MultiReasoningEngine Specification

### 4.1 Purpose

The MultiReasoningEngine (MRE) provides structured, mode-aware reasoning
capabilities to the OrchestrationEngine and agents. It selects the most
appropriate reasoning mode based on task context, executes the reasoning
chain, returns a confidence-scored result, and falls back gracefully when
the primary mode fails or produces low-confidence output.

### 4.2 Invariants

```
INVARIANT MRE-I1:
  Every reasoning result carries a confidence value in [0.0, 1.0].
  Results with confidence < 0.4 MUST trigger fallback_mode evaluation.

INVARIANT MRE-I2:
  Reasoning chains are append-only logs. No step may be removed or
  mutated after it has been written to the chain.

INVARIANT MRE-I3:
  The MRE never invokes itself recursively beyond depth 3.
  FORMALLY: reasoning_chain.depth <= 3

INVARIANT MRE-I4:
  Mode transitions within a chain are logged with the reason for transition.
  Silent mode switches are a specification violation.

INVARIANT MRE-I5:
  "meta" reasoning mode can only be selected by the MRE itself (system),
  not by external callers. External requests for "meta" mode are downgraded
  to "deductive" with a warning logged.
```

### 4.3 Schema: ReasoningRequest

```
SCHEMA ReasoningRequest {
  request_id      : TaskId
  context         : OBJECT        -- domain context, facts, observations
  goal            : STRING        -- what needs to be determined
  preferred_mode  : ReasoningMode -- OPTIONAL hint from caller
  max_depth       : INT [1..3]    -- OPTIONAL, default 2
  confidence_floor: ConfidenceVal -- OPTIONAL, minimum acceptable confidence
  timeout_ms      : INT           -- OPTIONAL, default 10000
}
```

### 4.4 Schema: ReasoningTrace

```
SCHEMA ReasoningTrace {
  request_id   : TaskId
  mode_used    : ReasoningMode
  mode_chain   : ARRAY of ReasoningStep
  final_answer : OBJECT
  confidence   : ConfidenceVal
  fallback_used: BOOLEAN
  duration_ms  : INT
}

SCHEMA ReasoningStep {
  step_index        : INT
  mode              : ReasoningMode
  input             : OBJECT
  output            : OBJECT
  confidence        : ConfidenceVal
  transition_reason : STRING | NULL  -- why mode changed, if it did
}
```

### 4.5 Reasoning Modes -- Formal Contracts

#### Mode: deductive

```
GIVEN   : A set of universally accepted premises P = {p1, p2, ..., pn}
          and a logical rule R such that R(P) implies conclusion C
PRODUCES: C with confidence = f(rule_strength, premise_certainty)
TRIGGERS: when the problem is fully specified, premises are known
FALLBACK: inductive (if rule strength < threshold)
```

#### Mode: inductive

```
GIVEN   : A set of observations O = {o1, o2, ..., om} representing
          specific instances or patterns
PRODUCES: A generalized hypothesis H covering O, with confidence
          proportional to |O| and pattern consistency
TRIGGERS: when many examples are available, no universal rule exists
FALLBACK: abductive (if sample too small or inconsistent)
```

#### Mode: abductive

```
GIVEN   : An observation set O and a knowledge base KB
PRODUCES: The most likely explanation E such that KB union {E} implies O
          MINIMALITY: E is the simplest (Occam) explanation
TRIGGERS: when effect is known but cause is unknown
FALLBACK: analogical (if no good explanation found in KB)
```

#### Mode: analogical

```
GIVEN   : A source domain S with known solution, and a target domain T
          with known problem structure; mapping function M: S -> T
PRODUCES: Proposed solution T_sol = M(S_sol), confidence = similarity(S,T)
TRIGGERS: novel problem with familiar structural parallels
FALLBACK: deductive (if structural similarity < 0.5)
```

#### Mode: causal

```
GIVEN   : An event graph G where nodes are events and edges are
          causal links with probabilities
PRODUCES: A causal chain C explaining target outcome, with
          confidence = PRODUCT(edge_probabilities along C)
TRIGGERS: when root-cause analysis or intervention planning is needed
FALLBACK: abductive (if causal graph incomplete)
```

#### Mode: meta

```
GIVEN   : A set of previous reasoning attempts A = {a1,...,ak} that
          failed to exceed confidence_floor
PRODUCES: A revised reasoning strategy RS that selects among modes,
          orchestrates a multi-mode chain, and synthesizes results
TRIGGERS: SYSTEM ONLY -- activated when all primary modes fail
FALLBACK: NONE (meta is the final escalation; returns best-effort result)
```

### 4.6 Operation: reason

```
GIVEN
  req IS-A ReasoningRequest
  req.preferred_mode != "meta" (or is downgraded if so)

WHEN
  MRE.reason(req)

THEN
  selected_mode = selectMode(req.preferred_mode, req.context)
  trace = executeChain(selected_mode, req.context, req.goal, req.max_depth)
  IF trace.confidence < (req.confidence_floor OR 0.4):
    trace = escalate(trace, req)  -- attempt fallback_mode
  RETURNS ReasoningTrace

RAISES
  REASONING_TIMEOUT   if duration exceeds req.timeout_ms
  INVALID_CONTEXT     if req.context is null or malformed
  MAX_DEPTH_EXCEEDED  if recursion would exceed req.max_depth
```

---

## 5. ScientificProductionAgent Specification

### 5.1 Purpose

The ScientificProductionAgent (SPA) orchestrates the full lifecycle of
scientific output production: from hypothesis formation through peer review
to publication. It integrates with SROIScanner to quantify social impact,
with MultiReasoningEngine for hypothesis validation, and reports status
to OrchestrationEngine at each quality gate.

### 5.2 Invariants

```
INVARIANT SPA-I1:
  Pipeline stages execute strictly in order. No stage may begin before
  its predecessor has status = "passed".

INVARIANT SPA-I2:
  Each stage transition emits a quality_gate_event with: stage, status,
  score, evaluator_id, timestamp.

INVARIANT SPA-I3:
  The SROI snapshot is computed after data_analysis stage and attached
  to all subsequent outputs (writing, peer_review, publication).

INVARIANT SPA-I4:
  Citation count in writing stage MUST be >= MIN_CITATIONS (5).
  Papers with fewer citations are blocked at the writing quality gate.

INVARIANT SPA-I5:
  A publication cannot be emitted with integrity_score < 0.85.
  This gate is absolute -- no override is permitted by any caller.
```

### 5.3 Pipeline Stages

#### Stage 1: hypothesis_formation

```
GIVEN   : domain_context OBJECT, research_question STRING
INPUTS  : { domain_context, research_question, prior_knowledge[] }
OUTPUTS : { hypothesis STRING, null_hypothesis STRING,
            testability_score FLOAT, reasoning_trace ReasoningTrace }
VALIDATION_RULES:
  - hypothesis.length >= 20 chars (non-trivial)
  - testability_score >= 0.6 (must be empirically testable)
  - reasoning_trace.confidence >= 0.5
QUALITY_GATE : testability_score >= 0.6 AND reasoning_trace.confidence >= 0.5
RAISES  : UNTESTABLE_HYPOTHESIS if testability_score < 0.6
```

#### Stage 2: literature_review

```
GIVEN   : hypothesis from Stage 1
INPUTS  : { hypothesis, search_keywords[], max_sources INT }
OUTPUTS : { sources[], gap_analysis STRING, relevance_scores{},
            citation_graph OBJECT }
VALIDATION_RULES:
  - sources.length >= MIN_CITATIONS (5)
  - each source has: doi OR url, title, authors[], year
  - gap_analysis.length >= 50 chars
QUALITY_GATE : sources.length >= 5 AND gap_analysis present
RAISES  : INSUFFICIENT_LITERATURE if sources.length < 5
```

#### Stage 3: methodology_design

```
GIVEN   : hypothesis + sources from Stages 1-2
INPUTS  : { hypothesis, sources, constraints OBJECT }
OUTPUTS : { methodology STRING, metrics_to_measure[], controls[],
            reproducibility_checklist[], ethics_flags[] }
VALIDATION_RULES:
  - reproducibility_checklist.length >= 3 items
  - metrics_to_measure.length >= 1
  - ethics_flags evaluated (array may be empty if no concerns)
QUALITY_GATE : reproducibility_checklist.length >= 3 AND metrics defined
```

#### Stage 4: data_analysis

```
GIVEN   : methodology from Stage 3
INPUTS  : { raw_data OBJECT, methodology, statistical_methods[] }
OUTPUTS : { findings OBJECT, statistical_summary OBJECT,
            sroi_snapshot SROISnapshot, confidence_intervals OBJECT,
            anomalies[] }
VALIDATION_RULES:
  - statistical_summary contains: p_value, effect_size, sample_size
  - p_value <= 0.05 OR explicitly flagged as exploratory
  - sroi_snapshot.ratio IS NUMERIC
QUALITY_GATE : statistical_summary complete AND sroi_snapshot attached
RAISES  : INVALID_DATA if raw_data fails schema validation
          STATISTICAL_FAILURE if required statistics cannot be computed
```

#### Stage 5: writing

```
GIVEN   : all prior stage outputs
INPUTS  : { findings, sroi_snapshot, sources, methodology, template STRING }
OUTPUTS : { draft STRING, citation_count INT, word_count INT,
            abstract STRING, sroi_section STRING }
VALIDATION_RULES:
  - citation_count >= 5 (SPA-I4)
  - word_count >= 500
  - abstract.length BETWEEN 150 AND 350 chars
  - sroi_section present and references sroi_snapshot
QUALITY_GATE : citation_count >= 5 AND sroi_section present
```

#### Stage 6: peer_review

```
GIVEN   : draft from Stage 5
INPUTS  : { draft, reviewer_profiles[], review_criteria OBJECT }
OUTPUTS : { review_scores{}, aggregate_score FLOAT, revision_notes[],
            integrity_score FLOAT, recommendation ENUM{accept|revise|reject} }
VALIDATION_RULES:
  - aggregate_score in [0.0, 1.0]
  - integrity_score in [0.0, 1.0]
  - revision_notes is ARRAY (may be empty for accept)
  - recommendation consistent with aggregate_score:
      accept  <-- aggregate_score >= 0.80
      revise  <-- aggregate_score in [0.60, 0.80)
      reject  <-- aggregate_score < 0.60
QUALITY_GATE : recommendation = "accept" AND integrity_score >= 0.85
```

#### Stage 7: publication

```
GIVEN   : Stage 6 recommendation = "accept"
          Stage 6 integrity_score >= 0.85 (SPA-I5 -- ABSOLUTE)
INPUTS  : { draft, sroi_snapshot, review_scores, publication_target STRING }
OUTPUTS : { publication_id STRING, doi STRING, published_at Timestamp,
            sroi_impact_summary STRING, access_level ENUM{open|restricted} }
VALIDATION_RULES:
  - doi format: "10.XXXX/XXXXXXXX"
  - published_at is valid ISO 8601 timestamp
  - sroi_impact_summary.length >= 50 chars
QUALITY_GATE : integrity_score >= 0.85 (no override permitted)
RAISES  : INTEGRITY_GATE_BLOCKED if integrity_score < 0.85
          PUBLICATION_FAILED if doi assignment fails
```

#### Stage 8: presentation_generation

```
GIVEN   : Stage 7 has status = "passed"
INPUTS  : { paper_artifact OBJECT }
OUTPUTS : { mira_deck_present BOOLEAN, title STRING, theme STRING,
            slides[] SCHEMA{title STRING, content STRING} }
VALIDATION_RULES:
  - mira_deck_present == true
  - slides.length >= 5
  - theme is defined and non-empty (e.g. "neon-emerald")
QUALITY_GATE : mira_deck_present == true AND slides.length >= 5
RAISES  : MIRA_DECK_MISSING if deck is not generated
          INSUFFICIENT_SLIDES if slides.length < 5
```

---

## 6. SROIScanner Specification

### 6.1 Purpose

The SROIScanner (SS) measures, tracks, and reports the Social Return on
Investment generated by the OpenCode ecosystem and its agents. It reads
ecosystem telemetry, agent outputs, and external social metrics to compute
SROI ratios, generate social value maps, and produce evolve recommendations
that guide future agent configuration.

### 6.2 Invariants

```
INVARIANT SS-I1:
  SROI ratio is always computed as:
    SROI = total_social_value / total_investment_cost
  WHERE total_social_value > 0 AND total_investment_cost > 0.
  Division by zero MUST raise INVESTMENT_COST_ZERO.

INVARIANT SS-I2:
  Social value components are additive and independently auditable.
  Every value_component has: category, amount, currency, evidence_source.

INVARIANT SS-I3:
  SROI snapshots are immutable once signed (signed = timestamp + hash).
  Unsigned snapshots are draft state and clearly labeled.

INVARIANT SS-I4:
  The scanner never inflates value. If evidence_source is missing,
  the value_component amount is zeroed and flagged as unverified.

INVARIANT SS-I5:
  Evolve recommendations are ranked by expected_impact DESC and must
  each carry: rationale, confidence, expected_impact, effort_estimate.
```

### 6.3 Schema: SROISnapshot

```
SCHEMA SROISnapshot {
  snapshot_id        : STRING (UUID)
  computed_at        : Timestamp
  sroi_ratio         : SROIRatio
  total_investment   : FLOAT (> 0)
  total_social_value : FLOAT (> 0)
  value_components   : ARRAY of ValueComponent
  beneficiary_groups : ARRAY of STRING
  time_horizon_days  : INT (> 0)
  confidence_score   : ConfidenceVal
  is_signed          : BOOLEAN
  signature_hash     : STRING | NULL
  recommendations    : ARRAY of EvolveRecommendation
}

SCHEMA ValueComponent {
  category        : STRING
  description     : STRING
  amount          : FLOAT
  currency        : STRING (ISO 4217)
  evidence_source : STRING | NULL
  is_verified     : BOOLEAN
  proxy_used      : STRING | NULL
}

SCHEMA EvolveRecommendation {
  recommendation_id : STRING
  title             : STRING
  rationale         : STRING
  confidence        : ConfidenceVal
  expected_impact   : FLOAT
  effort_estimate   : ENUM { low | medium | high }
  target_component  : STRING  -- which ecosystem component to evolve
  priority_rank     : INT
}
```

### 6.4 Operation: computeSROI

```
GIVEN
  investment_cost > 0
  social_value_inputs IS-A ARRAY of ValueComponent (length >= 1)

WHEN
  SS.computeSROI(investment_cost, social_value_inputs, time_horizon_days)

THEN
  verified_components   = FILTER(social_value_inputs, is_verified = TRUE)
  unverified_components = FILTER(social_value_inputs, is_verified = FALSE)
  -- Zero out unverified components (SS-I4):
  unverified_components.forEach(c => { c.amount = 0; c.flagged = TRUE })

  total_social_value = SUM(verified_components.map(c => c.amount))
  sroi_ratio = total_social_value / investment_cost
  snapshot.sroi_ratio = sroi_ratio
  snapshot.is_signed = FALSE  -- draft until signSnapshot() called

RAISES
  INVESTMENT_COST_ZERO    if investment_cost <= 0   (SS-I1)
  EMPTY_VALUE_COMPONENTS  if social_value_inputs.length = 0
  NEGATIVE_SOCIAL_VALUE   if total_social_value < 0 (anomaly alert)
```

### 6.5 Operation: signSnapshot

```
GIVEN
  snapshot.is_signed = FALSE
  snapshot.sroi_ratio IS NUMERIC
  snapshot.computed_at IS VALID TIMESTAMP

WHEN
  SS.signSnapshot(snapshot)

THEN
  snapshot.signature_hash = HASH(snapshot_id + computed_at + sroi_ratio)
  snapshot.is_signed = TRUE

RAISES
  ALREADY_SIGNED    if snapshot.is_signed = TRUE
  INVALID_SNAPSHOT  if required fields missing
```

### 6.6 Operation: generateEvolveRecommendations

```
GIVEN
  snapshot IS-A SROISnapshot (signed or unsigned)
  ecosystem_telemetry OBJECT (agent health, skill usage, MCP metrics)

WHEN
  SS.generateEvolveRecommendations(snapshot, ecosystem_telemetry)

THEN
  recommendations = analyze(snapshot, telemetry) -> ARRAY of EvolveRecommendation
  recommendations = SORT_DESC(recommendations, expected_impact)
  recommendations.forEach((r, i) => r.priority_rank = i + 1)
  snapshot.recommendations = recommendations

RAISES
  TELEMETRY_MISSING if ecosystem_telemetry is null or empty
```

---

## 7. Cross-Component Invariants

```
INVARIANT GLOBAL-1: Timestamp Monotonicity
  Within any task lifecycle, timestamps are strictly non-decreasing.
  started_at <= completed_at for all completed tasks.

INVARIANT GLOBAL-2: Agent Count Bounds
  0 <= healthy_agents <= 128 at all times.
  The system degrades gracefully if healthy_agents < 10 (alert emitted).

INVARIANT GLOBAL-3: Skill Registry Consistency
  Every skill referenced in any task, agent profile, or spec record
  MUST exist in the central skill_registry (155 entries).

INVARIANT GLOBAL-4: MCP Availability
  At least 80% of registered MCPs (>= 37 of 46) must be reachable
  for the ecosystem health_score to remain >= 90.

INVARIANT GLOBAL-5: SROI Propagation
  Any ScientificProductionAgent output that reaches publication stage
  MUST carry an sroi_snapshot. Absence of sroi_snapshot at publication
  is a specification violation, not merely a warning.
```

---

## 8. Error Taxonomy & Contracts

| Error Code               | Component | HTTP Analog | Retryable | Description                                |
|--------------------------|-----------|-------------|-----------|---------------------------------------------|
| NO_CAPABLE_AGENT         | OE        | 503         | YES       | No healthy agent has required skill         |
| DUPLICATE_TASK_ID        | OE        | 409         | NO        | Task ID already exists                      |
| SKILL_NOT_FOUND          | OE        | 404         | NO        | Skill not in registry                       |
| MAX_RETRIES_EXCEEDED     | OE        | 503         | NO        | Agent failures exceeded retry limit         |
| REASONING_TIMEOUT        | MRE       | 504         | YES       | Reasoning chain exceeded time budget        |
| INVALID_CONTEXT          | MRE       | 400         | NO        | Reasoning context is null/malformed         |
| MAX_DEPTH_EXCEEDED       | MRE       | 422         | NO        | Reasoning recursion depth limit hit         |
| UNTESTABLE_HYPOTHESIS    | SPA       | 422         | NO        | Hypothesis testability score too low        |
| INSUFFICIENT_LITERATURE  | SPA       | 422         | YES       | Fewer than 5 valid sources found            |
| INTEGRITY_GATE_BLOCKED   | SPA       | 403         | NO        | Publication integrity score < 0.85          |
| INVESTMENT_COST_ZERO     | SS        | 400         | NO        | SROI denominator is zero                    |
| EMPTY_VALUE_COMPONENTS   | SS        | 400         | NO        | No social value inputs provided             |
| TELEMETRY_MISSING        | SS        | 503         | YES       | Ecosystem telemetry unavailable             |
| ALREADY_SIGNED           | SS        | 409         | NO        | Snapshot is immutable after signing         |

---

## 9. Metrics & Observability Contract

All components MUST emit the following telemetry event types:

```
METRIC TYPE     : counter | gauge | histogram | summary
REQUIRED LABELS : component, operation, status, environment

COUNTERS:
  opencode_tasks_total          { component, status }
  opencode_reasoning_total      { mode, outcome }
  opencode_sroi_snapshots_total { is_signed, confidence_band }
  opencode_publications_total   { recommendation, access_level }

GAUGES:
  opencode_agents_healthy       { }
  opencode_agents_total         { }
  opencode_skills_registered    { }
  opencode_mcps_reachable       { }
  opencode_health_score         { }

HISTOGRAMS:
  opencode_task_duration_ms       { skill_id }
  opencode_reasoning_duration_ms  { mode }
  opencode_sroi_ratio             { time_horizon }

SLOs (Service Level Objectives):
  Task dispatch latency p99      < 200ms
  Reasoning chain completion p95 < 5000ms
  SROI computation p99           < 1000ms
  Scientific pipeline end-to-end < 24h (wall clock)
  System health score            >= 90 (target: >= 96 as currently measured)
```

---

## 10. Revision History

| Version | Date       | Author       | Changes                                          |
|---------|------------|--------------|--------------------------------------------------|
| 1.0.0   | 2026-06-18 | OpenCode SDD | Initial formal specification for all components  |
| 1.1.0   | 2026-06-20 | Antigravity  | Added LPD simulation, ZKP biotelemetry, and MIRA |

---

## 11. Dentistry Simulation, Biotelemetry & Presentation Specifications

### 11.1 LPDModel (Periodontal Ligament Biomechanical Model)

#### 11.1.1 Purpose
Formally models the non-linear viscoelastic anisotropic behavior of the periodontal ligament (LPD) under orthodontic forces, ensuring physical simulation accuracy.

#### 11.1.2 State Space (Z Schema equivalent)
- `displacement` : VECTOR3D -- current structural displacement
- `strain` : TENSOR3D -- internal stress deformation tensor
- `stress` : TENSOR3D -- applied biomechanical load
- `viscoelastic_factor` : FLOAT (0.0..1.0) -- decay coefficient over time
- `anisotropy_directions` : ARRAY of VECTOR3D -- fiber alignment axes

#### 11.1.3 Invariants
- **LPD-I1**: Applied stress must not exceed the ligament rupture threshold.
  `FORMALLY: vonMises(stress) < LPD_RUPTURE_LIMIT (4.5 MPa)`
- **LPD-I2**: Viscoelastic recovery decay must be non-negative.
  `FORMALLY: viscoelastic_factor >= 0.0`
- **LPD-I3**: Non-linear deformation must strictly satisfy anisotropic constraint.
  `FORMALLY: project(strain, anisotropy_direction) <= MAX_FIBER_ELONGATION`

#### 11.1.4 Operations

##### simulatePressure
- `GIVEN`
  - `stress_mpa` : FLOAT
  - `delta_t` : FLOAT > 0
- `WHEN`
  - LPDModel.simulatePressure(stress_mpa, delta_t)
- `THEN`
  - Updates strain and displacement using non-linear viscoelastic decay equations.
- `RAISES`
  - `LPD_RUPTURE` if applied force exceeds 4.5 MPa.

---

### 11.2 ZKPTelemetryVerifier (Zero-Knowledge Proof for Biotelemetry)

#### 11.2.1 Purpose
Ensures cryptographic validation of patient biotelemetry data from intraoral scanners without exposing raw anatomical telemetry, preventing forensically untraceable tampering.

#### 11.2.2 State Space
- `proven_metrics` : MAP of (MetricId -> Hash) -- verified telemetry hashes
- `zkp_keys` : SCHEMA { public_key: String, verification_key: String }
- `audit_log` : ARRAY of ZkpVerificationRecord

#### 11.2.3 Invariants
- **ZKP-I1**: Telemetry metrics cannot be modified after proof generation.
  `FORMALLY: verify(proof, public_inputs) == true`
- **ZKP-I2**: Verification must be zero-knowledge -- no patient identifier or raw DICOM coordinates must be contained in the proof payload.

#### 11.2.4 Operations

##### generateTelemetryProof
- `GIVEN`
  - `raw_telemetry` : OBJECT
  - `verification_key` : STRING
- `WHEN`
  - ZKPTelemetryVerifier.generateTelemetryProof(raw_telemetry, verification_key)
- `THEN`
  - Returns a cryptographic proof and public inputs containing hashes.
- `RAISES`
  - `TAMPERED_DATA` if checksums do not match or raw data is malformed.

##### verifyTelemetryProof
- `GIVEN`
  - `proof` : OBJECT
  - `public_inputs` : OBJECT
- `WHEN`
  - ZKPTelemetryVerifier.verifyTelemetryProof(proof, public_inputs)
- `THEN`
  - Returns `true` if proof is valid, logs verification record to audit_log.
- `RAISES`
  - `INVALID_PROOF` if cryptographic verification fails.

---

### 11.3 MiraAnimator (MIRA Animation Engine)

#### 11.3.1 Purpose
Coordinates the biomechanical motion frame sequences and renders/simulates patient intraoral scan changes over time.

#### 11.3.2 State Space
- `current_frame` : INT >= 0
- `timeline` : ARRAY of Frame
- `is_looping` : BOOLEAN

#### 11.3.3 Invariants
- **MIRA-I1**: Frame transitions must be continuous and within biomechanical limits.
  `FORMALLY: distance(frame[t].coordinates, frame[t-1].coordinates) <= MAX_DRIFT`

#### 11.3.4 Operations

##### renderFrame
- `GIVEN`
  - `frame_index` : INT
  - `coordinates` : OBJECT
- `WHEN`
  - MiraAnimator.renderFrame(frame_index, coordinates)
- `THEN`
  - Computes interpolated frame transition.
- `RAISES`
  - `COLLISION_DETECTED` if anatomical limits are crossed.

---

## 12. OpenTwins Integration Specification

### 12.1 OpenTwinsAdapter

#### 12.1.1 Purpose
Adapts the OpenCode Ecosystem OrchestrationEngine to the distributed, compositional digital twin architecture defined by OpenTwins, enabling seamless state synchronization across Edge, Fog, and Cloud environments.

#### 12.1.2 State Space (Z Schema equivalent)
- `active_twins` : MAP of (TwinId -> OpenTwinsTwin) -- active compositional twins
- `edge_state` : MAP of (TwinId -> TwinState) -- local edge state snapshots
- `cloud_state` : MAP of (TwinId -> TwinState) -- synchronized cloud state snapshots
- `last_sync_timestamp` : MAP of (TwinId -> Timestamp) -- last sync timestamps
- `registered_agents` : MAP of (AgentId -> TwinsAgentRole) -- agent role mappings

#### 12.1.3 Invariants
- **OTW-I1**: Sync latency between local edge state and cloud state must not exceed 500ms.
  `FORMALLY: timeDiff(NOW(), last_sync_timestamp[twin_id]) <= 500ms` for all synchronized active twins.
- **OTW-I2**: All messages sent through the adapter must conform to the OpenTwins compositional schema.
  `FORMALLY: validateCompositionalSchema(message) == true`
- **OTW-I3**: Any agent registered with OpenTwinsAdapter must exist in the OpenCode skill registry.
  `FORMALLY: central_skill_registry.contains(agent.skill_id) == true`

#### 12.1.4 Operations

##### registerTwin
- `GIVEN`
  - `twin_id` : STRING
  - `components` : ARRAY of STRING
- `WHEN`
  - OpenTwinsAdapter.registerTwin(twin_id, components)
- `THEN`
  - Instantiates an entry in active_twins and initialize edge_state and cloud_state.
- `RAISES`
  - `DUPLICATE_TWIN` if twin_id is already registered.
  - `INVALID_COMPONENTS` if components array is empty.

##### syncTwinState
- `GIVEN`
  - `twin_id` : STRING
  - `state_data` : OBJECT
- `WHEN`
  - OpenTwinsAdapter.syncTwinState(twin_id, state_data)
- `THEN`
  - Updates the local edge_state and pushes changes to cloud_state, updating the last_sync_timestamp.
- `RAISES`
  - `TWIN_NOT_FOUND` if twin_id is not registered.
  - `SYNC_TIMEOUT` if network latency exceeds 500ms.

##### dispatchToTwinsAgent
- `GIVEN`
  - `twin_id` : STRING
  - `task` : OBJECT
  - `role` : TwinsAgentRole
- `WHEN`
  - OpenTwinsAdapter.dispatchToTwinsAgent(twin_id, task, role)
- `THEN`
  - Maps the task to an OpenTwins-compatible agent and executes the action.
- `RAISES`
  - `UNMAPPED_AGENT_ROLE` if no local agent matches the role requirements.

---

## 13. Anny Integration Specification (Anatomical Face-Body Twin)

### 13.1 AnnyAnatomicalAdapter

#### 13.1.1 Purpose
Adapts the Anny PyTorch parametric body model (representing shape, pose, and UV texture coordinates) to the OpenCode dentistry digital twin, enabling the placement of intraoral scans inside a fully parameterized facial and cranial model for complete dental-facial aesthetics and biomechanics analysis.

#### 13.1.2 State Space (Z Schema equivalent)
- `patient_shape` : SCHEMA { age: FLOAT, height_cm: FLOAT, weight_kg: FLOAT, gender: ENUM{male|female} } -- phenotype shape parameters
- `joints_pose` : MAP of (JointId -> Vector3DRotation) -- joint rotations (e.g. head, jaw/mandible flexion)
- `uv_coordinates` : ARRAY of VECTOR2D -- normalized texture coordinate mappings
- `anatomical_mesh_hash` : STRING -- cryptographic hash of the current parameterized mesh geometry

#### 13.1.3 Invariants
- **ANY-I1**: Demographic phenotype parameters must remain within strictly valid anatomical bounds.
  `FORMALLY: age in [0.0..120.0] AND height_cm in [30.0..250.0] AND weight_kg in [2.0..250.0]`
- **ANY-I2**: Mandibular joint rotation angles must not exceed safe biological range of motion.
  `FORMALLY: joints_pose["temporomandibular_joint"].flexion <= 45.0 degrees` (maximum safe jaw opening angle)
- **ANY-I3**: Texture coordinates must be mapped within the normalized UV coordinate space.
  `FORMALLY: 0.0 <= uv.u <= 1.0 AND 0.0 <= uv.v <= 1.0` for all uv in uv_coordinates.

#### 13.1.4 Operations

##### parameterizePatientShape
- `GIVEN`
  - `profile` : SCHEMA { age: FLOAT, height_cm: FLOAT, weight_kg: FLOAT, gender: STRING }
- `WHEN`
  - AnnyAnatomicalAdapter.parameterizePatientShape(profile)
- `THEN`
  - Generates parameterized shape blendshapes and computes the new anatomical_mesh_hash.
- `RAISES`
  - `INVALID_DEMOGRAPHICS` if parameters violate ANY-I1.

##### animateAnatomicalPose
- `GIVEN`
  - `joint_id` : STRING
  - `rotation` : Vector3DRotation
- `WHEN`
  - AnnyAnatomicalAdapter.animateAnatomicalPose(joint_id, rotation)
- `THEN`
  - Updates the joints_pose rotation vector for joint_id and computes the deformed mesh geometry.
- `RAISES`
  - `ROM_LIMIT_EXCEEDED` if joint rotation exceeds safe range of motion limits (ANY-I2).

##### mapIntraoralTexture
- `GIVEN`
  - `mesh_vertices` : ARRAY of VECTOR3D
  - `uvs` : ARRAY of VECTOR2D
- `WHEN`
  - AnnyAnatomicalAdapter.mapIntraoralTexture(mesh_vertices, uvs)
- `THEN`
  - Maps the intraoral scan mesh UVs to the oral cavity region of the parametric body model.
- `RAISES`
  - `OUT_OF_BOUNDS_UV` if coordinates violate ANY-I3.

---

*End of OpenCode Ecosystem Formal Software Design Specification*
*Total components specified: 9 | Total invariants: 34 | Total operations: 20*
