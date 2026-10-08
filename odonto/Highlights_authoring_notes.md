# Highlights — authoring notes

*Internal notes. This file is not submitted; `Highlights.md` is the file that goes
to the submission system.*

Five points for the `Journal of Dentistry` submission system, each within the 85-character limit
set in the guide for authors.

| # | Point | Characters | Limit | Status |
|---|---|---|---|---|
| 1 | Public early-childhood caries cohort reproduced exactly from its released table | 79 | 85 | PASS |
| 2 | Child-separated nested folds keep one child's teeth out of training and test sets | 81 | 85 | PASS |
| 3 | Modest discrimination above chance: ROC area 0.737, average precision 0.178 | 75 | 85 | PASS |
| 4 | Spatial context did not beat a minimal clinical baseline; intervals included zero | 81 | 85 | PASS |
| 5 | External validation is required before clinical use; no decision threshold derived | 82 | 85 | PASS |

## Why points 3 and 4 state the null findings

The paired differences between the spatial and minimal models had 95% bootstrap intervals spanning
zero for average precision, ROC area and Brier score, so the paper cannot claim that the spatial
model is superior. A highlights list that omitted this would misrepresent the study.

## Why point 5 is the safety clause

The manuscript derives no treatment threshold and performs no decision-curve analysis, because doing
so at this sample size and discrimination level would imply a clinical recommendation the data
cannot support.
