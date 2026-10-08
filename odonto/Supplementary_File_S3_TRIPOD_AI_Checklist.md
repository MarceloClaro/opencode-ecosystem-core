# Supplementary File S3 — TRIPOD+AI reporting assessment

**Study:** OdontoCA tooth-level caries prediction, secondary analysis with development and child-grouped internal evaluation.

**Instrument:** TRIPOD+AI 2024, official checklist dated 11 January 2024: 27 numbered items, 52 rows including lettered subitems. Identifiers below match the original; short topic labels are paraphrases, not a substitute for its full recommendations. Source: Collins et al., *BMJ* 2024;385:e078378, [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378); official [checklist](https://www.tripod-statement.org/wp-content/uploads/2019/12/TRIPODAI_checklist.pdf) and [abstract checklist](https://www.tripod-statement.org/wp-content/uploads/2019/12/TRIPODAI-for-Abstracts.pdf).

**Assessment date:** 1 October 2026. AI-assisted internal reporting audit; not external independent review, certification or a numerical quality score. Both candidate models and exploratory recalibration are covered. Reporting completeness does not establish low risk of bias; see S4 separately.

**Evidence:** manuscript sections/tables, `real_clinical_prediction.py`, `calibrated_clinical_prediction.py` and `calibrated_clinical_internal_validation_corrected_sklearn190.json`. Section locations also apply to the Portuguese manuscript. **Reported:** sufficient information found. **Partial:** relevant information found but a component remains missing. **Absent:** required information not found. **N/A:** conditional analysis not performed. Author verification is still required. A disclosed gap remains a gap.

## Title, abstract and introduction

| ID | Topic | Status | Location and assessment |
|---|---|---|---|
| 1 | Title | Partial | Identifies tooth-level prediction and internal validation; does not explicitly identify multivariable model development. |
| 2 | Abstract | Partial | Principal methods/results appear. Recheck the final version against the separate 13-item abstract checklist; setting, eligibility and registration remain insufficient. Word limit alone does not establish completeness. |
| 3a | Rationale | Reported | §1 and §4.3 explain the prediction problem, earlier models and limitations of cross-cohort comparisons. |
| 3b | Use | Partial | §§1, 4.1–4.4, 5 define research scope; intended future users and care-pathway position remain unspecified. |
| 3c | Inequalities | Absent | Sociodemographic inequalities and their relevance to the dataset/application are not substantively discussed. |
| 4 | Objectives | Reported | End of §1 and §2.1 identify reconstruction, development, internal evaluation and calibration; no external evaluation is claimed. |

## Methods

| ID | Topic | Status | Location and assessment |
|---|---|---|---|
| 5a | Sources | Partial | §2.1 identifies worksheet, repository, revision and hash; source sampling and representativeness require fuller description. |
| 5b | Dates | Absent | Participant accrual and follow-up calendar dates are missing; publication or analysis dates do not replace them. |
| 6a | Setting | Partial | §§1–2.1 identify the longitudinal source but incompletely describe recruitment setting, centre count and geography. |
| 6b | Eligibility | Partial | §2.2/Table 1 describe transition selection, but original child recruitment criteria are incomplete. Secondary analysis does not make this inapplicable. |
| 6c | Treatment | Absent | Dental/preventive treatment during follow-up and its handling are not described; relevance and availability require verification. |
| 7 | Preparation | Partial | §§2.1–2.4 detail checks, reconstruction and preprocessing; differences in data quality across demographic groups were not assessed. |
| 8a | Endpoint | Partial | §2.2 defines healthy-to-carious transition and variable 2–5-month horizon; diagnostic examination procedures and demographic consistency need verification. |
| 8b | Assessors | Absent | Outcome examiner qualifications and relevant characteristics are not reported. Reusing recorded fields does not remove this reporting need. |
| 8c | Blinding | Absent | No source-study outcome-assessment blinding is documented. Temporal ordering alone does not demonstrate blinding. |
| 9a | Selection | Reported | §2.3 describes two feature sets defined before performance inspection and their rationale. This does not establish prospective registration. |
| 9b | Measurement | Partial | §§2.2–2.3/code identify visit-t fields and forbidden future fields; derived-field definitions/acquisition and assessor blinding remain incomplete. |
| 9c | Assessors | Absent | Clinical-predictor examiner qualifications and relevant characteristics are not documented; source measurement procedures need checking. |
| 10 | Size | Partial | §3.1/Table 1 give 996 transitions, 83 events, 81 children; no formal adequacy calculation addresses complexity and clustered evaluation. |
| 11 | Missingness | Partial | §§2.2–2.3 describe exclusions and training-fold imputation; variable-specific missingness and any missing-identifier/outcome losses need fuller reporting. |
| 12a | Partitioning | Reported | §2.4/code give five outer/three inner child-grouped folds, seed, corrected splitting and separation checks. |
| 12b | Encoding | Reported | §2.3 gives one-hot encoding, numeric standardisation and training-only transformations. |
| 12c | Fitting | Reported | §§2.3–2.4/code specify penalised logistic regression, four C values, average-precision tuning and nested internal evaluation. |
| 12d | Heterogeneity | Partial | §2.4 addresses dependence through grouping/resampling; cluster-level parameter/performance heterogeneity was not quantified. These are distinct analyses. |
| 12e | Measures | Reported | §2.4 defines scores, discrimination, calibration plots, reference models and paired comparisons; clinical utility was not evaluated. |
| 12f | Updating | Reported | §2.4 explains training-only intercept and positive-slope recalibration, inner cross-fitting and exploratory timing. |
| 12g | Predictions | Reported | §2.4/code show positive-class probabilities and train-fitted recalibration applied to each held-out outer fold. |
| 13 | Imbalance | Partial | §2.4 explains precision–recall assessment. Code uses no class weighting/resampling, but that absence is not explicit in the manuscript. |
| 14 | Fairness | Absent | No fairness assessment or approach to demographic performance differences is documented; no fairness claim is justified. |
| 15 | Output | Reported | §§2.2, 2.4, 3.3 define next-visit probabilities and state that no treatment threshold/decision rule was derived. |
| 16 | Datasets | Reported | §§2.1–2.4 establish common definitions/eligibility within one cohort, separated by child. No independent external dataset exists. |
| 17 | Ethics | Partial | Declarations identify secondary public-data use; approval/exemption and consent/waiver determination await author confirmation. |

## Open science and involvement

| ID | Topic | Status | Location and assessment |
|---|---|---|---|
| 18a | Funding | Absent | Declarations retain a completion field; sources and funder roles await confirmation. |
| 18b | Interests | Absent | Each author's competing interests await confirmation. |
| 18c | Protocol | Absent | No accessible protocol or explicit statement of no protocol is given; an architecture diagram alone is insufficient. |
| 18d | Registration | Absent | No registration details or explicit nonregistration statement is given. A software repository is not automatically study registration. |
| 18e | Data | Partial | Data declaration links the source and identifies the analysed file; reuse terms and final availability wording require verification. |
| 18f | Code | Partial | Scripts/results accompany the manuscript; persistent public access and reuse terms are not finalised. No archive DOI is established. |
| 19 | Involvement | Absent | Patient/public involvement or its explicit absence is not reported. No new recruitment does not answer this item. |

## Results

| ID | Topic | Status | Location and assessment |
|---|---|---|---|
| 20a | Flow | Partial | §3.1/Table 1 show filtering, sample/events/follow-up. JSON has 44 event-positive children; child-level outcomes should be distinguished from transition counts. |
| 20b | Characteristics | Partial | §3.1/Table 1 give counts/follow-up; predictor distributions, demographics, treatment and variable-specific missingness lack a descriptive table. |
| 20c | Distributions | Partial | Folds share a cohort. Fold logs give counts but not development/evaluation predictor distributions. |
| 21 | Counts | Partial | §3.1/JSON give totals and outer-fold child/event counts; each inner tuning partition's counts are not reported. |
| 22 | Specification | Partial | Reproducible analysis code is supplied; no single final fitted model, coefficients/preprocessing and deployment access conditions are released. |
| 23a | Performance | Partial | Tables 2–3/Figures 2–3 give estimates/selected intervals; calibration intervals, all score intervals and subgroup performance are incomplete. Uncertainty conditions on existing predictions. |
| 23b | Heterogeneity | N/A | Between-cluster performance heterogeneity was not examined; this conditional judgment does not demonstrate absence of heterogeneity. |
| 24 | Updating | Partial | §3.3/Table 3 and JSON report updated scores/selected intervals and fold parameters; no single final updated deployment model is supplied. |

## Discussion and use

| ID | Topic | Status | Location and assessment |
|---|---|---|---|
| 25 | Interpretation | Partial | §§4.1–4.4, 5 interpret uncertain differences/exploratory updating against prior work; fairness is not substantively discussed. |
| 26 | Limitations | Reported | §4.5 addresses cohort, size, follow-up, derived fields, missingness information, conditional uncertainty and exploratory updating. Disclosure does not remove bias. |
| 27a | Inputs | Partial | §§2.3, 4.4 discuss processing/prospective availability; no clinical procedure handles unavailable or poor-quality inputs. |
| 27b | Users | Absent | User interaction, training and required expertise for future implementation are unspecified; the software remains a research tool. |
| 27c | Research | Reported | §§4.4, 5 describe predictor verification, locked modelling, independent validation, fixed horizon, subgroup assessment and future utility analysis. |

## Actions before submission

Resolve author-controlled ethics/consent, funding, interests, protocol/registration and patient/public-involvement statements. Add verified source setting, recruitment dates/criteria, measurement and assessor details. Provide descriptive/missingness summaries and clarify partition counts, absence of fairness analysis and final-model status. Reconcile this map with the final abstract and data/code statements after edits. Unavailable details must be acknowledged, not fabricated.

This assessment replaces the earlier local 54-question document, whose numbering did not match TRIPOD+AI. No sample-adequacy conclusion follows from 83 events alone; a simple events-per-variable rule, penalisation or grouped validation cannot establish low bias. The companion PROBAST+AI appraisal is separate. This file does not alter the manuscript's 28-reference sequence.
