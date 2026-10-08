# PROBAST+AI risk-of-bias and applicability assessment

**Manuscript:** *Tooth-level prediction of early-childhood caries from a public longitudinal cohort:
reproducible internal validation with patient-separated folds*

**Tool:** PROBAST+AI, updated quality, risk of bias, and applicability assessment for prediction
models using regression or artificial intelligence methods. Cited in the manuscript as reference [11].

**Assessment scope:** this is a **secondary analysis** of a released dataset. The judgements below
concern this manuscript only. They do not assess the source study, whose ethics approval, sampling
and outcome ascertainment were performed by the original investigators.

**Overall judgements**

| Domain | Risk of bias | Applicability concern |
|---|---|---|
| Participants | **High** | High |
| Predictors | **High** | High |
| Outcome | **High** | Low |
| Analysis | **High** | Low |

**Overall risk of bias: High. Overall applicability concern: High.**

All four domains carry at least one High-risk item, so the overall rating is High on the domain
summarisation alone. The two ratings that are most consequential to a reader are Participants and
Analysis. Participants is High because 89 children from a single cohort cannot represent the
intended population, and the recruitment frame is not documented in the released materials to a
standard we can verify. Analysis is High because both the outcome horizon (the next recorded visit,
varying from two to five months) and the post-hoc choice between two recalibration forms were
settled after the results were visible. Predictors is High because the spatial fields were used as
provided and their construction cannot be independently verified. Outcome is High on the horizon
grounds just described, even though the outcome definition itself is a recorded clinical field
rather than an adjudicated endpoint. The manuscript states each of these in §4.5. This assessment
exists to make that reasoning explicit and checkable rather than implicit.

---

## Domain 1 — Participants

| Question | Judgement | Basis |
|---|---|---|
| 1.1 Were eligibility criteria for the participants inappropriate? | **Low** | The cohort is the complete released table of a published study; no sampling was performed by us. All 89 children and all eligible teeth were retained. |
| 1.2 Was the study population selected in an inappropriate way? | **Low** | No selection by us. The source selection is the source study's, and is not re-assessed here. |
| 1.3 Were the participants representative of the intended population? | **High** | Unknown. The source recruitment frame is not documented in the released materials to a standard we can verify. 89 children from a single cohort cannot represent the intended target population of children at risk of early-childhood caries. |
| 1.4 Could selection into the study have led to a biased association? | **Unclear** | The direction of any selection effect cannot be estimated without the source recruitment and attrition detail. |
| 1.5 Were there too few participants? | **High** | 81 children contributing 996 tooth records, but only **83 events in 44 children**. For the spatial model with 11 candidate predictors this is far below any accepted events-per-variable heuristic. |
| 1.6 Were the participants analysed in a way that accounted for clustering? | **Low** | Child is the grouping variable throughout: grouped folds, grouped bootstrap, no child in both training and test. This is handled correctly and is a genuine strength. |

## Domain 2 — Predictors

| Question | Judgement | Basis |
|---|---|---|
| 2.1 Were the predictors defined before looking at the data? | **Low** | Both feature sets were prespecified before performance was examined (§2.3). Regularisation was selected on inner folds only. |
| 2.2 Were the predictors measured consistently for all participants? | **High** | The clinical fields are consistent source-table columns. The **spatial fields are not**: `spatial_weighted_dmfs_t`, `sum_dmfs_t`, `sum_ns_dt_t` and `sum_s_dt_t` are source-defined derived quantities whose construction and prospective availability at a clinical visit we cannot verify. The manuscript says so (§2.3, §4.5). |
| 2.3 Were the predictors assessed for all participants in the same way? | **Unclear** | Depends on the unverified spatial derivation. |
| 2.4 Could outcome information leak into predictor measurement? | **Low** | Source-defined future fields — `HostGroup`, future tooth status, time to decay, next-visit status, follow-up interval — were explicitly barred from predictors and asserted at runtime. |
| 2.5 Were predictor values assessed or analysed inappropriately? | **Low** | Imputation, encoding and scaling were all fitted on training rows only, within each fold. |
| 2.6 Were predictors selected using the outcome? | **Low** | No feature selection on outer-fold results. |

## Domain 3 — Outcome

| Question | Judgement | Basis |
|---|---|---|
| 3.1 Was the outcome measure inappropriate? | **Low** | Tooth-level caries status at the next consecutive visit, from source-table fields. Clinically meaningful. |
| 3.2 Could the outcome measurement be influenced by knowledge of the predictors? | **Low** | The outcome is a previously recorded clinical field, not re-adjudicated by us. No assessor could be influenced by our model, because we did not create an assessor. |
| 3.3 Were the outcome categories or definitions unclear? | **Low** | `H→C` versus `H→H`, both defined explicitly. |
| 3.4 Was the outcome time horizon inappropriate? | **High** | The outcome is the **next recorded visit**, with follow-up varying from two to five months, median two. This is not a fixed-horizon risk, and predictions at different intervals are not directly comparable. The manuscript discloses this explicitly (§2.2). |
| 3.5 Was the outcome assessed by a method prone to error? | **Unclear** | Diagnostic ascertainment in the source study is not documented to a level we can verify from the released table. |
| 3.6 Did the outcome definition differ between participants? | **Unclear** | Cannot be determined without the source examination protocol. |

