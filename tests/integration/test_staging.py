from __future__ import annotations

import hashlib
import importlib.metadata
import json
import subprocess
import tomllib
from pathlib import Path

import pytest
from scripts.stage_browser_packages import StagingError, stage_browser_packages

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _descriptor(files: list[dict[str, object]]) -> str:
    return "".join(
        f"{record['path']}\0{record['sha256']}\0{record['bytes']}\n"
        for record in sorted(files, key=lambda item: str(item["path"]))
    )


def test_stage_manifest_records_versions_files_and_hashes(tmp_path: Path) -> None:
    target = tmp_path / "py"
    manifest = stage_browser_packages(target, project_root=PROJECT_ROOT)

    assert json.loads((target / "manifest.json").read_text(encoding="utf-8")) == manifest
    assert manifest["schema_version"] == 1
    assert manifest["pyodide_version"] == "0.29.3"
    assert manifest["pyodide_packages"] == ["numpy", "scipy"]
    assert (
        manifest["source_commit"]
        == subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    app, core = manifest["packages"]
    assert app["role"] == "app"
    assert app["distribution"] == "precision-guardrail-planner"
    assert app["import_name"] == "precision_guardrail"
    assert app["version"] == "0.1.4"
    assert app["artifact_url"] is None
    assert app["artifact_sha256"] is None
    assert app["files"]
    assert core["role"] == "core"
    assert core["distribution"] == "wald-inference"
    assert core["import_name"] == "wald_inference"
    assert core["version"] == "0.4.2"
    assert core["artifact_url"].endswith("/v0.4.2/wald_inference-0.4.2-py3-none-any.whl")
    assert (
        core["artifact_sha256"]
        == "225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349"
    )

    all_files = app["files"] + core["files"]
    for record in all_files:
        contents = (target / record["path"]).read_bytes()
        assert len(contents) == record["bytes"]
        assert hashlib.sha256(contents).hexdigest() == record["sha256"]
    for package in (app, core):
        assert (
            hashlib.sha256(_descriptor(package["files"]).encode()).hexdigest()
            == package["package_sha256"]
        )
    descriptor = _descriptor(all_files)
    assert hashlib.sha256(descriptor.encode()).hexdigest() == manifest["bundle_sha256"]


def test_stage_is_deterministic_and_removes_stale_files(tmp_path: Path) -> None:
    target = tmp_path / "py"
    target.mkdir()
    (target / "stale.py").write_text("stale = True\n", encoding="utf-8")

    first = stage_browser_packages(target, project_root=PROJECT_ROOT)
    first_bytes = (target / "manifest.json").read_bytes()
    second = stage_browser_packages(target, project_root=PROJECT_ROOT)

    assert not (target / "stale.py").exists()
    assert second == first
    assert (target / "manifest.json").read_bytes() == first_bytes


def test_stage_fails_on_configured_version_mismatch(tmp_path: Path) -> None:
    config = tmp_path / "browser-stage.toml"
    source = (PROJECT_ROOT / "browser-stage.toml").read_text(encoding="utf-8")
    config.write_text(source.replace('version = "0.1.4"', 'version = "9.9.9"'), encoding="utf-8")

    with pytest.raises(StagingError, match="expected '9.9.9'"):
        stage_browser_packages(
            tmp_path / "py",
            project_root=PROJECT_ROOT,
            config_path=config,
        )


def test_locked_core_distribution_is_the_configured_release_artifact() -> None:
    distribution = importlib.metadata.distribution("wald-inference")
    direct_url = json.loads(distribution.read_text("direct_url.json") or "{}")
    lock = tomllib.loads((PROJECT_ROOT / "uv.lock").read_text(encoding="utf-8"))
    [package] = [package for package in lock["package"] if package["name"] == "wald-inference"]

    assert distribution.version == "0.4.2"
    assert direct_url["url"].endswith("/v0.4.2/wald_inference-0.4.2-py3-none-any.whl")
    assert package["wheels"] == [
        {
            "url": direct_url["url"],
            "hash": ("sha256:225331d7b9d7b70e2508eecb92851a92a8c4e245baf412a1eb0f464d85da1349"),
        }
    ]
