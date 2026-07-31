# Validation

## Authority and migration baseline

Core 0.4.2 owns all numerical methods. The app regression fixture
`tests/fixtures/integrated_baseline/precision_b06_b07.json` contains only the B06/B07 core-owned
precision subset from:

- source repository: `reblocke/conf_curve_likelihood`;
- tag: `pre-split-baseline-2026-07-29`;
- behavior commit: `830756ecb11b4e8161f8dfe1fc75afc346ef4467`;
- baseline manifest SHA-256:
  `f54bb2d8311788c07adcf23fc9f038e35702449e4a77a474abea9411246cabcc`;
- fixture-set SHA-256:
  `81c341b39e711caffc85a444f0c1e4bc1e2d00633474c82e720afeb60def3c4d`.

Tolerances remain the frozen baseline tolerances: relative `1e-12` and absolute `1e-14`.

## Numerical and contract coverage

| Requirement | Evidence |
|---|---|
| B06 per-target values | `tests/regression/test_integrated_baseline.py` |
| B07 null/threshold infeasibility | regression and unit tests |
| Current sufficient multiplier exactly 1 | unit test with hexadecimal float identity |
| Stricter target requires at least as much information | scientific-reference test |
| Joint equals strictest finite target | unit and scientific-reference tests |
| Multiple binding ties | unit test |
| Infeasible mandatory target preserves other rows | unit test |
| Near-null undefined/infeasible | unit and regression tests |
| All six selected-claim rules | parametrized unit test |
| Solved metrics satisfy forward targets | direct Core forward-metric scientific-reference test |
| Information identity | property and scientific-reference tests |
| Approximate CI-width identity | scientific-reference test |
| Sensitivity order/gaps/expected monotonicity | unit test |
| Ratio conversion | unit test against the log transform |
| Direct-SE/CI equivalence | unit test |
| Core information-cap failure | unit test |
| Strict JSON | malformed constants, prohibited families, property test |
| Sample-size opt-in and ceiling | unit and browser tests |

The app does not claim an independent reimplementation oracle for the Core solver. Scientific
method validation and high-precision audits reside in the released Core repository; this
repository validates exact adoption, app semantics, frozen migration parity, and the browser
boundary.

## Browser, privacy, and accessibility

The staged package manifest records exact versions, URLs, artifact hashes, file hashes, package
hashes, bundle hash, Pyodide version, and source commit. Integration tests verify locked artifact
provenance, deterministic restaging, stale-file removal, and ignored generated output.

Chromium tests cover:

- Core 0.4.2 load and default joint result;
- textual per-target/joint results and plot;
- safe validation error without traceback/path leakage and successful recovery;
- linked field errors;
- scenario and sensitivity CSV schemas;
- figure and summary PNGs;
- reviewer/caption clipboard output;
- sensitivity feasibility gaps;
- active sample-size opt-in;
- mobile layout, keyboard order, reset state;
- unchanged URL, empty storage/cookies, and absence of entered values from requests.

WebKit runs the initial worker/calculation smoke. Both engines use Pyodide 0.29.3 and the exact
staged app/Core bytes.

## Interpretation checks

README, UI, CSV, reviewer text, caption, scientific scope, and `llms.txt` use the same terms:
assumed true effect, selected-claim probability, Type S, Type M, working-scale SE, relative
information, mandatory guardrail, binding target, no finite joint solution, and active
proportional-information assumption.

Plots always have textual/table equivalents. Infeasible points remain gaps. Ratio working-scale
notes, sensitivity-not-distribution wording, and sample-size limitations remain visible.

Engineering tests do not establish clinical validity, regulatory readiness, or suitability of
any entered guardrail/threshold.

## Release evidence

For each release record:

- exact reviewed merge commit and annotated tag target;
- exact equality between the version tag and authoritative project version;
- verification of the annotated remote tag object's identity and binding to the event commit;
- containment of the tag target in protected `main` history before repository code;
- locked Core wheel URL/SHA-256 and generated stage manifest hash;
- unit/property/scientific-reference/regression counts;
- Chromium and WebKit results;
- deterministic source/archive checksums;
- locally built and re-downloaded draft-body and asset comparison;
- nonempty release notes extracted only from the tagged version's changelog section;
- exact GitHub CLI archive version and checksum, with only the job-scoped GitHub token used for
  credentialed release commands;
- published stable-release immutability;
- hosted Pages smoke, input recovery, privacy/network, keyboard/focus, and export results;
- skipped checks and remaining limitations.

Repository-policy tests also verify full-SHA Action pins with version comments, checkout credential
isolation, least-privilege workflow permissions, release-cache disablement, protected-main and
annotated-tag gates, checksummed GitHub CLI installation, exact draft verification, stable
publication ordering, Dependabot coverage, and private-reporting guidance. These checks establish
engineering policy, not scientific, study-design, clinical, or regulatory validity.
