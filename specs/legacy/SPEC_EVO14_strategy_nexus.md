# SPEC_EVO14_strategy_nexus — NEXUS Pipeline Orchestrator
## Domain: strategy | Agent: nexus-strategy | Version: 1.0.0

### CT1: Phase transition validation
- **Given** a pipeline at Phase 2 (Foundation) with all quality gates PASSED
- **When** `advance_phase` is called
- **Then** returns Phase 3 (Build) and status "ADVANCED"
- **Given** a pipeline at Phase 2 with a FAILED gate
- **When** `advance_phase` is called
- **Then** returns Phase 2 and status "BLOCKED"

### CT2: Agent activation by phase
- **Given** NEXUS-Full mode and Phase 1 (Strategy)
- **When** `get_phase_agents` is called
- **Then** returns list containing "Studio Producer", "Senior Project Manager", "Sprint Prioritizer"
- **Given** NEXUS-Micro mode and Phase 3 (Build)
- **When** `get_phase_agents` is called
- **Then** returns a subset of agents with max 10 entries

### CT3: Quality gate evaluation
- **Given** quality criteria with all thresholds met
- **When** `evaluate_gate` is called
- **Then** returns verdict "PASS" with evidence list
- **Given** quality criteria with one threshold below minimum
- **When** `evaluate_gate` is called
- **Then** returns verdict "FAIL" with specific failing criterion

### CT4: Dev-QA loop retry tracking
- **Given** a task with 0 attempts
- **When** `record_qa_result("FAIL")` is called
- **Then** attempts = 1, status = "RETRY"
- **When** `record_qa_result("FAIL")` called 3 times total
- **Then** attempts = 3, status = "ESCALATED"
