# Reproducible tooth-level prediction of early-childhood caries from a public longitudinal cohort: an internally validated clinical-spatial study

## Abstract

**Objectives:** To strengthen the OdontoCA methodology by reproducing a public tooth-level cohort and estimating next-visit caries risk with patient-separated validation, while distinguishing this analysis from the project's synthetic technical run.

**Methods:** Public Table S1 was hash-checked and processed with OdontoCA tooth-transition definitions. The outcome was progression from a healthy tooth at visit *t* to caries at the next consecutive visit. One nonpositive follow-up interval was excluded. Two prespecified logistic models used either minimal clinical variables or clinical plus spatial variables available in the source table at *t*. Five outer and three inner child-grouped folds separated model selection from evaluation. Within each outer training partition, inner out-of-fold probabilities were used to fit intercept-only and intercept-and-slope recalibration, which was then applied to untouched outer test children. We report pooled out-of-fold discrimination, probability scores, calibration, and 1,000 paired child-cluster bootstrap intervals.

**Results:** The source cohort counts reproduced exactly: 2,504 records from 89 children yielded 997 eligible healthy-to-next-visit transitions and 84 events. The analysis set contained 996 transitions from 81 children and 83 events (8.33%). Under a corrected, reproducible group-split policy, uncalibrated average precision was 0.166 (95% bootstrap interval 0.120–0.246) for the minimal model and 0.178 (0.138–0.239) for the spatial model; ROC areas were 0.686 (0.618–0.754) and 0.737 (0.660–0.804), respectively. Their paired discrimination differences included zero. Training-only intercept-and-slope recalibration reduced the minimal model's held-out Brier score from 0.0806 to 0.0745 (paired difference −0.00610, 95% interval −0.01173 to −0.00067); the spatial model's change from 0.0754 to 0.0740 had an interval including zero.

**Conclusions:** Reproducible cohort construction and training-only recalibration support further research. The observed discrimination and improvement in one probability score are internal and exploratory; external validation and independent verification of derived predictors are needed before clinical use.

**Keywords:** early-childhood caries; clinical prediction; primary teeth; spatial features; internal validation; calibration; oral microbiome.

## 1. Introduction

Early-childhood caries develops across individual teeth, changing oral environments, and repeated visits. The source study by Yang and colleagues assembled a tooth-resolved longitudinal plaque dataset and reported its own microbiome-based prediction results [1]. Clinical and behavioural information also predicts subsequent caries [2]. Other longitudinal studies associate oral microbial community development with future disease [3,4], and salivary microbiome prediction in very young children has been investigated [5]. These published findings motivate research on tooth-level prediction but do not validate a different model or software implementation.

Biofilm simulation offers a mechanistic rationale for examining local interactions: in-silico studies have explored the roles of sugar exposure and bacterial interactions [6,7]. OdontoCA extends that idea to a probabilistic cellular-automaton rule and clinical, spatial, microbiome, and image branches. Its saved v1.3.2 `CI_SMOKE` notebook executed the synthetic branch; its v1.9.1 architecture diagram described a broader protocol. Neither artifact alone established performance in real children.

Prediction studies require particular care when records from the same child recur across teeth and visits. Nested cross-validation can reduce model-selection bias [8], while data leakage can inflate apparent performance [9]. TRIPOD+AI provides reporting guidance [10], and PROBAST+AI separates reporting from risk-of-bias and applicability assessment [11]. We therefore treat an executable pipeline, internal validation, and independent clinical validation as distinct evidence states.

Earlier work on spatial and temporal oral microbiota [12] and oral community composition [13] reinforces the biological motivation. At the same time, a review found limited prospective validation of early-childhood caries risk tools [14], and a systematic review identified modifiable risk factors that are not represented fully by a tooth-level spreadsheet [15]. The objective here was to reproduce the public clinical cohort underlying OdontoCA, develop two transparent baseline risk models, quantify internal predictive performance and calibration with child-level uncertainty, and identify the evidence required to progress toward clinical evaluation.

## 2. Materials and methods

### 2.1. Study design, source, and provenance

