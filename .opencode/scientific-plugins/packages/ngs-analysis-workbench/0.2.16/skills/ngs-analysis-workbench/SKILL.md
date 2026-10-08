---
name: ngs-analysis-workbench
description: Orchestrate an NGS analysis journey across understanding data, designing an analysis, running an approved workflow, and understanding results. Use for capability questions, broad or ambiguous requests, guided starts, public demos, resume requests, or work spanning multiple journey segments.
---

# NGS Analysis Workbench

Recover the partial [AnalysisContext](../../references/analysis-context.md),
then derive a turn-local route from the request, available context, and next
unresolved decision. Do not persist routing as scientific context.

## Route in order

1. Answer pure capability questions without starting a journey. Treat “what
   should I try?” as a guided start.
2. For resume requests, recover available artifacts, plan and run identities,
   files, and conversation context before asking the user to repeat anything.
3. Route a concrete goal directly to its focused skill.
4. For broad, ambiguous, or first-task requests, follow
   [Guided entry](references/guided-entry.md).

| Current need | Follow |
| --- | --- |
| Establish available inputs, metadata, relationships, missing facts, or supportable tasks | [understand-ngs-data](../understand-ngs-data/SKILL.md) |
| Translate a scientific outcome into a defensible design and evidence contract | [design-ngs-analysis](../design-ngs-analysis/SKILL.md) |
| Discover implementations, check readiness, plan, approve, run, monitor, or recover | [run-ngs-analysis](../run-ngs-analysis/SKILL.md) |
| Explain completed, partial, failed, or blocked evidence against the original scientific objective and next decision | [understand-ngs-results](../understand-ngs-results/SKILL.md) |

Chain skills only after the current skill produces its artifact and the request
requires the next segment. A result may route back to data understanding or
design. After a structured selection, continue the selected journey in the
same turn rather than returning another prompt for the user to copy.

## Routing rules

- Ask only for a decision that remains unresolved; do not repeat a choice the
  user already made or ask for facts that can be inspected.
- Do not treat a manifest, catalog entry, expected filename, or completed run
  as proof of executable readiness or scientific validity.
- Lead with the user's outcome and next decision, not internal routing.