## Domain 4 — Analysis

| Question | Judgement | Basis |
|---|---|---|
| 4.1 Were the predictor and outcome data available to the analysts at the time of prediction? | **Low** | All predictors are visit-*t* fields. Future fields were barred. |
| 4.2 Was the continuous predictor outcome handled appropriately? | **Low** | The outcome is binary; no discretisation was applied to predictors. |
| 4.3 Were all included participants and their data accounted for? | **Low** | Table 1 traces every stage from 2,504 records to the 996-transition analysis set, with the single excluded record and its reason. |
| 4.4 Could the selection of participants into the analysis set have introduced bias? | **Unclear** | One transition with a nonpositive follow-up interval was excluded. It was an event, so its removal slightly lowers the observed event fraction. The exclusion rule is defensible and disclosed, but its effect was not separately quantified. |
| 4.5 Were the missing data handled appropriately? | **Low** | Mode and median imputation fitted on training rows within each fold; no outcome values imputed. Missingness patterns are not reported in the source documentation. |
| 4.6 Were the model development and evaluation methods appropriate? | **High** | The development *methods* are appropriate, but the development *cohort* is not adequately sized. The locked primary model has 24 effective degrees of freedom against 83 outcome events, that is **3.5 events per parameter**, versus the 10 events per parameter recommended for stable estimation. This was previously judged Low on method grounds alone; it is revised to **High** because the events-per-parameter deficit is now quantified and material. Penalised logistic regression, nested child-grouped folds and child-cluster bootstrap remain appropriate choices. |
| 4.6a Is a final model available for external validation? | **Partially addressed** | A primary model is now locked as a versioned, hash-pinned artifact with a recorded source SHA-256, seed, and library versions, together with a pre-specified external validation protocol requiring 240 outcome events. This does **not** lower the domain risk: locking and pre-specification are necessary, not sufficient. The domain remains High until an independent external cohort has been scored and the pre-specified decision rule applied. |
| 4.7 Was overfitting, underfitting or optimistic bias addressed? | **Low** | Nested CV with strict child separation; the corrected split policy was adopted specifically because the prior one leaked. A sensitivity analysis across scikit-learn versions was run. |
| 4.8 Were performance metrics appropriately reported? | **Low** | Discrimination, probability scores and calibration, each with 95% child-cluster bootstrap intervals. |
| 4.9 Was uncertainty accounted for? | **High** | The bootstrap resamples existing out-of-fold predictions rather than refitting the nested models, so it **omits model-development variability** and is narrower than the true uncertainty. The manuscript states this in §4.5. It is a real limitation, not a reporting failure. |
| 4.10 Was model updating or recalibration handled appropriately? | **High** | Two recalibration forms were examined and the results interpreted **after seeing them**, with no independent dataset to confirm either. Selecting one on the strength of these results risks overstating future benefit. The manuscript says so. |
| 4.11 Were the model performance and threshold relevant to the intended use? | **Unclear** | No decision threshold was derived and no net-benefit analysis was performed. The intended use is stated as exploratory research rather than clinical decision support, which makes this acceptable — but it also means the paper does not demonstrate clinical usefulness. |

---

## What would change these judgements

**Participants (High → Moderate):** an external cohort of comparable size with documented recruitment
and attrition.

**Predictors (High → Moderate):** independent reconstruction of each derived spatial field from
measurements demonstrably available at the prediction visit, with the derivation documented. This is
the single highest-value action, because the spatial fields are what distinguishes the two models —
and the spatial model's advantage is not statistically established in any case.

**Outcome (Low → Low, but usefulness High):** a fixed prediction horizon with prespecified thresholds,
plus a decision-curve analysis at clinically meaningful thresholds.

**Analysis (High → Moderate):** full nested bootstrap that refits the entire pipeline per resample,
which would capture development variability the current intervals omit; and calibration assessed on
a genuinely separate dataset.

## Consistency with the manuscript's own claims

The manuscript's conclusion — that the technique "has a path to clinical evaluation through predictor
provenance, locked modelling, and independent external validation; it is not ready for patient-level
decision support" — is consistent with this assessment. It is also consistent with the observed
results: paired differences with intervals spanning zero, calibration slopes below one after
recalibration, and a minimal model's probability score close to that of a simple prevalence predictor.

No claim in the manuscript is contradicted by this assessment. That is the intended outcome of
running the appraisal rather than assuming the appraisal would agree.
