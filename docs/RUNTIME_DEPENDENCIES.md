# Runtime Dependencies and Provenance

Reviewed/retrieved 2026-07-30.

## Scientific numerical Core

- Distribution/import: `wald-inference` / `wald_inference`
- Version: `0.4.0`
- Repository: <https://github.com/reblocke/wald-inference-core>
- Release: <https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.0>
- Release tag/merge target: `fd7b24740122bed7ae07769674732c5e56c91277`
- Wheel:
  <https://github.com/reblocke/wald-inference-core/releases/download/v0.4.0/wald_inference-0.4.0-py3-none-any.whl>
- Wheel SHA-256:
  `401a0cc2a182918764149eb03c79672217b647147c494215c83515fd609c7af6`
- License: MIT
- Role: sole numerical authority for effect conversion, CI reconstruction, selected-claim
  semantics, forward Type S/M metrics, per-target precision inversion, joint solution, and
  sensitivity.

The URL and checksum are repeated in `pyproject.toml`, `uv.lock`, and `browser-stage.toml`.
Staging verifies installed direct-URL provenance plus every external package file against wheel
`RECORD` hashes.

## Browser runtime

- Pyodide 0.29.3 is loaded from its versioned jsDelivr path.
- Plotly.js 3.1.0 is loaded from Plotly's versioned CDN path.
- NumPy 2.2.6 and SciPy 1.14.1 are supplied by Pyodide for Core.
- Generated local Python files are listed and hashed by
  `web/assets/py/manifest.json`.

These static CDN requests do not include entered values. Availability still depends on reaching
the CDNs. No runtime package is fetched from a sibling repository.

## Development/runtime lock

`uv.lock` controls exact local/CI resolution. Developer tools include pytest, Hypothesis, Ruff,
Playwright, and pytest-playwright. GitHub Actions are pinned to major action versions in workflow
files and reviewed through normal dependency maintenance.

## Licenses

This repository and Core use MIT licenses. Pyodide, Plotly, NumPy, SciPy, Python, developer tools,
and GitHub Actions retain their respective licenses. No external data, figure, paper text, or
publisher artifact is bundled.
