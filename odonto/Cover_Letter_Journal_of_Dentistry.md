# Cover letter — Journal of Dentistry

*Draft for the authors to complete. Fields marked `[REQUIRED]` need author input; the rest is
written against the actual manuscript and can stand as-is.*

---

`[REQUIRED date]`

Editor
*Journal of Dentistry*
Elsevier

Re: Original Research Article — *Tooth-level prediction of early-childhood caries from a public
longitudinal cohort: reproducible internal validation with patient-separated folds*

---

Dear Editor,

We submit this manuscript for consideration as an Original Research Article.

**What the study does.** It is a secondary analysis of a publicly released tooth-level table from a
longitudinal study of early-childhood caries. We reconstructed the published cohort exactly — all
eleven prespecified count checks matched, from 2,504 source records in 89 children through to 997
eligible healthy-to-next-visit transitions with 84 events — and then developed two prespecified
penalised logistic models for the clinical-minimal and clinical-plus-spatial predictor sets. The
primary evaluation uses five outer and three inner child-grouped folds so that no child contributes
teeth to both training and test sets, with regularisation chosen on average precision in the inner
folds only.

**What the study finds.** Discrimination exceeded chance but was modest: ROC area 0.737 (95%
child-cluster bootstrap interval 0.660–0.804) and average precision 0.178 (0.138–0.239) against an
event fraction of 0.083 for the spatial model, and 0.686 (0.618–0.754) and 0.166 (0.120–0.246) for
the minimal model. Every paired comparison between the two models had an interval spanning zero.
Training-only intercept-and-slope recalibration reduced the minimal model's held-out Brier score
from 0.0806 to 0.0745; the spatial model's change was uncertain.

**Why we report it this way.** We consider the negative and null results to be the paper's
substance rather than its defect. A reanalysis that quietly dropped the null comparisons, or that
reported the recalibrated ranking improvement as new information, would misrepresent the data. We
therefore derive no treatment threshold, perform no decision-curve analysis, and state explicitly
that the result is not ready for patient-level decision support.

**Fit to the journal.** The work sits in the translational and digital-dentistry space the journal
covers. Its contribution is a reproducible, leakage-controlled, patient-separated internal validation
of tooth-level caries prediction under a published reporting standard, accompanied by a technical
audit of the underlying pipeline that identified a group-remapping defect in a prior analysis policy
and quantified its effect on the estimates. We believe the methodological reporting is the
transferable part.

**Reporting and reproducibility.** The study follows TRIPOD+AI and was appraised with PROBAST+AI;
both completed checklists accompany the manuscript. The analysis scripts, aggregate result files,
figures, and the SHA-256 hash of the exact source file analysed are available on request and will be
deposited with a persistent identifier. Raw source records are not redistributed, as they are
third-party material whose reuse terms belong to the original investigators. The source dataset is
available via Qiita as reported in the cited source publication.

**Declarations.** `[REQUIRED — confirm each statement]`

- CRediT authorship contribution statement is provided on the title page.
- Funding: `[REQUIRED — state each funder and grant number, or declare no specific grant]`.
- Competing interests: `[REQUIRED — declare none, or list each]`.
- Ethics: `[REQUIRED — state the reviewing body, protocol or exemption number, and date for this
  secondary analysis]`.
- Generative artificial intelligence: OpenAI Codex assisted with code review, execution of the
  secondary analysis, manuscript drafting, reference checking, and preparation of the Figure 1
  schematic, which is identified as AI-assisted in its legend. The authors inspected the data
  provenance, code, numerical results, citations, and final text and retain full responsibility.

**Exclusivity.** This manuscript is original, has not been published previously, and is not under
consideration by any other journal. `[REQUIRED — all authors confirm]`

**Suggested reviewers.** `[REQUIRED]` — we suggest reviewers with expertise in early-childhood
caries epidemiology and in clinical prediction model validation, and who have no institutional
conflict with the authors.

We thank you for considering this submission and look forward to your decision.

Sincerely,

`[REQUIRED — corresponding author name, degrees, affiliation, email, telephone, ORCID]`

---
