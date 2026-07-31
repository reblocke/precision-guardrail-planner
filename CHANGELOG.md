# Changelog

All notable changes use a release-oriented record here. This repository follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

- Harden CI, Pages, and release automation with least-privilege permissions, full-SHA Action pins,
  checkout credential isolation, and disabled dependency caching for release artifacts.
- Require a GitHub-verified signed annotated tag on protected `main`, bound to the event commit and
  authoritative project version before repository code is executed.
- Install an exact checksummed GitHub CLI, require repository immutability through a dedicated
  administration-read secret, and verify the complete draft body and asset set before one-time
  stable publication.
- Add grouped weekly Dependabot proposals, private vulnerability reporting guidance, contribution
  policy, scoped issue forms, a pull-request checklist, and repository-policy regressions.
- Preserve version `0.1.2`, the exact `wald-inference` v0.4.1 wheel and checksum, every inverse
  precision and browser contract, the app's negative scope, and the client-side privacy boundary.

## [0.1.2] - 2026-07-30

- Add explicit README metadata for the current app version, experimental maturity, exact versioned
  release URL, GitHub publication state, and software citation guidance.
- Add a repository-policy regression that keeps README release/version/citation metadata aligned
  with package and `CITATION.cff` versions.
- Preserve all scientific, inverse-planning, browser UI, privacy, and export behavior; Core remains
  pinned to `wald-inference` v0.4.1.

## [0.1.1] - 2026-07-30

- Publish the navigation and Core-marker Pages source as a checksum-addressed patch release so the
  deployed app, annotated tag, and release artifacts resolve to the same commit.
- Adopt the exact `wald-inference` v0.4.1 release, which corrects non-monotone threshold precision
  bracketing, exact pairwise support ratios, and strict ratio-scale underflow validation.
- Preserve the app's inverse-planning contracts and exports without adding or duplicating any
  numerical formula locally.

## [0.1.0] - 2026-07-30

- Added focused inverse precision planning for selected-claim probability, Type S, and Type M
  guardrails under all six released one-parameter Wald selected-claim rules.
- Added per-target feasibility/results plus the Core-defined strictest joint solution, binding
  ties, exact current-sufficient multiplier `1.0`, and explicit no-finite-solution status.
- Added optional true-effect sensitivity with feasibility gaps and an optional, actively enabled
  proportional-information sample-size projection.
- Added strict JSON, scenario/target and sensitivity CSVs, figure/summary PNGs, and copyable
  grant/reviewer text.
- Pinned `wald-inference` 0.4.0 to its released wheel URL and SHA-256 checksum; the app contains no
  duplicate numerical solver.
- Added B06/B07 migration regression tests, scientific invariants, all-rule coverage, Chromium and
  WebKit checks, privacy/accessibility checks, and deterministic browser staging.

[Unreleased]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/reblocke/precision-guardrail-planner/releases/tag/v0.1.0
