# Supplementary File S2 — OdontoCA evidence and reproducibility audit

## Public clinical source

The authors' Table S1 was retrieved from the repository at commit e5868fe5664460c7aac1c5b6d7980776ad26b29c. The file SHA-256 was b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa. The analysis scripts do not redistribute the spreadsheet. All 11 source-cohort count checks passed. The original 997 healthy-to-next-visit transitions included 84 events; one event had a recorded zero-month follow-up and was excluded from the 996-row, 83-event prediction analysis.

## Synthetic notebook: archived values versus independent rerun

The table compares saved notebook output with execution of its current cell sources on the local runtime. Both runs contained 686 transitions, 54 events, and 36 synthetic children. Metrics differ. The original execution environment and results ZIP were unavailable, so the cause has not been established. Neither set is a clinical result.

| Model | Archived AP | Rerun AP | Archived ROC-AUC | Rerun ROC-AUC | Archived Brier | Rerun Brier |
|:--|--:|--:|--:|--:|--:|--:|
| ca_rule | 0.081743 | 0.095082 | 0.534546 | 0.556435 | 0.073223 | 0.072032 |
| clinical | 0.105386 | 0.111871 | 0.590571 | 0.624018 | 0.073304 | 0.072101 |
| micro | 0.095530 | 0.067185 | 0.532613 | 0.430614 | 0.131119 | 0.076856 |
| combined | 0.074825 | 0.086585 | 0.480397 | 0.539235 | 0.081224 | 0.078489 |

The rerun used Python 3.14.4, NumPy 2.5.1, pandas 3.0.3, SciPy 1.18.0, and scikit-learn 1.9.0. The notebook SHA-256 was b0bc028dffd4b60164b1428f79126988607e5e2f28bc97ef736ce4168fa63eac. A future release should pin the executable environment, preserve the original run manifest and out-of-fold probabilities, and investigate the difference before using synthetic metrics as a regression gate.

## Real-data split-policy and Colab reproduction

The user's Colab output was independently reproduced with Python 3.11.16 and scikit-learn 1.6.1 using the legacy shuffled `StratifiedGroupKFold` policy. It is retained as a historical reproduction in `real_clinical_internal_validation_sklearn161.json`. The [scikit-learn issue 32478](https://github.com/scikit-learn/scikit-learn/issues/32478) documents the relevant defect: version 1.6.1 shuffled group outcome counts without preserving the mapping to group labels. The primary manuscript analysis instead uses deterministic permutation of child-group labels followed by stratified group splitting, recorded as `corrected_permuted_groups`. The corrected policy is implemented in `calibrated_clinical_prediction.py` and its aggregate output is `calibrated_clinical_internal_validation_corrected_sklearn190.json`. Its scikit-learn 1.6.1 sensitivity run, `calibrated_clinical_internal_validation_corrected_sklearn161.json`, agreed numerically with the 1.9.0 run to approximately 1e−8. The eligible cohort, source-file hash, 996 analysis transitions, 83 events and 81 children are identical under both policies; fold assignments and performance differ between the legacy and corrected policies. These estimates must not be averaged or treated as independent validations.

| Split policy and model | Average precision | ROC area | Brier score | Calibration slope |
|:--|--:|--:|--:|--:|
| Legacy 1.6.1, minimal | 0.2318 | 0.7551 | 0.07594 | 0.653 |
| Legacy 1.6.1, spatial | 0.2414 | 0.7802 | 0.07259 | 0.917 |
| Corrected 1.9.0, minimal | 0.1665 | 0.6865 | 0.08060 | 0.516 |
| Corrected 1.9.0, spatial | 0.1784 | 0.7372 | 0.07536 | 0.605 |

These are uncalibrated pooled out-of-fold scores. The manuscript reports the corrected policy as the main analysis and identifies the older Colab scores only when discussing reproducibility. The historical scores were reproduced to numerical precision apart from negligible floating-point changes in probability scores and calibration coefficients.

## Calibration procedure and interpretation

For every outer fold, model tuning used only the outer training children. Inner child-disjoint cross-fitted probabilities at the chosen regularisation value were the sole inputs to two logistic probability updates: an intercept-only map and an intercept-plus-positive-slope map. Each outer test child received predictions from the model fitted on all outer training rows, transformed by parameters learned on those same outer training children through inner cross-fitting. No outer test outcome entered calibrator fitting. Calibration was evaluated from the pooled untouched outer-fold predictions.

For the corrected policy, intercept-and-slope updating lowered minimal-model Brier score from 0.08060 to 0.07451, paired difference −0.006096 (95% child-bootstrap interval −0.011729 to −0.000672). Its log-loss difference was −0.02034 (−0.04058 to 0.00020). Spatial-model Brier score changed from 0.07536 to 0.07395, paired difference −0.001410 (−0.003082 to 0.000373). Intercept-only Brier differences for both models included zero. These intervals resample fixed cross-fitted predictions and do not capture model-development variation. The apparent Brier improvement for one model does not establish transportability, net benefit, or readiness for patient decisions.

## Test and evidence review

- The saved notebook's 24 PASS and two SKIP entries describe its own technical test report. TDD-005 can catch the assertion raised by its own negative test. TDD-010 checks a tautology. GATE-04 and GATE-05 are hard-coded true. These status counts are therefore not independent proof that every named property was verified.
- The new real-data analysis asserts patient disjointness in every outer fold, forbids future/outcome fields from candidate predictors, verifies valid probability ranges and class orientation, and reproduces the published cohort counts before fitting. Its five outer and three inner group folds are documented in `calibrated_clinical_internal_validation_corrected_sklearn190.json`.
- The 1,000 child-cluster bootstrap replicates resample fixed out-of-fold predictions. They do not refit the nested models and therefore omit development-stage variability. The updated calibration plot uses eight quantile bins, a descriptive view with limited resolution.
- Public source data are real, but this manuscript has no real microbiome alignment, image model, external-site or temporal validation, prospective prediction, or clinical decision threshold.

## Executed analysis outputs

- reproduce_evidence.py: clinical source counts plus an independent synthetic rerun.
- `real_clinical_prediction.py`: original minimal and spatial clinical analysis.
- `calibrated_clinical_prediction.py`: corrected patient splitting and training-only calibration.
- `evidence_v2.json`, `real_clinical_internal_validation_sklearn161.json`, and `calibrated_clinical_internal_validation_corrected_sklearn190.json`: aggregate results, seed, software versions, source hash, and fold summaries.
- `Figure_1_pipeline_v2_compact.png`, `Figure_2_discrimination_corrected_sklearn190.png`, and `Figure_3_calibration_corrected_sklearn190.png`: manuscript figures. The detailed proposed workflow is in Supplementary File S1.

The 28 journal-article DOIs listed in the manuscript were checked against Crossref (HTTP 200) and doi.org (HTTP 302) on 30 September 2026; metadata and the DOI-resolution audit are preserved in references_crossref_verified.json and references_verified.md.
