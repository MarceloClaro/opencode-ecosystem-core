# Technical feasibility of a tooth-level early-childhood caries prediction pipeline: a synthetic-data study

## Abstract

**Objectives:** To assess the technical execution and reporting boundaries of a tooth-level pipeline combining a probabilistic cellular-automaton rule with clinical-spatial and microbiome prediction models for early-childhood caries.

**Methods:** We audited the saved outputs and source code of OdontoCA v1.3.2 in its executed `CI_SMOKE` profile. A fixed-seed generator created three visits for 36 synthetic children. The binary outcome was progression from a healthy tooth at time *t* to caries at the next consecutive visit. A smoothed cellular-automaton rule and clinical, microbiome, and combined logistic models were assessed using child-grouped out-of-fold predictions. The logistic models used three outer and two inner cross-validation folds; hyperparameters were selected by average precision. The supplied v1.9.1 diagram was treated as proposed architecture only.

**Results:** There were 686 synthetic tooth transitions and 54 events (prevalence 7.87%). Average precision was 0.0817 for the cellular-automaton rule, 0.1054 for the clinical model, 0.0955 for the microbiome model, and 0.0748 for the combined model. Corresponding ROC areas were 0.5345, 0.5906, 0.5326, and 0.4804. Twenty-four technical tests passed and two real-data acceptance tests were skipped. Clinical cohort reproduction, real microbiome alignment, image analysis, and external validation were not performed.

**Conclusions:** The saved run demonstrates execution of a synthetic technical workflow. Its discrimination was weak, and the combined model performed below chance on pooled ROC area. These findings do not establish clinical predictive accuracy or readiness for patient use.

**Keywords:** dental caries; preschool child; oral microbiome; cellular automata; machine learning; cross-validation; synthetic data.

## 1. Introduction

Early-childhood caries develops across teeth and visits in a changing oral environment. Tooth-resolved longitudinal microbiome analysis offers one way to study spatial and temporal variation [1], while clinical and behavioural factors remain relevant predictors of subsequent caries [2]. Longitudinal work has associated early oral microbial communities with later disease [3,4], and small prospective microbiome prediction studies illustrate both the opportunity and the uncertainty of this approach [5]. Mechanistic biofilm simulations and cellular automata provide computational precedents [6,7], but neither constitutes validation of a patient-level risk tool.

The OdontoCA project proposes a pipeline that links tooth-level transitions, anatomical neighbourhoods, clinical variables, microbial abundance profiles, and eventually dental images. A central risk in evaluating such a pipeline is to confuse successful software execution with patient-level predictive validity. Synthetic records can test data flow, probability orientation, cross-validation, and metric calculation; they cannot estimate performance in the population from which real clinical decisions would be made. Repeated observations from the same child also require grouped validation, and model selection should be separated from performance estimation [8,9].

The purpose of this study was therefore narrow: to describe and critically assess the executed synthetic OdontoCA v1.3.2 workflow, report its saved metrics without clinical interpretation, and identify which parts of the broader v1.9.1 architecture remain untested. The study was not designed as a review, a prospective clinical study, an image-diagnostic accuracy study, or an external validation.

## 2. Materials and methods

### 2.1. Study design and evidence boundary

We examined the user-supplied OdontoCA v1.3.2 notebook, including its code, saved outputs, figures, and validation report. The linked Colab copy and local copy contain the same cell sources and outputs; the Colab copy retains execution counters. The active configuration was `PROFILE = "CI_SMOKE"`, seed 20260906, with network access and real clinical, microbiome, and image loading disabled. Consequently, every performance estimate reported here comes from a deterministic synthetic simulation. We did not independently rerun the full notebook or inspect the results bundle named in its report.

The separate OdontoCA v1.9.1 Mermaid diagram specifies a proposed 16-layer architecture with real-data adapters, visual quality control, duplicate checks, patient-linked fusion, acceptance gates, and output manifests. It contains neither experimental output nor a test log. We used it to contextualise the research roadmap, not to supply results. Figure 1 distinguishes the executed path from branches that remained unrun.

![Figure 1. Executed synthetic v1.3.2 workflow (solid blue) and unrun validation branches (dashed ochre). The diagram was prepared from the audited notebook; it is an explanatory schematic, not evidence that the dashed branches were executed.](manuscript_assets/Figure_1_pipeline.png){width=5.8in}

### 2.2. Synthetic longitudinal data and target

The notebook generated records for 36 synthetic children at three timepoints, using ten upper primary-tooth positions. Teeth began in a healthy state (`H`); progression to caries (`C`) was simulated with a fixed random seed. The transition probability depended on a child-specific baseline risk, molar status, and the number of neighbouring carious teeth, with an upper cap of 0.55. These rules are simulation assumptions rather than estimated biological effects.

