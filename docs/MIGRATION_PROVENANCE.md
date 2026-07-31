# Migration Provenance

## Portfolio source

This focused app was split from the design/precision functionality of
`reblocke/conf_curve_likelihood` under migration ticket CC-MIG-08.

- Frozen source tag: `pre-split-baseline-2026-07-29`
- Frozen behavior commit: `830756ecb11b4e8161f8dfe1fc75afc346ef4467`
- Baseline manifest SHA-256:
  `f54bb2d8311788c07adcf23fc9f038e35702449e4a77a474abea9411246cabcc`
- Fixture-set SHA-256:
  `81c341b39e711caffc85a444f0c1e4bc1e2d00633474c82e720afeb60def3c4d`

The selected B06/B07 core-owned values are copied with those identifiers in
`tests/fixtures/integrated_baseline/precision_b06_b07.json`. No patient data or external
scientific artifact is included.

## Numerical extraction

Numerical formulas were not copied into this repository. They were extracted, validated, and
released separately in `reblocke/wald-inference-core`. This app consumes Core 0.4.2's
`joint_precision_result` and `precision_sensitivity` APIs plus released forward/reconstruction
primitives. The exact wheel URL, checksum, tag target, and license are documented in
`RUNTIME_DEPENDENCIES.md`.

## App scaffold

The initial browser/worker shell was initialized from
`reblocke/scientific-applet-template` using the recorded identity in
`.applet-template-initialized.json`. Template-only demonstration code, tests, wording, and
maintainer files were removed or replaced. The app has no runtime dependency on the template.

## Scope separation

The focused app retains inverse precision targets, joint/binding semantics, sensitivity, and
explicitly opted-in proportional-information projection. It excludes observed compatibility,
relative likelihood, S−2, and full Type S/M panels. Those focused questions remain in other
portfolio tools or the backward-compatible integrated workbench.
