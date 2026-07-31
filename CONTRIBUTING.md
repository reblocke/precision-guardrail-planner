# Contributing

## Repository scope

This repository owns the focused, client-side inverse precision guardrail planner. Released
`wald-inference` is the sole numerical authority. Local code may validate a request, assemble the
focused response, choose a sensitivity grid, produce warnings, serialize strict browser JSON,
render or export the result, and perform the explicitly opted-in arithmetic sample-size
projection. It must not implement a Wald formula or solver, treat information as automatically
identical to sample size, or add observed compatibility, relative likelihood, S-2, full Type S/M
curves, design-specific sample-size methods, clinical thresholds, or decision support.

Use public issue forms only for nonsensitive engineering, scientific-boundary, and accessibility
reports. Report vulnerabilities through the private process in [SECURITY.md](SECURITY.md). Never
place credentials, protected health information, patient-level data, unpublished restricted data,
or other sensitive values in an issue, pull request, fixture, screenshot, URL, or workflow log.

## Change process

1. Start from the current `main` branch and make one reviewable change.
2. State assumptions, success criteria, silent-failure risks, and verification before editing.
3. Route any missing scientific formula or primitive to `wald-inference-core`, release it there,
   and adopt only its exact released artifact.
4. Keep Python under `src/` as source of truth and regenerate browser Python with `make stage-web`.
5. Keep the scientific core exact-version and checksum bound in metadata, lock, and staging
   configuration.
6. Keep third-party GitHub Actions pinned to full commit SHAs with version comments.
7. Open a pull request and let all required checks complete before merging.

Do not add a backend, telemetry, persistence, cookies, hidden state, input-bearing URLs, uploads,
or out-of-scope calculations as conveniences.

## Verification

Restore the locked environment and run the complete documented suite:

```bash
uv sync --locked
uv run playwright install chromium webkit
make verify
git diff --check
git status --short
```

Changes to the browser worker, staging, interface, or export behavior require both Chromium and
WebKit verification. Scientific changes require the frozen B06/B07 regression,
scientific-reference and property checks, and exact Core provenance checks. Document every skipped
check or warning.

## Release changes

A release change requires a reviewed pull request and an annotated version tag pointing to
the exact reviewed merge commit. The tag must equal `v` plus the authoritative project version,
and that version needs a nonempty changelog section. The tag workflow:

1. verifies the annotated remote tag object and its binding to the event commit before executing
   repository code;
2. requires the tag target to be contained in protected `main` history and match the
   project version;
3. verifies the complete suite with read-only contents permission;
4. builds and checksums all assets before creating a release;
5. transfers the complete bundle to a narrowly write-enabled publishing job;
6. requires repository release immutability;
7. creates a draft stable release using only the current version's changelog section;
8. downloads and compares every draft asset and the release body; and
9. publishes only the verified draft once as stable.

Before creating the tag, enable immutable releases. Every credentialed release command uses the
job-scoped GitHub token; no external release credential is required. After publication, the
workflow requires the release to report immutable and independently verifies it and every asset.

If a release job fails while the release remains a draft, leave the draft for inspection. If a
post-publication verification fails, preserve the published artifacts and investigate the release
state. Do not replace assets or move a tag after publication.