For each child and tooth, the code paired consecutive timepoints and retained transitions with a one-step timepoint difference. The analysis cohort consisted of teeth in state `H` at time *t*. The positive outcome was `H→C` at *t*+1; `H→H` was negative. Features described the tooth and its clinical-spatial context at *t*. Fields containing future status, time to decay, and the source-defined host group were excluded from model predictors. The generator also created 24 synthetic amplicon sequence variant (ASV) count features per baseline sample through gamma/Poisson draws with programmed dependence on simulated risk factors. These ASVs are not observed taxa or measured microbial profiles.

### 2.3. Prediction rules and model fitting

The cellular-automaton comparator estimated event probabilities from training data, grouping by tooth niche, child-level caries status, and the count of carious neighbouring teeth. Hierarchical fallback tables and prior-strength smoothing limited sparsity. Its predictions were generated out of fold with child-disjoint splits.

Three logistic-regression pipelines were compared: (i) clinical-spatial predictors with categorical imputation and one-hot encoding plus median imputation and scaling of numeric variables; (ii) synthetic ASV counts with training-fold prevalence/abundance selection, a 0.5 pseudocount, centred log-ratio transformation, scaling, and logistic regression; and (iii) the clinical features combined with a microbial branch that also used principal-component analysis retaining 95% of variance. In the nested search, the microbiome transformations were fitted inside the training portion of each fold. The code selected the probability column corresponding to outcome label 1 from the fitted estimator's class order.

### 2.4. Validation and analysis

The synthetic smoke profile requested three outer and two inner stratified group folds, with each child restricted to one side of a split. Logistic-regression regularisation was tuned in the inner folds using average precision. Pooled out-of-fold predictions were summarised by average precision (PR-AUC), area under the receiver-operating-characteristic curve (ROC-AUC), Brier score, and log loss. A child-level bootstrap of 200 resamples was requested for uncertainty and model differences, but the saved validation report did not provide confidence intervals; none are inferred here.

Average precision was interpreted alongside the observed event fraction of 54/686. A below-chance audit checked whether pooled ROC-AUC fell below 0.5 or PR-AUC below the event fraction. The code explicitly prohibited re-labelling `1 − ROC-AUC` as performance after inspecting results. Technical checks were reported separately from model performance. The notebook's self-labelled TRIPOD+AI and PROBAST+AI rows were treated as internal checklists rather than independent assessments under those reporting and risk-of-bias frameworks [10,11].

### 2.5. Images and the proposed extended architecture

The v1.3.2 notebook defines paths for a dental-image inventory, optional visual model training, optional tooth segmentation, and an experimental FHIR `RiskAssessment` export. The executed profile did not activate image inventory or training. The v1.9.1 diagram extends these concepts to four visual domains, annotation adapters, image-quality review, cross-split duplicate checks, controlled tuning, tooth assignment, and multimodal fusion restricted to the same patient, visit, and tooth. These are design specifications, not methods that produced the numerical results in this paper. The complete supplied diagram is preserved as Supplementary File S1.

## 3. Results

### 3.1. Analysis set and source status

The synthetic generator yielded 686 eligible healthy-to-next-visit tooth transitions from 36 children, of which 54 progressed to the simulated caries state. The event fraction was 7.87%. The clinical and synthetic-microbiome models used the same transition-level target. Table 1 makes the provenance of each study component explicit.

**Table 1. Status of data sources and modules in the saved OdontoCA v1.3.2 run.**

| Component | Status in `CI_SMOKE` | Interpretation |
|:--|:--|:--|
| Synthetic clinical-spatial transitions | Executed | Software test records; no patients enrolled |
| Synthetic 24-ASV count matrix | Executed | Generated counts; no laboratory measurements |
| Real `Table_S1` cohort reconstruction | Not run | Hard-coded expected counts were not reproduced |
| Qiita 14341 microbiome alignment | Not run | No real SampleID-to-BIOM audit |
| Image benchmark inventory and visual model | Not run / not requested | No image performance estimate |
| External clinical validation | Not performed | Generalisability cannot be assessed |
| v1.9.1 16-layer diagram | Design only | No execution evidence in the supplied diagram |

### 3.2. Out-of-fold synthetic performance

Table 2 reports the saved metrics at the precision present in the notebook. The clinical-spatial logistic model had the highest average precision and ROC-AUC among the four synthetic comparisons, although both were modest. The combined model had ROC-AUC 0.4804 and average precision 0.0748, below the corresponding chance-reference values of 0.5 and 0.0787. This was reported without post hoc outcome inversion. Figures 2 and 3 reproduce the notebook's synthetic curves; the cellular-automaton rule was not plotted in those saved figures.

