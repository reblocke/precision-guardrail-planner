# Precision Guardrail Planner

[![CI](https://github.com/reblocke/precision-guardrail-planner/actions/workflows/ci.yml/badge.svg)](https://github.com/reblocke/precision-guardrail-planner/actions/workflows/ci.yml)

[Open the client-side app](https://reblocke.github.io/precision-guardrail-planner/) ·
[browse the focused-tool catalog](https://reblocke.github.io/wald-inference-tools/)

This focused app answers one design-conditioned question:

> At an assumed true effect and selected-claim rule, what working-scale standard error and
> relative information are required to meet the chosen selected-claim probability, Type S, and
> Type M guardrails?

It is an educational and research-facing inverse-precision tool for one-parameter Wald models.
It is not a formal study-design calculator, a clinical recommendation, or evidence that a target
effect is clinically validated.

Public engineering, scientific-boundary, and accessibility reports use the scoped issue forms in
`.github/`. Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md); never put
protected health information, credentials, restricted data, or sensitive values in a public
report. Contribution and release requirements are documented in
[CONTRIBUTING.md](CONTRIBUTING.md).

> **Release metadata:** Current app version: `0.1.2`.
> Release maturity: experimental software. GitHub publication state is recorded on the versioned release page:
> <https://github.com/reblocke/precision-guardrail-planner/releases/tag/v0.1.2>.
> Cite the exact tagged software release or commit used; see [CITATION.cff](CITATION.cff).

## What it reports

For every selected mandatory guardrail, the app reports:

- finite/infeasible status;
- required working-scale standard error;
- required relative-information multiplier;
- approximate 95% working-scale CI width;
- achieved selected-claim probability, Type S, and Type M at the solved precision;
- a solver note naming current sufficiency or the reason no finite solution was found.

The joint result is the smallest finite required SE—equivalently the largest information
multiplier—across all requested targets. It identifies every constraint tying the joint
requirement within a documented relative multiplier tolerance of `1e-8`. If current precision
already meets every target, the joint multiplier is exactly `1.0`. If any mandatory target is
infeasible, the joint status is “no finite joint solution under the selected assumptions,” while
all per-target rows remain visible.

Optional sensitivity evaluates that same joint question across a user-entered plausible
true-effect range. Gaps remain gaps; they are not interpolated into solutions. The range is a
sensitivity analysis, not a probability distribution or posterior for the true effect.

## Inputs and working scales

Current precision can be entered as:

- a positive finite working-scale SE; or
- the limits of a reported 95% CI, from which the released numerical core reconstructs the
  working-scale SE.

The CI midpoint is not adopted as the true effect. Users separately enter the assumed true
effect, effect measure, null, alpha, selected-claim rule, direction, any required claim threshold,
and at least one guardrail.

Ratio measures—odds, risk, hazard, incidence-rate, and mean ratios—are converted to the log
working scale. Their SE, CI width, effect distance, and Type M calculations are therefore
log-scale quantities. Additive measures use the identity working scale.

The six released selected-claim rules are supported:

1. two-sided `p < alpha` against the null;
2. one-sided positive `p < alpha`;
3. one-sided negative `p < alpha`;
4. CI excludes the null in the selected direction;
5. estimate exceeds a claim threshold and two-sided `p < alpha`;
6. CI excludes a claim threshold.

Threshold rules require the threshold to lie beyond the null in the selected direction. An
assumed truth at/near the null leaves Type S/Type M planning undefined; a truth on the
unattainable side of a threshold may make a selected-claim probability target infeasible.

## Information is not automatically sample size

The numerical core defines relative information through:

```text
required SE = current SE / sqrt(information multiplier)
```

That multiplier is not automatically a sample-size multiplier. The app shows an approximate
sample-size projection only after the user actively enables:

> Assume information is proportional to sample size and all other design features remain
> unchanged.

With that assumption active, it reports the ceiling of current effective sample size times the
joint information multiplier. It does not model clustering, attrition, allocation, event rates,
censoring, covariate adjustment, finite populations, or any other design-specific feature.

## Numerical authority and architecture

The app does not implement a Wald solver. All effect conversion, CI reconstruction, selected
claim semantics, forward Type S/M metrics, per-target inversion, joint solution, and sensitivity
results come from the exact released
[`wald-inference` 0.4.1](https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.1)
wheel:

```text
https://github.com/reblocke/wald-inference-core/releases/download/v0.4.1/wald_inference-0.4.1-py3-none-any.whl
SHA-256 d7272023f65088729d3ff997cab7cac57b84f22ac6108244ec2170434557d99b
```

The local `precision_guardrail` package owns only strict request validation, natural/working-scale
display orchestration, response assembly, warnings, reviewer text, exports, and the explicitly
opted-in arithmetic sample-size projection.

```text
browser form
  -> dedicated Web Worker
  -> verified generated Python bundle
  -> precision_guardrail.contract.calculate_json
  -> wald_inference joint/sensitivity APIs
  -> strict JSON response
  -> textual joint/per-target results + plot + local exports
```

`src/precision_guardrail/` is the source-of-truth app package. `make stage-web` copies the locked
app and Core packages into ignored `web/assets/py/`, records file/package/bundle hashes, and
removes stale generated files. The worker verifies every staged byte before importing Python.
Never hand-edit generated stage files.

The focused response has exactly these top-level sections:

```text
meta
current_precision
assumptions
selection_rule
target_effect
per_target_results
joint_result
sensitivity_optional
sample_size_projection_optional
warnings
```

It contains no observed compatibility curve, relative-likelihood result, S−2 result, or full Type
S/M curve. Forward design metrics appear only as achieved values at solved precision and as
support for sensitivity rows.

## Exports

All exports are explicit local user actions:

- scenario/target CSV, including assumptions and one row per target plus the joint result;
- sensitivity CSV, including per-target and joint rows at every assumed effect;
- figure PNG;
- summary PNG;
- copyable grant/reviewer text and figure caption.

Undefined values are blank in CSV and `null` in JSON, never `NaN` or infinity. Plots are not the
sole carrier of a result: equivalent feasibility, target, multiplier, and binding information is
available as text and tables.

## Development and verification

```bash
uv sync --locked
uv run playwright install chromium webkit
make stage-web
make fmt-check
make lint
make test
make e2e
make e2e-webkit-smoke
make verify
uv run pytest -q tests/scientific_reference/ tests/regression/
git diff --check
git status --short
```

A new version is published only from a signed annotated tag whose commit is already contained in
protected `main`. The release workflow verifies the tag before executing repository code, reruns
the complete suite with read-only contents permission, builds a deterministic source archive,
browser-stage manifest, and checksums, and transfers them to a narrowly write-enabled publishing
job. That job requires repository release immutability through the
`RELEASE_SETTINGS_READ_TOKEN` Actions secret, creates one draft stable release, re-downloads and
compares the exact release body and every asset, and publishes only the verified draft.
Credentialed commands use an exact checksummed GitHub CLI. Release notes contain only the tagged
version's nonempty changelog section.

The suite covers the frozen integrated B06/B07 baseline values, all six claim rules, current
sufficiency, strictness/ties, infeasibility, near-null behavior, threshold unattainability,
forward-metric attainment, information and CI-width identities, sensitivity monotonicity where
expected, ratio conversion, direct-SE/CI equivalence, the Core information cap, strict JSON,
sample-size opt-in/rounding, deterministic staging, Chromium, WebKit, privacy, accessibility, and
exports.

See [scientific scope](docs/SCIENTIFIC_SCOPE.md),
[validation](docs/VALIDATION.md), [decisions](docs/DECISIONS.md),
[runtime provenance](docs/RUNTIME_DEPENDENCIES.md), and
[migration provenance](docs/MIGRATION_PROVENANCE.md).

## Related Wald tools

- Choose a tool: [Wald inference tools catalog](https://reblocke.github.io/wald-inference-tools/).
- Closest adjacent tool:
  [Type S/M Calibrator](https://reblocke.github.io/type-s-m-calibrator/).
- [Integrated workbench](https://reblocke.github.io/conf_curve_likelihood/).
- [Precision Guardrail Planner repository](https://github.com/reblocke/precision-guardrail-planner).
- Numerical core:
  [wald-inference Core v0.4.1](https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.1).
- Privacy: calculations stay in the browser and entered values are not persisted or transmitted;
  see the [privacy note](docs/PRIVACY.md).

## Privacy

The app is static and client-side. It has no backend, telemetry, analytics, browser storage,
cookies, upload, input-bearing URL, or application logging. Inputs exist only in page and worker
memory. Static CDN requests do not include entered values. CSV/PNG files are created only after
an explicit local download action. See [docs/PRIVACY.md](docs/PRIVACY.md).

## License and citation

Code is MIT licensed. Copyright (c) 2026 Brian Locke. Cite the exact release or commit used;
machine-readable metadata is in [CITATION.cff](CITATION.cff).
