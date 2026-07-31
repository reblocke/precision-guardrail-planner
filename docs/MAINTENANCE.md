# Maintenance

## Status and ownership

Status: experimental, actively maintained software.

Current version: 0.1.2.

Maintainer: Brian Locke (`@reblocke`). Use the scoped repository issue forms and reviewed pull
requests for nonsensitive public coordination. Report vulnerabilities and privacy defects
privately through [SECURITY.md](../SECURITY.md). Scientific-meaning, Core-adoption, accessibility,
and release changes require explicit review.

## Dependency updates

Review Pyodide, Plotly, Python, uv, Ruff, pytest, Hypothesis, Playwright, GitHub Actions, and Core
updates deliberately. Dependabot groups weekly `uv` and GitHub Actions updates for review; it does
not authorize automatic merging. Keep each third-party Action pinned to a full commit SHA with its
reviewed version in a comment. For a Core update:

1. review upstream release notes/API/scientific changes and tag target;
2. update the exact wheel URL and SHA-256 in `pyproject.toml` and `browser-stage.toml`;
3. regenerate and inspect `uv.lock`;
4. rerun B06/B07 regression parity, all-rule tests, strict JSON, staging, Chromium, and WebKit;
5. update docs, UI metadata, and changelog in the same review.

Do not adopt an unreleased sibling checkout or hand-copy a missing Core primitive.

## Release

Use a reviewed pull request and expected-head merge. Confirm local full verification, CI, and
hosted Pages, then create an annotated semantic-version tag on the exact merge commit.

The release workflow verifies the annotated remote tag object and its binding to the event commit
before it executes repository code. It requires that commit to be contained in protected `main`,
parses the project version
with isolated Python, reruns the complete suite under read-only contents permission, disables the
shared dependency cache for the release build, and creates the deterministic source archive,
browser-stage manifest, and SHA-256 checksums before a release exists. A separate job with narrowly
scoped contents-write permission uses an exact checksummed GitHub CLI and the job-scoped GitHub
token to create a draft stable release with every asset, re-downloads and compares the draft assets
and release body, publishes only the verified draft, then requires the published release to report
immutable and independently verifies every asset. The tag must equal `v` plus the authoritative
project version, and the public release body contains only that version's nonempty changelog
section.

If the workflow fails while the release remains a draft, retain the draft for inspection. If a
post-publication verification fails, preserve the published artifacts and investigate the release
state. Repair the workflow and create a new tag only after the failure is understood; never move a
published tag or replace a published asset. Publish once into the intended stable lifecycle state
only after hosted Pages and portfolio-level validation are complete.

Repository settings must retain read-only default workflow permissions, protect `main` and `v*`
tags, enable private vulnerability reporting and Dependabot security updates, and enable immutable
releases before the next tag is created. Release automation requires no external release
credential; all credentialed GitHub commands use the job-scoped GitHub token. Because the workflow
verifies immutability after publication rather than querying the setting beforehand, confirm this
repository setting before creating the tag.

## Deprecation

Deprecations will be announced in the README, hosted app, changelog, release notes, and tool
catalog with a successor link and migration interval. Existing release tags remain immutable.
The hosted URL will not be silently redirected or removed.
