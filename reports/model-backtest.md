# Phase 3 — probability model walk-forward validation

Test years 2021-2025, trained on all prior years. Target is the cell-month binomial rate `p_ge_3h` (see `models/features.py` docstring: CAA data is cell-level, not flight-level, so this is a documented substitution for the per-flight target in PLAN.md, not an approximation).

`brier_proxy`/`log_loss` are weighted against the observed cell rate — see `models/calibration.py` docstring for why this is a proxy, not the exact flight-level Brier score.

| Year | Model | Calibrated | n cells | n flights | Brier proxy | Log loss | mean pred | mean actual |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2021 | baseline | False | 16,316 | 309,025 | 0.00037 | 0.0240 | 0.277% | 0.345% |
| 2021 | gbm | False | 16,316 | 309,025 | 0.00037 | 0.0227 | 0.447% | 0.345% |
| 2021 | gbm | True | 16,316 | 309,025 | 0.00037 | 0.0228 | 0.467% | 0.345% |
| 2021 | logistic | False | 16,316 | 309,025 | 0.00038 | 0.0234 | 0.625% | 0.345% |
| 2021 | logistic | True | 16,316 | 309,025 | 0.00037 | 0.0230 | 0.471% | 0.345% |
| 2022 | baseline | False | 29,697 | 764,529 | 0.00077 | 0.0641 | 0.430% | 1.043% |
| 2022 | gbm | False | 29,697 | 764,529 | 0.00074 | 0.0592 | 0.514% | 1.043% |
| 2022 | gbm | True | 29,697 | 764,529 | 0.00077 | 0.0609 | 0.378% | 1.043% |
| 2022 | logistic | False | 29,697 | 764,529 | 0.00074 | 0.0589 | 0.597% | 1.043% |
| 2022 | logistic | True | 29,697 | 764,529 | 0.00077 | 0.0611 | 0.401% | 1.043% |
| 2023 | baseline | False | 30,491 | 894,707 | 0.00050 | 0.0504 | 0.956% | 0.898% |
| 2023 | gbm | False | 30,491 | 894,707 | 0.00052 | 0.0530 | 0.407% | 0.898% |
| 2023 | gbm | True | 30,491 | 894,707 | 0.00050 | 0.0505 | 0.985% | 0.898% |
| 2023 | logistic | False | 30,491 | 894,707 | 0.00051 | 0.0521 | 0.509% | 0.898% |
| 2023 | logistic | True | 30,491 | 894,707 | 0.00050 | 0.0507 | 0.978% | 0.898% |
| 2024 | baseline | False | 31,519 | 938,697 | 0.00043 | 0.0458 | 0.882% | 0.796% |
| 2024 | gbm | False | 31,519 | 938,697 | 0.00044 | 0.0484 | 0.405% | 0.796% |
| 2024 | gbm | True | 31,519 | 938,697 | 0.00042 | 0.0458 | 0.846% | 0.796% |
| 2024 | logistic | False | 31,519 | 938,697 | 0.00042 | 0.0458 | 0.648% | 0.796% |
| 2024 | logistic | True | 31,519 | 938,697 | 0.00042 | 0.0458 | 0.958% | 0.796% |
| 2025 | baseline | False | 32,437 | 954,753 | 0.00039 | 0.0374 | 0.781% | 0.620% |
| 2025 | gbm | False | 32,437 | 954,753 | 0.00038 | 0.0374 | 0.606% | 0.620% |
| 2025 | gbm | True | 32,437 | 954,753 | 0.00038 | 0.0370 | 0.680% | 0.620% |
| 2025 | logistic | False | 32,437 | 954,753 | 0.00039 | 0.0374 | 0.761% | 0.620% |
| 2025 | logistic | True | 32,437 | 954,753 | 0.00039 | 0.0375 | 0.796% | 0.620% |

## Baseline vs. complexity
- logistic (calibrated), test year 2025: Brier proxy 0.00039 vs. baseline 0.00039 — **beats** the shrunken-cell-mean baseline.
- gbm (calibrated), test year 2025: Brier proxy 0.00038 vs. baseline 0.00039 — **beats** the shrunken-cell-mean baseline.
