# Changelog

All notable changes use a release-oriented record here. This repository follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.4] - 2026-07-31

- Update the locked test/build toolchain to pytest 9.1.1 and setuptools 83.0.0.
- Update the reviewed, full-SHA GitHub Actions pins used by CI, Pages, and release workflows.
- Publish the maintenance-only app state as an immutable patch release so the hosted Pages commit,
  package metadata, citation, and release artifacts identify the same source commit.
- Preserve the exact Core v0.4.2 pin, all inverse-precision and joint-solution semantics, focused
  response/export contracts, browser behavior, negative scope, and client-side privacy boundary.

## [0.1.3] - 2026-07-31

- Harden CI, Pages, and release automation with least-privilege permissions, full-SHA Action pins,
  checkout credential isolation, and disabled dependency caching for release artifacts.
- Require an annotated tag whose exact remote tag object is bound to the event commit on protected
  `main` and the authoritative project version before repository code is executed, without making
  GitHub signature verification a release gate.
- Use only the job-scoped GitHub token for remote tag and release operations; remove the external
  settings credential and prepublication immutable-settings query while retaining exact draft
  body/asset comparison and post-publication immutable-release and asset verification.
- Add grouped weekly Dependabot proposals, private vulnerability reporting guidance, contribution
  policy, scoped issue forms, a pull-request checklist, and repository-policy regressions.
- Adopt the exact immutable `wald-inference` v0.4.2 wheel and checksum in package metadata, the
  lockfile, browser staging, runtime copy, and validation contracts. Core v0.4.2 changes governance
  and release controls only; every inverse-precision and browser contract, the app's negative scope,
  and the client-side privacy boundary remain unchanged.

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

[Unreleased]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/reblocke/precision-guardrail-planner/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/reblocke/precision-guardrail-planner/releases/tag/v0.1.0
