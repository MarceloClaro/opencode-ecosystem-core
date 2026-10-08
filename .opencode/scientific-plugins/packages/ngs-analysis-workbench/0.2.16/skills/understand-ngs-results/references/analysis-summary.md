# Analysis summary writing guide

Use this format for the model-authored review returned in the conversation and,
when authorized by the parent skill, preserved as `analysis_summary.md`.

## Workbench summaries

Begin with a dedicated `Takeaway:` line containing one complete, plain-text
sentence written specifically for Workbench run history. Capture the analysis,
sample or study, relevant scientific context, and most important finding or
blocker; target 100 characters and never exceed 125 characters, including any
non-completed lifecycle prefix. For example:

Takeaway: FastQC of Allobates femoralis skin RNA-seq sample SRR8288062; high-quality reads, no trimming needed.

For an incomplete run, begin the takeaway with its actual lifecycle, such as
`Running:`, `Failed:`, or `Blocked:`, and identify the key missing result or
blocker. After a blank line, write one plain-language, scientifically contextual
paragraph of five or six sentences. In natural prose, answer these questions:

- What scientific question, sample, study, or downstream decision motivated it?
- What actually ran, remains partial, failed, or is blocked?
- What do the verified outputs show, or which evidence is unavailable?
- What do those observations mean for the original scientific question?
- What conclusions remain unsupported by the available evidence?
- What is the smallest justified next scientific or operational step?

Blend answers when needed rather than adding visible labels or forcing a rigid
template. Preserve measured findings and name the true blocker when present.
The paragraph is the visible Workbench run-detail summary; only the separate
takeaway sentence appears in run history, without its `Takeaway:` label or an
ellipsis.

Do not use Markdown formatting, field labels such as "Study:" or "Experimental
unit:", tables, URLs, checksums, plan/run IDs, workflow paths, or configuration
details in this opening paragraph. Keep technical identifiers, structured
evidence, provenance, and expanded interpretation in the following sections.

## Detailed review sections

Include these stable sections after the opening paragraph:

1. **Scientific context and question:** the original experimental objective,
   supported organism, tissue, condition, perturbation, sample design, domain,
   hypothesis, or downstream decision. Include only context supplied by the
   user or independently verified in study/sample metadata; mark unknowns.
2. **Question, lifecycle, and endpoint:** what was requested, what actually
   ran, which observed processes finished or failed, and the durable run
   identity when one exists. Never describe a pending, failed, canceled,
   orphaned, blocked, or inaccessible analysis as completed.
3. **Key findings:** the important observed values, units, denominators,
   per-sample differences, and source artifact paths.
4. **Interpretation:** what the evidence means for data quality and the
   original scientific question, including notable outliers or failure modes.
   For FastQC, explain readiness and limitations for the stated experimental
   goal without claiming biological findings from read QC alone.
5. **Artifacts:** the verified results, QC reports, and provenance grouped as
   described by the parent skill.
6. **Limitations and blockers:** recorded failure or readiness evidence,
   inaccessible logs or artifacts, unsupported or inconclusive claims, missing
   outputs, reference or fixture constraints, warnings, and calibrated
   confidence. Say explicitly which final QC or biological conclusions cannot
   be made.
7. **Recommended next step:** the smallest justified scientific or operational
   action.

Explain the outputs; do not just reproduce tool-generated prose, enumerate
files, or declare a completed workflow successful without interpreting its
evidence. Do not invent differential expression, cell calling, biological
conclusions, or missing metrics. Identify downsampled, reduced-reference, or
fixture runs as technical smoke tests when appropriate.
