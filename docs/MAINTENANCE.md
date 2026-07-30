# Maintenance

## Status and ownership

Status: active experimental research software, version 0.1.2.

Maintainer: Brian Locke (`@reblocke`). Use repository issues and reviewed pull requests for public
coordination. Scientific-meaning, Core-adoption, privacy, accessibility, and release changes
require explicit review.

## Dependency updates

Review Pyodide, Plotly, Python, uv, Ruff, pytest, Hypothesis, Playwright, GitHub Actions, and Core
updates deliberately. For a Core update:

1. review upstream release notes/API/scientific changes and tag target;
2. update the exact wheel URL and SHA-256 in `pyproject.toml` and `browser-stage.toml`;
3. regenerate and inspect `uv.lock`;
4. rerun B06/B07 regression parity, all-rule tests, strict JSON, staging, Chromium, and WebKit;
5. update docs, UI metadata, and changelog in the same review.

Do not adopt an unreleased sibling checkout or hand-copy a missing Core primitive.

## Release

Use a reviewed pull request and expected-head merge. Confirm local full verification and CI, then
create an annotated semantic-version tag on the exact merge commit. The release workflow reruns
the full suite and publishes a prerelease with deterministic source archive, browser-stage
manifest, and SHA-256 checksums. Verify all assets and hosted Pages before reporting completion.

Promote stability only after portfolio-level independent validation.

## Deprecation

Deprecations will be announced in the README, hosted app, changelog, release notes, and tool
catalog with a successor link and migration interval. Existing release tags remain immutable.
The hosted URL will not be silently redirected or removed.
