# SPEC_EVO14_strategy_handoff — Handoff Templates
## Domain: strategy | Agent: handoff-templates | Version: 1.0.0

### CT1: Standard handoff document generation
- **Given** from_agent="Backend Architect", to_agent="Frontend Developer", phase=2, task_ref="T-042"
- **When** `generate_handoff` is called with type="standard"
- **Then** returns dict with keys: metadata, context, deliverable, quality
- **Assert** metadata.from == "Backend Architect" and metadata.priority is set

### CT2: QA verdict generation (PASS)
- **Given** task_id="T-001", developer="Frontend Developer", attempt=2
- **When** `generate_qa_verdict` is called with verdict="PASS"
- **Then** returns dict with verdict="PASS", evidence dict non-empty
- **Assert** acceptance_criteria all marked as passed

### CT3: QA verdict generation (FAIL)
- **Given** task_id="T-002" with specific issues list
- **When** `generate_qa_verdict` is called with verdict="FAIL"
- **Then** returns dict with verdict="FAIL", issues list non-empty
- **Assert** each issue has category, severity, expected, actual, fix fields
- **Assert** retry_instructions contains "Do NOT introduce new features"

### CT4: Escalation report after 3 failures
- **Given** task with 3 failed attempts history
- **When** `generate_escalation` is called
- **Then** returns dict with attempts_exhausted=3, root_cause_analysis non-empty
- **Assert** resolution_options contains at least 3 options
- **Assert** impact_assessment.blocking is a non-empty list
