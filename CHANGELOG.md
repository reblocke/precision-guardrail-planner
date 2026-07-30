# Changelog

All notable changes use a release-oriented record here. This repository follows
[Semantic Versioning](https://semver.org/).

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
