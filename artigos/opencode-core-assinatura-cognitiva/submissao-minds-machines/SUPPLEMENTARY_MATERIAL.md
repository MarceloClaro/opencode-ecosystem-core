# Supplementary Material

**Manuscript:** The house that helps to think: authored cognitive prostheses, agentic AI, and the limits of epistemic sovereignty

**Article type:** Original Research

**Note:** This supplementary material is anonymized for double-blind review. The repository URL is provided in the title page.

---

## Supplementary Table S1. Repository indicators

Counts obtained by direct inspection of the checkout on 10 November 2026; Git base `1ce6ae98`. Counts of files or configuration do not measure quality, availability, authentication, inference, or external validation. Uncommitted files may change the totals.

| Indicator | Value | Source | Limit of interpretation |
|---|---:|---|---|
| Specification files | 681 | `specs/SPEC-*.md` | Count of files; not quality or currency |
| Test files | 646 | `tests/test_*.py` | Count; not coverage or reliability |
| Evolution cycles | 845 | `evolution/cycles.json` | Includes legacy entries; scores are self-assessment |
| Configured agents | 374 | `opencode.json` | Configuration; not availability |
| MCP servers | 35 | `opencode.json` | Configuration; not authentication |
| Commands | 35 | `opencode.json` | Configuration |
| Structural checks | 22 | `doctor.py` | Local checks; not external certification |
| Most recent cycle | R1131 | `evolution/cycles.json` | Local record; no hardware or external validation |

The reconciled block in `README.md` records 366 agents and 35 MCPs. The difference between the two counts is documentary and should be reconciled before publication.

## Supplementary Table S2. Cognitive functions and architectural mechanisms

| Move | Externalized function | Mechanism | Evidence | Limit |
|---|---|---|---|---|
| Perceive | Context and memory | MetaBus, shared memory, confidence ledger | `mci/metabus.py` | Selective memory; last 1,000 events |
| Specify | Intention and criteria | SpecRegistry, SpecVerifier, acceptance criteria | `sdd/spec_engine.py`, `specs/` | A spec does not guarantee execution |
| Delegate | Division of labor and attention | Blackboard A2A, Agent Cards, Trust Engine | `mci/blackboard.py`, `trust/` | Agents are not people |
| Execute | Sequencing and persistence | TaskRuntime, DAG, leases, budget | `mci/task_runtime.py` | Does not decide what matters |
| Verify | Reality testing | TDD, SpecVerifier, BehavioralGate, anti-overclaim | `sdd/tdd_runner.py`, `mci/metacognitive_gate.py` | A test is not scientific truth |
| Reflect | Consolidation and learning | Reflexion, EvolutionRegistry, lessons | `mci/reflexion.py`, `evolution/cycles.py` | Self-assessment is not external validation |

## Supplementary Table S3. From reported vulnerability to architectural hypothesis

| Reported vulnerability | Design hypothesis | Mechanism in the Core | Limit |
|---|---|---|---|
| Loss of context between sessions | Externalized, retrievable memory | MetaBus, `shared_memory.json`, confidence ledger | Selective memory; not a total backup |
| Difficulty starting and sequencing long tasks | Contracts and decomposition | Specs, acceptance criteria, DAGs, leases | Requires human intention |
| Risk of confusing conviction with evidence | Independent verification | TDD, SpecVerifier, anti-overclaim gate | A test is not scientific truth |
| Hyperfocus and difficulty stopping | Budgets and limits | Timeouts, stop rules, doctor, helpdesk | The system does not control the user |
| Fear of losing continuity | Durable state and resumption | TaskRuntime, checkpoints, EvolutionRegistry | Preserves traces, not the person |
| Need for meaning and legacy | Documentation and teaching | Book, manual, MIRA, didactic pipeline | Does not measure pedagogical efficacy |

## Supplementary Table S4. Proposed N-of-1 outcome matrix

The selection should be finalized with a clinician and, where applicable, an ethics committee.

| Outcome | Instrument | Frequency | Hypothesis | Risk of distortion |
|---|---|---|---|---|
| Time to resume after interruption | Automatic log + diary | Daily | The Core reduces the cost of resumption | Measure depends on context |
| Task completion rate | System log | Weekly | The Core increases completion | May incentivize easy tasks |
| Errors in routine tasks | Blinded checklist | Weekly | The Core reduces errors | May miss rare errors |
| Perceived cognitive load | Adapted NASA-TLX | Weekly | The Core reduces load | Self-report subject to bias |
| Trust calibration | Declared confidence vs. accuracy | Weekly | The Core improves calibration | May measure trust in the system, not judgment |
| Sense of agency | Brief scale + interview | Biweekly | The Core preserves agency | Multidimensional concept |
| Sleep and social life | Habit diary | Weekly | The Core does not worsen these domains | Self-report |
| Stress symptoms | Validated scale | Biweekly | The Core does not increase stress | Requires clinical interpretation |

## Supplementary Note S1. Glossary of architectural terms

- **MetaBus.** A metacognitive event bus and shared memory layer. It stores episodic and semantic memory, a confidence ledger, and events that can be consulted before a new decision.
- **Blackboard.** A shared task board on which agents volunteer for tasks based on Agent Cards, declared capabilities, historical confidence, and load.
- **Agent Card.** A description of an agent's capabilities, input schema, and status.
- **Trust Engine.** A component that maintains historical scores by action, applies a behavioral gate, and records outcomes.
- **BehavioralGate.** A pre-execution guard that authorizes or blocks an action based on a trust score and a threshold.
- **TaskRuntime.** A local, deterministic runtime for nanogranular task graphs, with states, leases, budgets, and recovery.
- **SpecRegistry.** A registry of formal specifications with acceptance criteria.
- **SpecVerifier.** A component that verifies whether a delivery satisfies the acceptance criteria of a specification.
- **EvolutionRegistry.** A registry of evolution cycles with objective, changes, score, lessons, hashes, and state anchors.
- **Token Economy.** A coordination layer with stake, slashing, and a fee market. It is a governance device, not a measure of truth or competence.

## Supplementary Note S2. Anonymized inventory of the documentary corpus

The analysis used the following categories of documents. File paths are preserved for verifiability; the repository URL is provided in the title page.

| Category | Examples | Use in the article |
|---|---|---|
| Project overview | `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, `MANUAL.md` | Research question, cycle, layers, limits |
| Self-correction | `CORRIGENDUM.md` | Anti-overclaim policy and public correction |
| Design preface | R909 preface and specification | Definition of cognitive signature |
| Memory and orchestration | `mci/metabus.py`, `mci/blackboard.py`, `mci/task_runtime.py`, `mci/reflexion.py`, `mci/metacognitive_evaluator.py`, `mci/metacognitive_gate.py` | Externalized memory, delegation, interruption, reflection, verification |
| Specification and tests | `sdd/spec_engine.py`, `sdd/tdd_runner.py`, `sdd/tdd_history.py`, `specs/`, `tests/` | Contract, acceptance criteria, test evidence |
| Trust and economy | `trust/trust_engine.py`, `trust/behavioral_gate.py`, `economy/token_economy.py` | Confidence, behavioral gate, stake, slashing |
| Evolution | `evolution/cycles.py`, `evolution/cycles.json` | Cycles, lessons, hashes, self-assessment |
| Configuration | `opencode.json` | Agent, MCP, and command counts |
| Diagnostics | `doctor.py`, `helpdesk.py` | Structural checks and orientation |

The article does not report experimental data. The corpus is documentary, and the counts are dated. The analysis distinguishes observation, interpretation, and prescription, as explained in Section 2.2.
