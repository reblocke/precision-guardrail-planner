from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_makefile_exposes_required_commands() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    for target in [
        "stage-web:",
        "fmt:",
        "fmt-check:",
        "lint:",
        "test:",
        "e2e:",
        "verify:",
        "serve:",
        "clean:",
    ]:
        assert target in makefile


def test_ci_and_pages_use_repository_targets() -> None:
    ci = (PROJECT_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    pages = (PROJECT_ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "make fmt-check" in ci
    assert "make lint" in ci
    assert "make test" in ci
    assert "make e2e" in ci
    assert "make e2e-webkit-smoke" in ci
    assert "make stage-web" in pages
    assert "web" in pages


def test_generated_stage_is_ignored_and_not_tracked() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "web/assets/py/" in gitignore
    assert (
        subprocess.run(
            ["git", "check-ignore", "web/assets/py/manifest.json"],
            cwd=PROJECT_ROOT,
            check=False,
        ).returncode
        == 0
    )
    assert (
        subprocess.run(
            ["git", "ls-files", "web/assets/py"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == ""
    )


def test_public_metadata_has_canonical_identity_and_no_author_prompts() -> None:
    public_files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CHANGELOG.md",
        PROJECT_ROOT / "CITATION.cff",
        PROJECT_ROOT / "llms.txt",
        *sorted((PROJECT_ROOT / "docs").glob("*.md")),
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in public_files)

    assert "AUTHOR ACTION REQUIRED" not in text
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert "family-names: Locke" in citation
    assert "given-names: Brian" in citation
    assert "Copyright (c) 2026 Brian Locke" in (PROJECT_ROOT / "LICENSE").read_text(
        encoding="utf-8"
    )


def test_readme_related_tools_has_catalog_core_marker() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    related = readme.split("## Related Wald tools", maxsplit=1)[1].split(
        "\n## ",
        maxsplit=1,
    )[0]

    assert "wald-inference Core v0.4.1" in related
    assert "https://github.com/reblocke/wald-inference-core/releases/tag/v0.4.1" in related


def test_readme_records_current_release_and_software_citation() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    citation = (PROJECT_ROOT / "CITATION.cff").read_text(encoding="utf-8")
    project = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    version = project["version"]

    assert f"Current app version: `{version}`." in readme
    assert (
        f"https://github.com/reblocke/precision-guardrail-planner/releases/tag/v{version}"
    ) in readme
    assert "Release maturity: experimental software." in readme
    assert "GitHub publication state is recorded on the versioned release page:" in readme
    assert "Cite the exact tagged software release or commit used" in readme
    assert "[CITATION.cff](CITATION.cff)" in readme
    assert f"version: {version}" in citation