This was a secondary analysis of the public `all_metadata` worksheet in the source study's `Table_S1.xlsx`, obtained from the authors' [Single-tooth-ECC repository](https://github.com/HuangShiLab/Single-tooth-ECC). The exact file used in this analysis had SHA-256 `b7819fee81efbe2e227b7700c3cd86ce8bc6f7fe6f49da6214f4107d099184fa`. We did not redistribute the source records. The OdontoCA notebook's reconstruction functions were executed independently against that file. Its expected counts were compared with observed counts before model fitting. All clinical results in this paper come from this public table, not from the notebook's synthetic `CI_SMOKE` output.

The source study also makes sequencing data available via Qiita [1]. We did not complete an exact clinical SampleID-to-BIOM match, analyse real microbial counts, or use dental images. The planned microbiome analysis would need to address the compositional nature of sequencing counts and fit all selection and log-ratio transformations inside training folds [16,17]. Figure 1 distinguishes the executed clinical analysis from these unrun branches.

![Figure 1. OdontoCA evidence workflow. Blue paths were executed in separate analyses: the original synthetic CI_SMOKE technical path and the new public-cohort clinical reconstruction and internal prediction. Amber paths are proposed microbiome and image research. External validation and matched-cohort fusion remain gates before clinical claims.](manuscript_assets/Figure_1_pipeline_v2_compact.png){width=6.8in}

### 2.2. Tooth transitions and analysis cohort

The published spreadsheet contains patient, tooth-position, visit, and current tooth-status fields. We mapped the 20 primary-tooth positions to FDI identifiers, removed composite position `T5161` from individual-tooth modelling, and linked each child's same tooth to its next recorded visit. Only consecutive visit indices were retained. The binary outcome was `H→C` versus `H→H`, where `H` means clinically healthy at visit *t* and `C` means carious at the next visit. Teeth already carious at *t* were excluded from onset prediction. Current-visit neighbour status and host caries experience were derived or taken from the visit-*t* record. Source-defined `HostGroup`, future tooth status, time to decay, next-visit status, and follow-up interval were barred from predictors.

The notebook's original transition rule yielded 997 eligible `H` transitions and 84 events. We excluded one transition with a recorded follow-up interval of zero months from the primary predictive analysis; that transition was an event. The final set contained 996 transitions from 81 children. Follow-up time was not a fixed horizon; observed positive intervals ranged from two to five months. Consequently, the estimated risk refers to the next recorded visit within this range, not to a universal two-month endpoint.

### 2.3. Prespecified candidate models

Two penalised logistic-regression models were specified before examining their performance. The **minimal clinical** model used tooth position, age in months at *t*, host dmfs at *t*, and the number of adjacent carious teeth at *t*. The **clinical-spatial** model added the source table's current-visit host status, niche categories, spatially weighted dmfs, and three spatial summary fields. This comparison asks whether recorded spatial context adds predictive information to a simple clinical baseline. Source-derived spatial fields were used as provided; their construction and availability at a prospective clinical visit require further independent verification.

Categorical fields were imputed by the most frequent training value and one-hot encoded; numeric fields were median-imputed and standardised. All operations were fitted on training rows within each fold. The regularisation parameter `C` was chosen from 0.01, 0.1, 1, and 10 using average precision in the inner folds. The positive probability was explicitly selected for outcome class 1. No feature was selected after examining outer-fold results, and the test rows were not used for imputation, encoding, scaling, or tuning.

### 2.4. Validation and uncertainty

We used five outer stratified group folds and three inner stratified group folds, with the child as the group, fixed seed 20260930, and no child shared between outer training and test sets. The primary analysis used a deterministic permutation of child-group labels before stratified allocation, yielding the corrected group-split policy documented in the executable script. The original shuffled splitter in scikit-learn 1.6.1 had a confirmed group-remapping defect; the earlier Colab output is retained in Supplementary File S2 as a historical reproduction, not combined with the primary analysis. The corrected split assignments were reproduced under scikit-learn 1.6.1 and 1.9.0. The reported probabilities are pooled out-of-fold predictions. The event fraction was the reference for average precision. A fold-specific training-prevalence model supplied a reference Brier score and log loss. Because positive outcomes were uncommon, we reported precision–recall results alongside ROC area: precision–recall changes with event prevalence [18], whereas ROC area continues to describe ranking discrimination under imbalance [19]. Neither measure by itself establishes clinical utility.

For each outer fold and each model, we generated inner cross-fitted probabilities on the outer training children at the selected regularisation value. We fitted two monotone mappings to those training-only probabilities: an intercept adjustment with slope fixed at one and logistic intercept-and-slope recalibration with a positive slope constraint. The full outer-training model's probabilities for held-out children were then transformed without using their outcomes for fitting. This evaluates the entire recalibration procedure on held-out children; pooled out-of-fold outcomes were never used to fit a calibrator. Both calibration methods were evaluated as an exploratory extension after the initial model audit. We describe calibration using mean predicted risk, observed event fraction, calibration-in-the-large, a fitted slope, and eight quantile risk bins. Brier score and log loss are overall probability scores, not standalone proof of calibration [20]. Performance and calibration were considered together [21]. For uncertainty, we resampled children 1,000 times with replacement, retaining their tooth observations, and calculated percentile intervals for each uncalibrated model, the paired spatial-minus-minimal difference, and paired within-model recalibration changes in Brier score and log loss. These intervals condition on the fitted out-of-fold probabilities; they omit the full variability of repeating development. Independent external or temporal validation, with a locked model and suitable sample size, remains necessary [22].

### 2.5. Technical audit and analysis boundary

The supplied v1.3.2 notebook was inspected for outcome timing, grouped partitioning, and test quality. Its saved `CI_SMOKE` run used 36 synthetic children and 686 synthetic tooth transitions. A separate rerun of its current source code generated the same transition and event counts but different predictive metrics from the saved notebook outputs. We retained this discrepancy in Supplementary File S2 instead of combining the two synthetic runs or using either as clinical evidence. The broader v1.9.1 flowchart was treated as a design source, and the revised detailed workflow is available as Supplementary File S1.

## 3. Results

### 3.1. Source-cohort reconstruction

All 11 prespecified count checks matched the public source: 2,504 metadata rows from 89 children included 220 composite-position rows and 2,284 single-tooth rows. Same-child, same-tooth linking generated 1,388 observed transitions, of which 1,160 connected consecutive visit indices. The latter comprised 913 `H→H`, 84 `H→C`, 163 `C→C`, and no `C→H` transitions. Thus the original onset cohort contained 997 healthy-at-*t* transitions. Removing one nonpositive follow-up interval left 996 transitions, 83 events (8.33%), 81 children, and 44 children with an event (Table 1). Positive follow-up intervals had a median of two months, interquartile range two to three months, and range two to five months.

**Table 1. Reproduction of the published-source cohort and definition of the predictive analysis set.**

| Stage | Records | Children or events | Interpretation |
|:--|--:|:--|:--|
| Public `all_metadata` worksheet | 2,504 | 89 children | Source records, before tooth filtering |
| Composite position `T5161` | 220 | — | Excluded from individual-tooth modelling |
| Single-tooth rows | 2,284 | — | Tooth-level records |
| Same-tooth observed transitions | 1,388 | — | Any successive recorded visits |
| Consecutive-index transitions | 1,160 | 913 `H→H`; 84 `H→C`; 163 `C→C`; 0 `C→H` | Exact notebook rule |
| Healthy-at-*t* onset cohort | 997 | 84 events | Reproduced source target counts |
| Primary predictive analysis | 996 | 83 events; 81 children | One zero-month interval excluded |

### 3.2. Internal predictive performance

Across the child-grouped out-of-fold predictions, the minimal clinical model achieved average precision 0.166 (95% child-bootstrap interval 0.120–0.246) and ROC area 0.686 (0.618–0.754). The clinical-spatial model achieved average precision 0.178 (0.138–0.239) and ROC area 0.737 (0.660–0.804), above the event fraction of 0.083 for average precision (Table 2; Figure 2). The spatial-minus-minimal difference was 0.012 (−0.046 to 0.058) for average precision and 0.051 (−0.009 to 0.112) for ROC area. Both intervals included zero; superiority of the spatial model was not established.

**Table 2. Patient-grouped, pooled out-of-fold performance in the real public clinical cohort (996 transitions; 83 events).**

| Model | Average precision (95% interval) | ROC area (95% interval) | Brier score (95% interval) | Log loss |
|:--|:--|:--|:--|--:|
| Minimal clinical | 0.166 (0.120–0.246) | 0.686 (0.618–0.754) | 0.0806 (0.0624–0.0996) | 0.2884 |
| Clinical plus spatial | 0.178 (0.138–0.239) | 0.737 (0.660–0.804) | 0.0754 (0.0574–0.0949) | 0.2690 |
| Fold-specific training prevalence | — | — | 0.0764 | 0.2869 |

![Figure 2. Precision–recall and ROC curves for uncalibrated models under the corrected group-split policy. Predictions were made only for each child's held-out outer fold. The horizontal precision reference is the analysis event fraction (0.083); the ROC diagonal denotes chance ranking. These are internal, not external, results.](manuscript_assets/Figure_2_discrimination_corrected_sklearn190.png){width=6.7in}

### 3.3. Calibration and model comparison

The uncalibrated minimal model had mean predicted risk 0.1182 against an observed event fraction of 0.0833, calibration-in-the-large −0.446, and slope 0.516. The spatial model's corresponding values were 0.0878, −0.066, and 0.605. Slopes below one indicate predictions that were too extreme in this internal sample. The eight-bin plot shows the uncalibrated and two training-only recalibrated versions of each model (Figure 3). The spatial model's uncalibrated Brier score, 0.0754, was close to the training-prevalence reference, 0.0764; the minimal model's score, 0.0806, was worse. The paired spatial-minus-minimal Brier difference was −0.0052 (95% bootstrap interval −0.0104 to 0.0004), including zero.

Intercept-and-slope recalibration reduced the minimal model's Brier score to 0.0745: paired difference −0.00610 (95% child-cluster interval −0.01173 to −0.00067). Its log loss changed from 0.2884 to 0.2680, but that paired interval included zero (−0.04058 to 0.00020). The spatial model's Brier score changed from 0.0754 to 0.0740: paired difference −0.00141 (−0.00308 to 0.00037), also including zero. Intercept-only updating did not provide a clear paired Brier improvement for either model. These comparisons are exploratory, conditional on the cross-fitted predictions, and do not establish clinical benefit. The recalibrated slopes remained below one (Table 3). We did not derive a treatment threshold or clinical decision rule.

**Table 3. Held-out probability assessment before and after recalibration fitted only on outer-training children. The observed event fraction was 0.0833; paired uncertainty for Brier changes is reported in the text.**

| Model and probability version | Mean risk | Calibration slope | Brier score | Log loss |
|:--|--:|--:|--:|--:|
| Minimal, uncalibrated | 0.1182 | 0.516 | 0.0806 | 0.2884 |
| Minimal, intercept only | 0.0819 | 0.613 | 0.0762 | 0.2730 |
| Minimal, intercept and slope | 0.0802 | 0.808 | 0.0745 | 0.2680 |
| Spatial, uncalibrated | 0.0878 | 0.605 | 0.0754 | 0.2690 |
| Spatial, intercept only | 0.0810 | 0.603 | 0.0753 | 0.2690 |
| Spatial, intercept and slope | 0.0827 | 0.811 | 0.0740 | 0.2638 |

![Figure 3. Descriptive calibration of uncalibrated, intercept-updated, and intercept-and-slope-updated held-out predictions for the two real-data models. Points represent eight quantile bins of predicted risk, and the diagonal denotes perfect calibration. This grouped plot has limited resolution and is not external calibration evidence.](manuscript_assets/Figure_3_calibration_corrected_sklearn190.png){width=6.7in}

### 3.4. Technical status of the other OdontoCA branches

The original notebook's saved synthetic run recorded 24 passing technical checks and two skipped real-data acceptance checks. Source inspection found a duplicate-key test that could catch its own assertion, a patient-overlap test with a tautological condition, and two hard-coded acceptance gates. The separate clinical analysis here used explicit child-disjoint and future-feature assertions. The archived synthetic and independent rerun model scores did not match despite identical 686-transition and 54-event counts. In the real-data analysis, the user's Colab result was reproduced under scikit-learn 1.6.1; the corrected group-split policy in scikit-learn 1.9.0 yielded different internal estimates. Both differences are documented in Supplementary File S2. No real Qiita microbiome model, image model, patient-linked multimodal fusion, or external clinical validation was executed for this manuscript.

## 4. Discussion

### 4.1. Principal findings and clinical research potential

This analysis advances OdontoCA from a synthetic integration demonstration to a reproducible public-cohort reconstruction and an exploratory real clinical prediction study. The 11 count checks establish that the tooth-level target was reconstructed as expected. Patient-grouped internal validation produced discrimination above chance and average precision above event prevalence for both clinical models. The stronger point estimate for the spatial model is consistent with a potential role for local oral context, but the paired uncertainty intervals include zero. Training-only intercept-and-slope recalibration reduced the minimal model's held-out Brier score; the spatial model's Brier change remained uncertain. These results warrant prospective methodological work; they do not show that spatial features or recalibration improve patient care.

### 4.2. Interpretation of performance and calibration

The event fraction was 8.33%, so average precision had a low prevalence reference. A ROC area of 0.737 describes ranking in this one cohort. The uncalibrated spatial Brier score was close to that of a simple prevalence predictor, while the recalibrated minimal Brier score was lower in this internal analysis. Its residual calibration slope of 0.808 and the limited number of children show that probability estimates still need development before individual interpretation. Fold-specific monotone updates can alter pooled rankings across folds; any resulting change in pooled discrimination should not be interpreted as new feature information. Internal out-of-fold evaluation limits some optimism but cannot replace transportability testing; PROBAST highlights concerns about participants, predictors, outcomes, and analysis [23]. Decision-curve analysis could eventually quantify net benefit at prespecified clinical thresholds [24], but doing it now would invite an unsupported treatment recommendation.

### 4.3. Relation to microbiome and spatial literature

The clinical-only design avoids attributing another group's microbiome results to OdontoCA. Recent microbiome risk modelling in a small nested case-control study [25] adds context, not a direct comparator, because case mix, follow-up, and validation differ. The source paper's tooth-resolved microbiome findings [1] and the observed structure of oral plaque communities [26] motivate an exact SampleID-linked extension. That extension should audit sequencing library quality, compositional preprocessing, patient grouping, and incremental performance against the clinical baseline. It must use matched patient, visit, and tooth records; data from unrelated image or microbiome cohorts cannot be fused to create a fictitious multimodal patient.

### 4.4. Reporting and next validation phase

The original TRIPOD statement [27], the updated TRIPOD+AI guidance [10], and practical model-development guidance [28] support full disclosure of cohort flow, candidate predictors, tuning, uncertainty, and deviations. The next phase should lock the clinical-spatial algorithm, independently reconstruct or document each derived spatial feature from measurements available at the prediction visit, and validate it in a genuinely separate clinic or later time period. A fixed prediction horizon, prespecified thresholds, subgroup checks, calibration updating, and clinical utility analysis should be planned before testing. The same evidence gate applies to proposed image and microbiome branches.

### 4.5. Limitations

The analysis uses one public cohort and a modest number of children and events, with multiple teeth per child. Follow-up varies from two to five months, and the target is the next visit rather than a fixed-time risk. Source-derived spatial fields were not reconstructed from raw examinations, and information about acquisition, missingness, and prospective availability needs author verification. The child bootstrap resampled existing out-of-fold predictions rather than refitting every nested model, so its intervals omit model-development variability. Two calibration forms were examined without an independent external dataset, and selecting one after seeing these results may overstate its future benefit. No independent outcome adjudication, external population, prospective workflow test, or net-benefit analysis was available. The saved synthetic notebook and current-code rerun yielded different metrics, and the legacy clinical Colab and corrected split policies gave different internal estimates; executable outputs and software versions must be pinned. The original work's reported diagnostic or predictive accuracy [1] is not an OdontoCA result.

## 5. Conclusion

OdontoCA reproduced the public tooth-level cohort counts and achieved exploratory child-grouped internal prediction on real clinical records. The uncalibrated clinical-spatial model had ROC area 0.737 and average precision 0.178, but its advantage over a minimal clinical model was uncertain. Training-only intercept-and-slope recalibration improved the minimal model's Brier score within this cohort; calibration remained imperfect and the spatial model's Brier change was uncertain. The technique has a path to clinical evaluation through predictor provenance, locked modelling, and independent external validation; it is not ready for patient-level decision support.

## Declarations

**Ethics approval:** No new participants were recruited. We analysed the source study's publicly released supplementary table. The authors must confirm the applicable ethics or waiver determination for this secondary analysis before submission.

**Data and code availability:** The source spreadsheet is in the [original investigators' repository](https://github.com/HuangShiLab/Single-tooth-ECC); the clinical reconstruction and analysis scripts, aggregate JSON results, figures, and source-file hash accompany this manuscript. Raw source records are not redistributed. A permanent archive identifier and the source repository's reuse terms should be confirmed before submission.

**Funding:** To be completed and verified by the authors.

**Declaration of competing interest:** To be completed and verified by each author.

**CRediT authorship contribution statement:** To be completed from the confirmed author list and actual contributions.

**Declaration of generative AI use:** OpenAI Codex assisted with code review, execution of the secondary analysis, manuscript drafting, reference checking, and diagram preparation. The named authors must inspect the data provenance, code, numerical results, citations, and final text and retain responsibility for the submitted work.

**Supplementary material:** Supplementary File S1 contains the detailed evidence-aware architecture. Supplementary File S2 documents the synthetic notebook audit, rerun discrepancy, and validation limits. The real clinical OOF analysis is separate from the source investigators' published models.

