# Scientific Scope

## Focused question

At a specified assumed true effect and selected-claim rule, what working-scale standard error and
relative-information multiplier are required to meet one or more mandatory minimum
selected-claim probability, maximum Type S, and maximum Type M guardrails?

## Intended users and setting

The app is an educational and research-facing aid for investigators, reviewers, and methods
collaborators exploring one-parameter Wald precision assumptions. It is not a formal
study-design calculator, a diagnosis/treatment tool, a medical device, regulatory software, or
evidence that an entered effect is a clinically validated target or MCID.

## Inputs

- **Current precision:** a positive finite working-scale SE or two valid reported 95% CI limits.
  CI reconstruction determines precision only; its midpoint is not assumed true.
- **Effect measure:** supported additive or positive natural-scale ratio measure.
- **Null:** finite, and positive for ratio measures.
- **Assumed true effect:** finite, and positive for ratio measures. Every output is conditional
  on this user-specified design assumption.
- **Alpha:** strictly between zero and one.
- **Selected-claim rule:** one of the six rules released in Core 0.4.1.
- **Claim direction:** positive or negative; material for directional and threshold rules.
- **Claim threshold:** required for threshold rules and beyond the null in the selected direction.
- **Guardrails:** at least one minimum selected-claim probability in `(0,1)`, maximum Type S in
  `(0,1)`, or maximum Type M greater than `1`.
- **Sensitivity:** optional ordered finite natural-display-scale true-effect bounds and 3–101
  points. Positive bounds are required for ratio measures.
- **Current effective sample size:** optional positive finite value, accepted only when the user
  actively enables the proportional-information assumption.

These are study/scenario values and may be sensitive in context. The app neither requests
identifiers nor persists/transmits entered values.

## Outputs

Each target row reports requested value, feasibility, required working-scale SE, relative
information, approximate 95% working-scale CI width, achieved selected-claim probability, achieved
Type S, achieved Type M, current-sufficiency status, and solver note.

The joint result reports:

1. finite or no-finite-solution status;
2. the smallest required SE/largest relative-information multiplier across finite mandatory
   targets;
3. every target tying that requirement within relative multiplier tolerance `1e-8`;
4. exact multiplier `1.0` when current precision already satisfies all mandatory targets;
5. per-target preservation when any mandatory target is infeasible.

Sensitivity reports per-target and joint results at each entered assumed effect, including
undefined/no-solution gaps. It does not assign probabilities to the x-axis.

The optional sample-size output is the ceiling of current effective sample size times the joint
information multiplier. It appears only under explicit proportional-information opt-in and is
clearly labeled approximate and non-design-specific.

## Formula authority

Released
[`wald-inference` 0.4.1](https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.1)
is the sole authority for:

- natural/working-scale effect conversion;
- reported-CI reconstruction;
- selected-claim intervals and probabilities;
- repeated-study Type S and Type M;
- per-target monotonic inversion and finite bracketing;
- joint strictness, current sufficiency, binding ties, infeasibility, and sensitivity;
- approximate Wald CI width and relative-information identities.

The exact artifact provenance is in [RUNTIME_DEPENDENCIES.md](RUNTIME_DEPENDENCIES.md). The app
adapter does not copy those formulas or solvers.

## Interpretation

Selected-claim probability is the repeated-study probability that the configured rule selects a
claim, conditional on the assumed truth and design SE. Type S is the conditional probability of
the wrong sign among selected claims. Type M is the conditional exaggeration of working-scale
distance from the null among selected claims. Type S and Type M are undefined at/near the null
because direction/magnitude denominators are not meaningful there.

Ratio measures use the log working scale. Thus an entered ratio is converted to a log effect, its
SE is a log-scale SE, its approximate CI width is log-scale, and Type M refers to log-distance
from the log null.

An information multiplier is relative Fisher information under the Core model. It does not by
itself specify sample size, enrollment, events, duration, or resources.

## Limitations and non-goals

The app does not implement:

- exact trial or observational-study sample-size calculations;
- clustering, attrition, unequal allocation, event rates, censoring, covariate R², or finite
  population corrections;
- cost optimization or resource allocation;
- Bayesian assurance or posterior probability;
- automatic guardrail selection;
- clinical validation of target effects, thresholds, or MCIDs;
- observed-data compatibility curves, relative likelihood, S−2, or full Type S/M panels;
- multivariable, non-normal, small-sample, robust/sandwich, or design-specific variance models.

Wald and proportional-information approximations can be inappropriate. Users remain responsible
for selecting defensible scientific assumptions and performing a formal design analysis when
needed.
