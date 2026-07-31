# Decisions

## 2026-07-31 — Core 0.4.2 replaces Core 0.4.1 without numerical change

The app pins the immutable official Core 0.4.2 wheel at
`https://github.com/reblocke/wald-inference-core/releases/download/v0.4.2/wald_inference-0.4.2-py3-none-any.whl`
with SHA-256 `225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349`.
The annotated upstream tag targets `8afd0a463cc1d2586b8ce5cf92f40900647c3190`. Package metadata,
the lockfile, browser staging, public runtime markers, and validation contracts use that same
artifact.

Core 0.4.2 changes governance and release controls only and explicitly preserves every numerical
formula, public API, tolerance, dependency resolution, and frozen baseline value. The app therefore
adopts the new immutable release without changing local orchestration, solver or joint semantics,
scientific interpretation, the focused response, browser behavior, or exports. The historical Core
0.4.1 adoption decision remains below as the record for the numerical repairs first consumed here.

## 2026-07-31 — Release automation uses only the job-scoped GitHub token

This decision supersedes only the 2026-07-30 requirements for a GitHub-verified tag signature and
a dedicated repository-administration-read release credential. The earlier decision is preserved
below as the historical policy record.

Future releases still require an annotated semantic-version tag. Before repository code executes,
the workflow confirms the local annotated tag, remote tag-object type and SHA, tag name, peeled
event commit, protected-`main` containment, and exact project-version match. Deterministic assets,
checksums, bundle transfer, draft-first creation, release-body and asset byte comparison, and
stable one-time publication are unchanged.

The publishing job no longer queries repository immutable-release settings before creating the
draft. Every credentialed GitHub command uses the exact checksummed GitHub CLI with the job-scoped
`github.token`; no separately managed release credential is required. Immutable releases must
still be enabled before creating the tag. Immediately after publication, the workflow requires
the release to report immutable and independently verifies the release and every asset.
Because the settings query is intentionally removed, maintainers must confirm immutable releases
are enabled before tagging; the workflow detects a disabled setting only after publication.

## 2026-07-30 — Fail-closed repository and release governance

Third-party GitHub Actions are content-addressed by full commit SHA and receive grouped,
review-only Dependabot proposals. Ordinary CI has explicit read-only contents permission; Pages
and release jobs receive only their required writes. Checkout credentials are not persisted, and
the release-artifact build disables shared dependency caching.

A release requires a GitHub-verified signed annotated tag and enabled repository release
immutability. The tag must equal `v` plus the authoritative project version. Before isolated
version parsing or repository code execution, the workflow binds the remote tag object to the
event commit and requires that commit to be contained in protected `main` history. It then builds
and checksums all assets, extracts a nonempty body from only that version's changelog section,
transfers the complete bundle to a separate publishing job, creates a draft stable release,
re-downloads and compares every draft asset and its body, and publishes only after exact
verification. Credentialed release commands use an exact checksummed GitHub CLI; the
pre-publication immutability query uses a dedicated administration-read Actions secret. A failed
run leaves an inspectable draft rather than an incompletely published release.

Private vulnerability reporting is the disclosure path. Public issue forms explicitly exclude
credentials, restricted data, sensitive user values, and protected health information. These
governance changes do not alter the app version, numerical authority, browser contract,
design-conditioned inverse-precision semantics, or explicit sample-size opt-in.

## 2026-07-30 — Core 0.4.1 replaces Core 0.4.0

The app pins the exact Core 0.4.1 release wheel by URL and SHA-256. This patch repairs
non-monotone threshold precision bracketing, exact pairwise support ratios, and strict ratio-scale
underflow validation in the numerical authority. The app continues to delegate all formulas and
solvers to Core.

## 2026-07-30 — Released Core 0.4.0 is the numerical authority

The app pins the exact Core 0.4.0 release wheel by URL and SHA-256. All effect conversions, CI
reconstruction, selected-claim semantics, forward metrics, per-target inversion, joint results,
binding ties, and sensitivity results come from Core. The app does not copy a solver/formula.

## 2026-07-30 — Focused inverse-precision response

The stable response has ten sections: metadata, current precision, assumptions, selection rule,
target effect, per-target results, joint result, optional sensitivity, optional sample-size
projection, and warnings. Observed compatibility, relative likelihood, S−2, and full Type S/M
curves are excluded.

## 2026-07-30 — Joint semantics remain explicit

Every mandatory target is solved independently. The strictest finite precision is the smallest
required SE/largest information multiplier. Binding targets use Core's relative multiplier
tolerance `1e-8`; multiple ties are retained. Current-sufficient requirements remain exactly
`1.0`. Any infeasible mandatory target makes the joint result infeasible without hiding rows.

## 2026-07-30 — Natural-display-linear sensitivity grid

Users enter natural/display-scale endpoints. The app creates an inclusive linear display-scale
grid and sends every converted working-scale value to Core. For ratios, this produces a
natural-ratio x-axis while calculations remain log-scale. The UI/export state that the range is a
sensitivity analysis, not a distribution.

## 2026-07-30 — Sample-size projection requires active opt-in

No sample-size value is accepted or displayed unless the user actively enables the exact
proportional-information assumption. The local ceiling arithmetic is an app-level projection,
not a design-specific solver. No clustering, attrition, allocation, event, censoring, or other
design claim is added.

## 2026-07-30 — Verified client-side runtime and privacy boundary

Python is staged from the locked environment into ignored generated output. The Web Worker
verifies file/package/bundle hashes before importing exact-version packages. There is no backend,
telemetry, persistence, cookie, input-bearing URL, upload, or application input log.

## 2026-07-30 — Creation-time template, not runtime framework

The scientific applet template supplied the initial shell and initializer provenance. This app
now evolves independently and has no shared runtime UI dependency.
