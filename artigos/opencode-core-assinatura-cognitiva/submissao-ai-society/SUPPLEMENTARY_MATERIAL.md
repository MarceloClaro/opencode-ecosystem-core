# Supplementary Material

**Manuscript:** The house that helps to think: authored cognitive prostheses, agentic AI, and the care of memory

**Article type:** Open Forum

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

## Supplementary Table S2. Proposed N-of-1 outcome matrix

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

## Supplementary Table S3. Risks and safeguards

| Risk | Manifestation | Safeguard in the Core | Additional safeguard needed | Residual risk |
|---|---|---|---|---|
| Dependency | The author stops acting without the system | Durable state, documentation | Tool-free sessions; deliberate practice | Medium |
| Automation bias | Accepting agent suggestions without checking | Gates, tests, adversarial review | Independent red team; manual sampling | Medium |
| Deskilling | Loss of skills through offloading | Explicit specs and tests | Regular manual exercises | Medium |
| Hyperfocus | Work without pause; exhaustion | Timeouts, budgets | Time limits; social support; sleep | High |
| Perfectionism | Endless specs and tests | Acceptance criteria, stop rules | Scope review; “good enough” | High |
| Complexity | 681 specs, 646 tests, 845 cycles | Modularity, documentation | Pruning, technical debt, prioritization | High |
| Privacy | Memory records sensitive context | Local-first, allowlists | Redaction, retention, consent | Medium |
| False security | Language of “verified” | Anti-overclaim gate | User education; external audit | Medium |
| Isolation | Work mediated by agents | Collaboration via Blackboard | Human ties; community | High |
| Care overload | The system demands more than it returns | Doctor, helpdesk | Cost-benefit metric; pauses | High |

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

The article does not report experimental data. The corpus is documentary, and the counts are dated. The analysis distinguishes observation, interpretation, and prescription, as explained in Section 3.2.
