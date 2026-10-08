# Title page — separate file for double-anonymised submission

> **Instructions for the authors (delete this block before submission).**
> This file exists because the *Journal of Dentistry* uses double-anonymised peer review and
> requires the title page and the manuscript to be uploaded as **separate files**. The manuscript
> file carries no author identity. Complete every field marked `[REQUIRED]` below.
> Fields marked `[OPTIONAL]` may be left blank if genuinely not applicable, but a blank
> declaration is better than a placeholder — an unfilled placeholder will be returned by the
> editorial office.

---

## Manuscript

**Article type:** Original Research Article — secondary analysis with internal validation

**Title:** Tooth-level prediction of early-childhood caries from a public longitudinal cohort:
reproducible internal validation with patient-separated folds

**Running title:** Tooth-level prediction of early-childhood caries

**Keywords (1–7, English):** early-childhood caries; clinical prediction; primary teeth; spatial
features; internal validation; calibration; oral microbiome

*(7 keywords — within the 1–7 range required by the journal.)*

---

## Authors and affiliations — `[REQUIRED]`

| # | Full name | Degrees | Affiliation(s) | Email | ORCID iD |
|---|---|---|---|---|---|
| 1 | `[REQUIRED]` | | `[REQUIRED]` | `[REQUIRED]` | |
| 2 | `[REQUIRED]` | | | `[REQUIRED]` | |
| 3 | `[REQUIRED]` | | | `[REQUIRED]` | |

**Affiliation list — `[REQUIRED]`**

`[REQUIRED]` — *[Department, Institution, Street, City, Postal code, Country]*
`[REQUIRED]` — *[as above]*

**Corresponding author — `[REQUIRED]`**

> `[REQUIRED full name]`
> `[REQUIRED postal address]`
> Email: `[REQUIRED]` · Telephone: `[REQUIRED]` · ORCID: `[REQUIRED]`

---

## Declarations — must match the manuscript file exactly

### Funding — `[REQUIRED]`

`[REQUIRED]` — *State each funder and grant number, or write: "This research received no
specific grant from any funding agency in the public, commercial, or not-for-profit sectors."*

### Declaration of competing interest — `[REQUIRED]`

`[REQUIRED]` — *Either: "The authors declare that they have no known competing financial interests
or personal relationships that could have appeared to influence the work reported in this paper."*
*Or list each interest: funder, relationship, and role.*

### CRediT authorship contribution statement — `[REQUIRED]`

Use the official CRediT taxonomy (https://www.credit.org/). One or more roles per author; every
author must be listed. Suggested role set for this study:

| Author | Conceptualization | Methodology | Software | Formal analysis | Writing – original draft | Writing – review & editing | Data curation | Visualization |
|---|---|---|---|---|---|---|---|---|
| `[REQUIRED]` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

*Adjust to the real contributions. The journal requires CRediT and will not process a manuscript
without it.*

### Ethics approval and consent to participate — `[REQUIRED]`

This is a **secondary analysis of a publicly released supplementary table**. No participants were
recruited for this work. The authors must supply one of the following, with institution, protocol
or exemption number, and date:

- `[REQUIRED]` — *Institutional Review Board name, protocol number, approval date.*
- `[REQUIRED]` — *Name of the reviewing body, reference number, and date of the determination that
  the work was exempt or required no approval.*
- `[REQUIRED]` — *Confirmation that the source study obtained ethics approval, with the approving
  body and protocol number as reported in reference [1].*

**Consent:** not applicable — no individual participants were recruited or contacted for this
secondary analysis. `[REQUIRED — confirm this wording matches the actual determination]`

### Declaration of generative artificial intelligence use

Present in the manuscript as submitted. Confirm the wording below reflects actual practice:

> OpenAI Codex assisted with code review, execution of the secondary analysis, manuscript drafting,
> reference checking, and diagram preparation. Figure 1 was prepared with that assistance and is
> identified as such in its legend. The named authors inspected the data provenance, code, numerical
> results, citations, and final text, and retain full responsibility for the submitted work.

`[REQUIRED — confirm accuracy, or edit to match actual use]`

### Data and code availability

Present in the manuscript as submitted. Under the journal's Option B policy, deposit, citation and
linking of materials is encouraged; where materials cannot be shared, the reason must be given.

- `[REQUIRED]` — *Zenodo/OSF DOI for the analysis scripts and aggregate results, if deposited.*
- Raw source records are **not** redistributed: the source spreadsheet is third-party material
  released by the original investigators, and its reuse terms are theirs to set.

---

## Reporting-guideline statements already in the manuscript

The Methods (`Study design, source, and provenance` and `Tooth transitions and analysis cohort`)
now carry the guideline statements and point to both completed checklists:

> This study is reported in accordance with the TRIPOD+AI statement [10] and was appraised with
> PROBAST+AI [11]. The completed checklists are provided as Supplementary Files S3 and S4.

**TRIPOD+AI** is the applicable guideline. **PRISMA-ScR is not** — this is a prediction-model
development and internal-validation study, not a scoping review.

---

## Upload checklist — Editorial Manager

| Item | File in `submission_package/` | Status |
|---|---|---|
| Title page | `Journal_of_Dentistry_Title_Page.pdf` | Complete — author fields are placeholders |
| Anonymised manuscript | `Manuscript_Anonymised.docx` | Complete — no author identity |
| Figure 1 | `Figure_1.png` | 400 DPI, vector PDF also available |
| Figure 2 | `Figure_2.png` | 300 DPI |
| Figure 3 | `Figure_3.png` | 300 DPI |
| Graphical abstract | `Graphical_Abstract.png` / `.pdf` | Drafted, optional |
| Highlights (3–5) | `Highlights.pdf` | 5 points, each ≤85 characters |
| Cover letter | `Cover_Letter_Journal_of_Dentistry.pdf` | Complete |
| Supplementary File S1 | `Supplementary_File_S1_Architecture.pdf` | Architecture diagram |
| Supplementary File S2 | `Supplementary_File_S2_Technical_Audit.pdf` | Technical audit |
| Supplementary File S3 | `Supplementary_File_S3_TRIPOD_AI_Checklist.pdf` | Complete, 4 items marked incomplete |
| Supplementary File S4 | `Supplementary_File_S4_PROBAST_AI_Assessment.pdf` | Complete, overall risk High |

### Artwork resolution — resolved

Figures 2 and 3 were previously rasterised at 170 DPI, below the journal's 300 DPI minimum. The
source file `Table_S1.xlsx` was obtained from the original investigators' repository, its SHA-256
and commit were verified, and `manuscript_assets/calibrated_clinical_prediction.py` was re-run
against it. All 96 aggregate statistics were reproduced exactly, confirming that the re-render
reflects the same analysis. Figures 2 and 3 were then re-exported at 300 DPI and Figure 1 at
400 DPI. No image was upscaled artificially.

### Outstanding before submission

1. **Author-supplied declarations.** Ethics approval, funding, competing interests and the CRediT
   contribution statement are placeholders. These require the authors and cannot be inferred.
2. **TRIPOD+AI incomplete items.** Items 17, 25, 29, 42 and 49 remain unfilled; see S3 for the
   specific gap in each.
3. **Code availability identifier.** The manuscript states that code will be deposited and that a
   persistent identifier should be supplied. Confirm the archive and add the DOI, or state why
   sharing is not possible, as the journal requires.