**Table 2. Pooled out-of-fold performance for synthetic tooth transitions only (n = 686; 54 events).**

| Model | PR-AUC | ROC-AUC | Brier score | Log loss |
|:--|--:|--:|--:|--:|
| Probabilistic cellular-automaton rule | 0.081743 | 0.534546 | 0.073223 | 0.278713 |
| Clinical-spatial logistic regression | 0.105386 | 0.590571 | 0.073304 | 0.279610 |
| Synthetic microbiome CLR logistic regression | 0.095530 | 0.532613 | 0.131119 | 0.431432 |
| Clinical plus synthetic microbiome | 0.074825 | 0.480397 | 0.081224 | 0.325447 |

![Figure 2. Precision-recall curves from synthetic out-of-fold predictions. The dashed horizontal line is the synthetic event fraction (0.0787). The cellular-automaton rule was not included in the saved plot. These curves have no clinical interpretation.](manuscript_assets/Figure_2A_synthetic_PR.png){width=5.6in}

![Figure 3. Receiver-operating-characteristic curves from synthetic out-of-fold predictions. The dashed diagonal indicates chance ranking. The cellular-automaton rule was not included in the saved plot.](manuscript_assets/Figure_2B_synthetic_ROC.png){width=5.6in}

### 3.3. Technical checks and unavailable results

The notebook's technical-test table recorded 24 passes, two skips, and no failures. The two skipped acceptance tests required real clinical and real microbiome data. Source inspection identified limitations in the evidential strength of some passing checks: one duplicate-key test could catch its own assertion failure, one patient-overlap test used a tautological condition, and two acceptance gates were set to `True` by implementation rather than measured through a separate audit. The outer cross-validation loop itself contains an assertion of child-disjoint train and test groups. These observations qualify the test-count summary; they do not imply that real-data validation was performed.

The saved report explicitly states `NOT_RUN` for real clinical reconstruction, Qiita alignment, and image benchmark audit; visual training was `NOT_REQUESTED` and external clinical validation `NOT_PERFORMED`. Expected real-dataset counts in the code and the v1.9.1 diagram are targets for future reproduction, not observed results of this run. Brier score and log loss were reported, but calibration plots, calibration slope, and calibration intercept were not provided. Accordingly, the internal checklist's `calibration = PASS` entry cannot establish calibration quality.

## 4. Discussion

The principal result is an evidence boundary rather than a claim of clinical accuracy. A complete synthetic path generated tooth transitions, fitted multiple models, produced child-grouped out-of-fold predictions, and surfaced a below-chance combined model without reversing its label. This is useful for testing a research workflow. The synthetic estimates do not indicate that any model predicts real early-childhood caries or that microbiome data improve care. In this run, adding synthetic microbiome counts worsened pooled discrimination relative to the clinical-spatial model.

The distinction matters because the synthetic microbiome generator intentionally encoded selected clinical-risk features into some ASV counts. Even under that favourable constructed relationship, the combined pipeline did not outperform the clinical comparator. This observation should prompt investigation of fold-level stability, class imbalance, feature selection, model specification, and simulation design before real-data analysis. It cannot establish a biological conclusion about oral taxa. The number of children is small, and all outcomes arise from programmed transition probabilities.

The planned real-data pathway has merit as a research protocol: it separates longitudinal tooth transitions from image data, restricts predictors to time *t*, fits microbiome transformations within cross-validation, and blocks fusion of unmatched cohorts. Its extension in the v1.9.1 diagram adds annotation conversion, visual quality control, duplicate checks, and a requirement for legitimate independent test data. These safeguards are commitments in an architecture document. They must be supported by execution logs and independently inspectable outputs before appearing as accomplished methods or results.

The study has several limitations. We assessed saved notebook outputs rather than completing an independent rerun of every cell. No real clinical records, ASV matrix, or images were supplied for verification. The results bundle named by the notebook was unavailable in the reviewed materials. The technical-test count overstates the strength of some individual checks, and the internal reporting checklists are not external TRIPOD+AI or PROBAST+AI reviews [10,11]. No patient-level confidence intervals, external-site evaluation, calibration curve, clinical utility analysis, or threshold-specific decision analysis was available. The diagram's 46 SDD requirements and 58 TDD tests also cannot be counted as executed v1.3.2 results.

A defensible next study would first obtain the licensed/authorised clinical table and microbial counts, reproduce tooth-level transitions with a provenance manifest, repair the weak tests, and prespecify child-level partitions. It should report full discrimination and calibration with uncertainty, then evaluate an independent clinical cohort. Image accuracy and patient-linked multimodal fusion require their own ground truth and matching keys. Until those steps are completed, OdontoCA is a research pipeline rather than a clinical decision-support system.

