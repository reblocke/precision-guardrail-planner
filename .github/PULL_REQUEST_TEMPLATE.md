## Scope

Describe the engineering, scientific-boundary, documentation, governance, or maintenance problem
addressed. Name `wald-inference-core` when the released numerical package owns the affected
behavior.

## Risk and release impact

Describe silent-failure risks, privacy/accessibility implications, generated-stage effects, and
whether the change requires a new release.

## Verification

List the exact commands run and their outcomes. Include skipped checks and warnings.

## Checklist

- [ ] Any scientific-method change is implemented and released in `wald-inference-core`; this
      repository adds or copies no Wald formula.
- [ ] The response remains inverse-precision-only and adds no observed compatibility, relative
      likelihood, S-2, full Type S/M curve, design-specific sample-size method, clinical threshold,
      or decision-support behavior.
- [ ] Relative information is not represented as sample size unless the existing explicit
      proportional-information opt-in is active.
- [ ] Public copy stays within validated functionality and does not imply clinical or regulatory
      readiness.
- [ ] Examples and fixtures are synthetic and contain no credentials, sensitive data, or protected
      health information.
- [ ] No backend, telemetry, persistence, cookies, hidden state, upload, or input-bearing URL was
      added.
- [ ] Generated Python under `web/assets/py/` was produced by `make stage-web`, not edited by hand.
- [ ] Every third-party GitHub Action remains pinned to a full commit SHA with a version comment.
- [ ] `uv sync --locked` and `make verify` pass.
- [ ] README, scientific scope, validation, privacy, decisions, maintenance, citation, and
      changelog were reviewed for synchronization.