## 5. Conclusion

OdontoCA v1.3.2 executed a synthetic technical smoke test for tooth-level caries progression modelling. In that run, 54 of 686 synthetic transitions were events, and the combined model performed below chance on pooled ROC-AUC. The broader v1.9.1 architecture is a proposed protocol without accompanying execution evidence. Neither artifact demonstrates clinical predictive validity; real-data reproduction and independent validation are prerequisites for reporting clinical performance.

## Declarations

**Ethics approval:** The reported analysis used programmatically generated synthetic records only; no patient records or human participants were analysed in this run. Requirements for future real-data work must be assessed separately.

**Data and code availability:** The source notebook and saved synthetic outputs are in the [linked Colab file](https://colab.research.google.com/drive/1JNkdMWv2kE_QMoEf0exn21RMnABCfe0Q). Public access and anonymous-review access have not been established. A permanent archive identifier and the cited result bundle require confirmation before submission. No real patient-level data were analysed for this manuscript.

**Funding:** To be completed and verified by the authors before submission.

**Declaration of competing interest:** To be completed and verified by each author before submission.

**CRediT authorship contribution statement:** To be completed from the confirmed author list and actual contributions before submission.

**Declaration of generative AI use:** OpenAI Codex assisted with source auditing, manuscript drafting, reference organisation, and preparation of the explanatory Figure 1. The scientific claims, references, image rights, and final text require review and approval by the named authors before submission. Figures 2 and 3 were extracted from the notebook's saved outputs.

**Supplementary material:** Supplementary File S1 contains the user-supplied OdontoCA v1.9.1 Mermaid architecture. It is a design document and does not report executed results.

## References

1. Yang F, Teng F, Zhang Y, Sun Y, Xu J, Huang S. Single-tooth resolved, whole-mouth prediction of early childhood caries via spatiotemporal variations of plaque microbiota. *Cell Host Microbe*. 2025;33(6):1019–1032.e6. doi:[10.1016/j.chom.2025.05.006](https://doi.org/10.1016/j.chom.2025.05.006).
2. Toledo Reyes L, Knorst JK, Ortiz FR, et al. Early childhood predictors for dental caries: a machine learning approach. *J Dent Res*. 2023;102(9):999–1006. doi:[10.1177/00220345231170535](https://doi.org/10.1177/00220345231170535).
3. Dashper SG, Mitchell HL, Lê Cao KA, et al. Temporal development of the oral microbiome and prediction of early childhood caries. *Sci Rep*. 2019;9:19732. doi:[10.1038/s41598-019-56233-0](https://doi.org/10.1038/s41598-019-56233-0).
4. Blostein F, Bhaumik D, Davis E, et al. Evaluating the ecological hypothesis: early life salivary microbiome assembly predicts dental caries in a longitudinal case-control study. *Microbiome*. 2022;10:240. doi:[10.1186/s40168-022-01442-5](https://doi.org/10.1186/s40168-022-01442-5).
5. Raksakmanut R, Thanyasrisung P, Sritangsirikul S, et al. Prediction of future caries in 1-year-old children via the salivary microbiome. *J Dent Res*. 2023;102(6):626–635. doi:[10.1177/00220345231152802](https://doi.org/10.1177/00220345231152802).
6. Head D, Devine DA, Marsh PD. In silico modelling to differentiate the contribution of sugar frequency versus total amount in driving biofilm dysbiosis in dental caries. *Sci Rep*. 2017;7:17413. doi:[10.1038/s41598-017-17660-z](https://doi.org/10.1038/s41598-017-17660-z).
7. Martin B, Tamanai-Shacoori Z, Bronsard J, et al. A new mathematical model of bacterial interactions in two-species oral biofilms. *PLoS ONE*. 2017;12(3):e0173153. doi:[10.1371/journal.pone.0173153](https://doi.org/10.1371/journal.pone.0173153).
8. Varma S, Simon R. Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics*. 2006;7:91. doi:[10.1186/1471-2105-7-91](https://doi.org/10.1186/1471-2105-7-91).
9. Rosenblatt M, Tejavibulya L, Jiang R, Noble S, Scheinost D. Data leakage inflates prediction performance in connectome-based machine learning models. *Nat Commun*. 2024;15:1829. doi:[10.1038/s41467-024-46150-w](https://doi.org/10.1038/s41467-024-46150-w).
10. Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. doi:[10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378).
11. Moons KGM, Damen JAA, Kaul T, et al. PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool for prediction models using regression or artificial intelligence methods. *BMJ*. 2025;388:e082505. doi:[10.1136/bmj-2024-082505](https://doi.org/10.1136/bmj-2024-082505).
